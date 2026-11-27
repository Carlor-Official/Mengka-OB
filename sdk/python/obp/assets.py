"""Native file-reference publishing; no patches to framework files or old web routes."""
import hashlib,io,os,tempfile,logging,re,stat,threading,time
from pathlib import Path
from PIL import Image
from . import state
from .runtime import peer

IMAGE_RETENTION_SECONDS = 24 * 60 * 60
ASSET_SWEEP_SECONDS = 5 * 60
_image_name = re.compile(r'^[0-9a-f]{64}\.(?:jpg|jpeg|png|gif|webp|bmp|avif)$')
_asset_lock = threading.RLock()
_log = logging.getLogger(__name__)

def cleanup_generated_images(data_root=None, *, now=None):
    """Expire only SDK-owned generated images, never state, uploads or symlinks."""
    base = Path(data_root) if data_root is not None else state.root()
    root = base / 'assets'
    if root.is_symlink() or not root.is_dir():
        return {'removed': 0, 'bytes': 0}
    cutoff = (time.time() if now is None else now) - IMAGE_RETENTION_SECONDS
    result = {'removed': 0, 'bytes': 0}
    with os.scandir(root) as entries:
        for entry in entries:
            if not _image_name.fullmatch(entry.name):
                continue
            # Re-stat under the same lock as publish/refresh: a reused image
            # must not be removed based on an older directory-entry snapshot.
            with _asset_lock:
                try:
                    path = root / entry.name
                    info = path.lstat()
                    if not stat.S_ISREG(info.st_mode) or info.st_mtime > cutoff:
                        continue
                    path.unlink()
                    result['removed'] += 1
                    result['bytes'] += info.st_size
                except FileNotFoundError:
                    continue
                except OSError:
                    _log.warning('Generated image cleanup could not remove a file')
    return result

class _AssetMaintenance:
    def __init__(self):
        self.root = state.root()
        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self._run, name='obp-image-retention', daemon=True)
        self.thread.start()

    def _run(self):
        while not self.stopped.is_set():
            try:
                result = cleanup_generated_images(self.root)
                if result['removed']:
                    _log.info('Expired generated images removed=%d bytes=%d', result['removed'], result['bytes'])
            except Exception:
                _log.exception('Generated image retention sweep failed')
            self.stopped.wait(ASSET_SWEEP_SECONDS)

    def close(self):
        self.stopped.set()
        self.thread.join(timeout=2)

def start_asset_maintenance():
    """Start one service-local sweeper, including when no new images are made."""
    return _AssetMaintenance()

def save_asset(data,extension='jpg'):
    data=bytes(data)
    if not data or len(data)>8*1024*1024:raise ValueError('image must be between 1 byte and 8 MiB')
    root=state.root()/'assets'
    if root.is_symlink():raise ValueError('asset directory must not be a symlink')
    root.mkdir(parents=True,exist_ok=True)
    name=hashlib.sha256(data).hexdigest()+'.'+extension
    dest=root/name
    # The framework reads this path concurrently with plugin rendering. Only
    # expose a completed file; another publisher must never reuse a partial one.
    with _asset_lock:
        if dest.is_file() and not dest.is_symlink() and dest.read_bytes()==data:
            os.utime(dest,None)
            return 'assets/'+name
    fd,temporary=tempfile.mkstemp(prefix='.'+name+'.',suffix='.tmp',dir=root)
    os.close(fd)
    staging=Path(temporary)
    try:
        staging.write_bytes(data)
        with _asset_lock:
            os.replace(staging,dest)
            os.utime(dest,None)
    finally:
        staging.unlink(missing_ok=True)
    return 'assets/'+name

def publish_rendered_jpeg(data,*args,**kwargs):
    with Image.open(io.BytesIO(data)) as img:
        if img.format!='JPEG' or img.width*img.height>40_000_000:raise ValueError('invalid JPEG')
        img.verify()
    path=save_asset(data)
    result=peer().call_sync('publish_asset',{'app_id':state.active_app.get(),'path':path})
    return result['url']

def install_web_integration():
    return {'installed':True,'transport':'obp/1','asset_provider':'publish_asset'}

def fit_markdown_size(width,height,max_width=320,max_height=500,**kwargs):
    width=max(1,int(width));height=max(1,int(height));scale=min(1,max_width/width,max_height/height)
    return max(1,int(width*scale+.5)),max(1,int(height*scale+.5))
