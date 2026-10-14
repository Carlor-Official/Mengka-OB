// Build with: go build -o echo.exe main.go (Windows), or go build -o echo main.go.
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

type Frame struct {
	Type    string          `json:"type"`
	ID      string          `json:"id"`
	AppID   string          `json:"app_id"`
	Event   string          `json:"event"`
	Data    json.RawMessage `json:"data"`
	Success bool            `json:"success"`
	Error   string          `json:"error"`
}

func main() {
	if os.Getenv("OB_PLUGIN_PROTOCOL") != "obp/1" || os.Getenv("OB_PLUGIN_TRANSPORT") != "ipc" || os.Getenv("OB_PLUGIN_TOKEN") == "" {
		fmt.Fprintln(os.Stderr, "Start this plugin through a Mengka OB IPC service.")
		os.Exit(1)
	}
	out := json.NewEncoder(os.Stdout)
	send := func(v any) {
		if e := out.Encode(v); e != nil {
			os.Exit(1)
		}
	}
	send(map[string]any{"type": "hello", "protocol": "obp/1", "token": os.Getenv("OB_PLUGIN_TOKEN")})
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 4<<20)
	pending := map[string]string{}
	ack := func(id string) { send(map[string]string{"type": "event.ack", "id": id}) }
	for scanner.Scan() {
		var f Frame
		if json.Unmarshal(scanner.Bytes(), &f) != nil {
			fmt.Fprintln(os.Stderr, "Invalid protocol frame")
			continue
		}
		switch f.Type {
		case "hello.ok":
			fmt.Fprintln(os.Stderr, "IPC plugin connected")
		case "ping":
			send(map[string]string{"type": "pong", "id": f.ID})
		case "action.result":
			if event, ok := pending[f.ID]; ok {
				if !f.Success {
					fmt.Fprintln(os.Stderr, "Reply failed:", f.Error)
				}
				ack(event)
				delete(pending, f.ID)
			}
		case "event":
			var env struct {
				D struct {
					ID      string `json:"id"`
					Content string `json:"content"`
					Group   string `json:"group_openid"`
					Author  struct {
						OpenID string `json:"user_openid"`
					} `json:"author"`
				} `json:"d"`
			}
			if json.Unmarshal(f.Data, &env) != nil {
				ack(f.ID)
				continue
			}
			content := strings.TrimSpace(env.D.Content)
			if strings.HasPrefix(content, "<@") {
				if i := strings.Index(content, ">"); i >= 0 {
					content = strings.TrimSpace(content[i+1:])
				}
			}
			scope, target := "", ""
			switch f.Event {
			case "GROUP_AT_MESSAGE_CREATE":
				scope, target = "group", env.D.Group
			case "C2C_MESSAGE_CREATE":
				scope, target = "c2c", env.D.Author.OpenID
			}
			if content != "/ob ping" || scope == "" || target == "" {
				ack(f.ID)
				continue
			}
			id := "reply:" + f.ID
			pending[id] = f.ID
			send(map[string]any{"type": "action", "id": id, "action": "send_message", "params": map[string]any{"app_id": f.AppID, "scope": scope, "target": target, "payload": map[string]any{"content": "萌卡OB IPC 插件已连接", "msg_type": 0, "msg_seq": 1, "msg_id": env.D.ID}}})
		}
	}
	if e := scanner.Err(); e != nil {
		fmt.Fprintln(os.Stderr, "IPC input error:", e)
	}
}
