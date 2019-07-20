# encoding: utf-8
'''
Websocket ラッパークラス

MIT License

Copyright (c) 2019 amenoyoya https://github.com/amenoyoya/pylib.git

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import logging
from websocket_server import WebsocketServer as create_server
from websocket import create_connection, enableTrace, WebSocketApp

def create_logger():
    ''' ロガー作成 '''
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(' %(module)s -  %(asctime)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


class WebsocketServer:
    ''' Websocket Server ラッパークラス '''
    def __init__(self, port=3000, host='localhost'):
        self.server = create_server(port=port, host=host, loglevel=logging.INFO)
        self.server.set_fn_new_client(
            lambda client, server: self.on_client_connected(client)
        )
        self.server.set_fn_client_left(
            lambda client, server: self.on_client_disconnected(client)
        )
        self.server.set_fn_message_received(
            lambda client, server, message: self.on_message_recieved(client, message)
        )
        self.logger = create_logger()
    
    def log(self, msg, *args, **kargs):
        ''' ログメッセージを出力 '''
        self.logger.info(msg, *args, **kargs)

    def send_message(self, client, message):
        ''' clientにmessage送信 '''
        return self.server.send_message(client, message)

    def run_forever(self):
        ''' サーバー実行 '''
        return self.server.run_forever()

    # --- event methods --- #
    def on_client_connected(self, client):
        ''' 新規クライアントが接続したときのコールバック '''
        self.log('New client {}:{} has been connected.'.format(client['address'][0], client['address'][1]))
    
    def on_client_disconnected(self, client):
        ''' クライアントとの接続が終了したときのコールバック '''
        self.log('Client {}:{} has been disconnected.'.format(client['address'][0], client['address'][1]))
    
    def on_message_recieved(self, client, message):
        ''' クライアントからメッセージを受信したときのコールバック '''
        self.log('Message "{}" has been received from {}:{}'.format(message, client['address'][0], client['address'][1]))


class WebsocketClient:
    ''' Websocket Client ラッパークラス '''
    def __init__(self):
        self.client = None
        self.logger = create_logger()

    def open(self, server_host):
        ''' server_hostにクライアントを新規接続 '''
        self.close()
        self.client = create_connection(server_host)
    
    def open_server(self, server_host):
        ''' server_hostにクライアントを新規接続し、サーバーとして動作させる '''
        self.close()
        enableTrace(False)
        self.client = WebSocketApp(
            server_host,
            on_message = lambda ws, message: self.on_message_recieved(message),
            on_error = lambda ws, error: self.on_error(error),
            on_close = lambda ws: self.on_disconnect()
        )
        self.client.on_open = lambda ws: self.on_connect()
        self.client.run_forever()
    
    def close(self):
        ''' clientをサーバーから切断する '''
        if self.client is not None:
            self.client.close()
            self.client = None

    def log(self, msg, *args, **kargs):
        ''' ログメッセージを出力 '''
        self.logger.info(msg, *args, **kargs)

    def send_message(self, message):
        ''' 接続先のサーバーにmessage送信 '''
        return self.client.send(message)
    
    def recieve_message(self):
        ''' 接続先サーバーから送られてきたメッセージを受信 '''
        return self.client.recv()

    # --- event methods (サーバーモードで動作する際に使用) --- #
    def on_connect(self):
        ''' Websocketサーバー接続時のコールバック '''
        self.log('Connect')

    def on_disconnect(self):
        ''' Websocketサーバーから切断時のコールバック '''
        self.log('Disconnect')

    def on_message_recieved(self, message):
        ''' Websocketサーバーからメッセージ受信時のコールバック '''
        self.log('Received:{}'.format(message))

    def on_error(self, error):
        ''' エラー発生時のコールバック '''
        self.log('Error:{}'.format(error))
    