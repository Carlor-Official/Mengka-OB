"""Exercise the actual ZIP in a child process; no QQ/network access."""
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class IPCSmokeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mengka-ob-sdk-test-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.package = self.folder / "package"
        with zipfile.ZipFile(ROOT.parent / "releases/mengka-ob-python-sdk.zip") as archive:
            archive.extractall(self.package)
        self.start()

    def start(self):
        env = dict(os.environ, OB_PLUGIN_PROTOCOL="obp/1", OB_PLUGIN_TRANSPORT="ipc",
                   OB_PLUGIN_TOKEN="local-test-token", OB_PLUGIN_DATA_DIR=str(self.folder / "data"),
                   PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        self.proc = subprocess.Popen([sys.executable, "main.py"], cwd=self.package, env=env,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True, encoding="utf-8")
        self.addCleanup(self.stop)
        self.frames = queue.Queue()
        self.errors = []
        proc, frames, errors = self.proc, self.frames, self.errors

        def read():
            for line in proc.stdout:
                try:
                    frames.put(json.loads(line))
                except Exception as error:
                    frames.put({"invalid_frame": str(error)})

        def logs():
            errors.extend(proc.stderr)

        self.reader = threading.Thread(target=read, daemon=True)
        self.logger = threading.Thread(target=logs, daemon=True)
        self.reader.start()
        self.logger.start()
        hello = self.receive()
        self.assertEqual(hello["type"], "hello")
        self.assertEqual(hello["protocol"], "obp/1")
        self.send({"type": "hello.ok", "data": {"app_ids": ["123456"], "config": {}}})
        self.assertEqual(self.receive(), {"type": "runtime.status", "event": "ready"})

    def stop(self):
        proc = getattr(self, "proc", None)
        if proc is None:
            return
        if proc.poll() is None:
            proc.stdin.close()
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        self.reader.join(timeout=2)
        self.logger.join(timeout=2)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            stream.close()
        self.proc = None

    def send(self, frame):
        self.proc.stdin.write(json.dumps(frame) + "\n")
        self.proc.stdin.flush()

    def receive(self):
        try:
            return self.frames.get(timeout=8)
        except queue.Empty:
            self.fail("IPC output timed out: " + "".join(self.errors))

    def event(self, delivery, group=False):
        event = "GROUP_AT_MESSAGE_CREATE" if group else "C2C_MESSAGE_CREATE"
        body = {"id": "message-" + delivery, "content": "ping", "author": {"user_openid": "user-1"}}
        if group:
            body.update(group_openid="group-1", author={"member_openid": "member-1"})
        return {"type": "event", "id": delivery, "app_id": "123456", "event": event,
                "data": {"op": 0, "t": event, "d": body}}

    def test_reply_ping_and_persisted_duplicate_receipt(self):
        self.send({"type": "ping", "id": "heartbeat"})
        self.assertEqual(self.receive(), {"type": "pong", "id": "heartbeat"})
        for delivery, group in (("event-1", False), ("event-2", True)):
            event = self.event(delivery, group)
            self.send(event)
            action = self.receive()
            self.assertEqual(action["action"], "send_message")
            params = action["params"]
            self.assertEqual(params["app_id"], "123456")
            self.assertEqual(params["scope"], "group" if group else "c2c")
            self.assertEqual(params["target"], "group-1" if group else "user-1")
            self.assertEqual(params["payload"], {"content": "pong", "msg_type": 0,
                                               "msg_id": "message-" + delivery, "msg_seq": 1})
            self.send({"type": "action.result", "id": action["id"], "success": True, "data": {"id": "accepted"}})
            ack = {"type": "event.ack", "id": delivery, "consumed": True}
            self.assertEqual(self.receive(), ack)
            self.send(event)
            self.assertEqual(self.receive(), ack)
        self.stop()
        self.start()
        self.send(self.event("event-1"))
        self.assertEqual(self.receive(), {"type": "event.ack", "id": "event-1", "consumed": True})
        self.send({"type": "ping", "id": "after-restart"})
        self.assertEqual(self.receive(), {"type": "pong", "id": "after-restart"})

    def test_rejection_is_not_acknowledged_as_success_or_automatically_retried(self):
        self.send(self.event("rejected"))
        action = self.receive()
        self.send({"type": "action.result", "id": action["id"], "success": False,
                   "error": "QQ API 业务码 40054004", "official_response": {"http_status": 400,
                   "body": {"code": 40054004, "message": "test rejection"}}})
        self.send({"type": "ping", "id": "after-rejection"})
        self.assertEqual(self.receive(), {"type": "pong", "id": "after-rejection"})
        with self.assertRaises(queue.Empty):
            self.frames.get(timeout=0.5)


if __name__ == "__main__":
    unittest.main()
