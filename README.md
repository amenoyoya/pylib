# pylib

## What's this?
自作Pythonライブラリ集

***

## Libraries

### Frasco
- `web/frasco.py`
    - Flaskの簡易ラッパー

#### Environment
- Python: `3.6.7`
    - Flask: `1.0.2`
        ```bash
        $ pip install flask
        ```

---

### Websock
- `web/websock.py`
    - Websocketサーバー／クライアントの簡易ラッパー

#### Environment
- Python: `3.6.7`
    - websocket-server: `0.4`
        ```bash
        $ pip install websocket-server
        
        # latest version update
        $ pip install --upgrade git+https://github.com/Pithikos/python-websocket-server
        ```
    - websocket-server: `0.56.0`
        ```bash
        $ pip install websocket-client
        ```

---

### SqlDB
- `sqldb/`
    - Python標準のSQLite3を使いやすくしたもの
    - JSONデータを用いてSQLite3を操作可能

#### Environment
- Python: `3.6.7`
