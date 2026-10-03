proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto https;
proxy_set_header Sec-WebSocket-Protocol $http_sec_websocket_protocol;
proxy_buffering off;
proxy_request_buffering off;
gzip off;
# long timeouts: mobile operators (MCI/Irancell/Rightel) often hold idle sockets
proxy_connect_timeout 60s;
proxy_read_timeout 1h;
proxy_send_timeout 1h;
proxy_socket_keepalive on;
