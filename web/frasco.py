# encoding: utf-8
'''
Flask Webserver Wrapper Library

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
import flask, os
from flask import Flask, render_template, jsonify, session, request, g
from flask_cors import CORS
from functools import wraps

class Response:
    ''' Response class '''
    @staticmethod
    def text(string, status=200):
        ''' render string '''
        return string, status

    @staticmethod
    def html(filename, status=200):
        ''' render html file '''
        with open(filename, 'rb') as f:
            return f.read(), status
    
    @staticmethod
    def template(filename, kwargs={}, status=200):
        ''' render template html file '''
        # template file should be in 'templates/'
        return render_template(filename, **kwargs), status

    @staticmethod
    def json(data, status=200):
        ''' response of json '''
        res = jsonify(data)
        res.status_code = status
        return res
    
    @staticmethod
    def redirect(url, status=302):
        ''' redirect to url '''
        return flask.redirect(url, status)


class AuthUser:
    ''' Basic User class for authentication
    required static methods:
        auth: authonicate from post data
        save: user info to string (session_id)
        load: string (session_id) to user info
    '''
    def __init__(self, username):
        self.name = username

    @staticmethod
    def auth(data):
        ''' static method: authonicate from post data
        params:
            data (dict): post data
        return:
            user (AuthUser): Authenicated user or None
        '''
        if data.get('username') == 'admin':
            # 単純に username が 'admin' かどうかで認証
            return AuthUser('admin')

    @staticmethod
    def save(user):
        ''' static method: user info to string (session_id)
        params:
            user (AuthUser): Authenicated user
        return:
            session_id (str)
        '''
        return user.name
    
    @staticmethod
    def load(session_id):
        ''' static method: string (session_id) to user info
        params:
            session_id (str)
        return:
            user (AuthUser): Authenicated user or None
        '''
        return AuthUser(session_id)


class Frasco(Flask):
    ''' Flask wrapper class '''
    def __init__(self, import_name, User=AuthUser, *args, **kwargs):
        super(Frasco, self).__init__(import_name, *args, **kwargs)
        self.config.from_object(import_name)
        # jsonifyでの日本語の文字化けを防ぐ
        self.config['JSON_AS_ASCII'] = False
        # cookieを暗号化する秘密鍵
        self.config['SECRET_KEY'] = os.urandom(24)
        # 認証処理用ユーザークラス
        self.AuthUser = User
        # Cross Origin Resource Sharing 有効化
        CORS(self)

    def get(self, route):
        ''' get method routing decorator '''
        return self.route(route, methods=['GET'])

    def post(self, route):
        ''' post method routing decorator '''
        return self.route(route, methods=['POST'])
    
    def put(self, route):
        ''' put method routing decorator '''
        return self.route(route, methods=['PUT'])
    
    def delete(self, route):
        ''' delete method routing decorator '''
        return self.route(route, methods=['DELETE'])

    def secret(self, err_response):
        ''' decorator for authentication
        params:
            err_response (tuple): response for the case of unauthorized
        example:
            @frasco.post('/member')
            @frasco.secret(Response.redirect('/login'))
            def member_page():
                return Response.text('Here is a secret page')
        '''
        def _wrapper(func):
            @wraps(func) # デコレートした関数名が`wrapper`になるのを防ぐ: ルーティングを複数定義したときルートが上書きされるのを防ぐ
            def wrapper(*args, **kargs):
                # セッション`auth`に保存されたIDからユーザー情報を取得
                session_id = session.get('auth')
                if session_id is None:
                    return err_response
                # current_user に現在ログイン中のユーザー情報を保存
                self.current_user = self.AuthUser.load(session_id)
                if self.current_user is None:
                    return err_response
                return func(*args, **kargs)
            return wrapper
        return _wrapper

    def auth(self, login_route, logout_route, logout_response):
        ''' decorator for login/logout process
        params:
            login_route (str): login route
            logout_route (str): logout route
            logout_response (tuple): response after logout
        example:
            @frasco.auth('/api/login', '/api/logout', Response.redirect('/'))
            def login(user):
                if user:
                    # succeeded to login
                    return Responce.json({'username': user.name})
                # failed to login
                return Response.text('Failed to login', 400)
        '''
        def _wrapper(func):
            @wraps(func) # デコレートした関数名が`wrapper`になるのを防ぐ: ルーティングを複数定義したときルートが上書きされるのを防ぐ
            def wrapper():
                # POSTデータから認証処理実行
                user = self.AuthUser.auth(request.form)
                if user is not None:
                    # セッションID保存
                    session['auth'] = self.AuthUser.save(user)
                return func(user)
            return self.post(login_route)(wrapper)
        
        @self.get(logout_route)
        def logout():
            session.pop('auth', None) # セッション削除
            return logout_response
        
        return _wrapper
