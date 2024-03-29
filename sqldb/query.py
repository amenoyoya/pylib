# encoding: utf-8
'''
SQL QueryBuilder by RPN Library

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
from .rpn import RPN, Value, Variable

class QueryBuilder(RPN):
    ''' SQLクエリ構築クラス '''
    
    @staticmethod
    def _operator(x, y, op, binds):
        ''' クエリ構築基本式
        [column, value, operator]
        => exp: '(column operator ?)', binds: [value]
        '''
        exp = '('
        if x.type == Value.VALUE:
            binds += [x.value]
            exp += '?'
        else:
            exp += x.value
        exp += ' ' + op + ' '
        if y.type == Value.VALUE:
            binds += [y.value]
            exp += '?'
        else:
            exp += y.value
        exp += ')'
        return Value(exp, Value.CHUNK)
    
    @staticmethod
    def build_insert_query(table_name, values):
        ''' values配列からinsertクエリ構築
        params:
            table_name: 対象テーブル名,
            values(list): [
                [column1_name, column2_name, ...],
                [column1_value1, column2_value1, ...],
                ...
            ]
        return:
            query(str): insertクエリ,
            binds(list): バインディングされた値(list)
        '''
        return 'insert into ' + Variable(table_name).value + ' (' + \
            ','.join([Variable(column).value for column in values[0]]) + ') values (' + \
            ','.join(['?' for i in range(len(values[0]))]) + ')', values[1:]

    @staticmethod
    def build_update_query(table_name, values):
        ''' values配列からupdateクエリ構築
        params:
            table_name: 対象テーブル名,
            values(dict): {column_name: column_value}
        return:
            query(str): updateクエリ,
            binds(list): バインディングされた値(list)
        '''
        queries, binds = [], []
        for column, value in values.items():
            queries += [Variable(column).value + ' = ?']
            binds += [value]
        return 'update ' + Variable(table_name).value + ' set ' + ','.join(queries), binds

    @staticmethod
    def build_select_query(selects):
        ''' selectターゲットの配列からselectクエリ構築
        params:
            selects(list): selectターゲットの配列
        return:
            query(str): selectクエリ
        '''
        if type(selects) is not list:
            return 'select *'
        return 'select ' + ','.join(['*' if s == '*' else Variable(s).value for s in selects])

    @staticmethod
    def build_order_query(columns):
        ''' カラム配列からorderクエリ構築
        params:
            columns(dict): カラム配列 {'カラム名': 'desc' or 'asc'}
        return:
            query(str): orderクエリ
        '''
        if type(columns) is not dict:
            return ''
        order_type = {'desc': 'desc', 'asc': 'asc'}
        return 'order by ' + ','.join([Variable(k).value + ' ' + order_type[v] for k, v in columns.items()])

    @classmethod
    def build_where_query(self, s_exp):
        ''' ポーランド記法のクエリ式からwhereクエリ構築
        params:
            s_exp(dict): ポーランド記法のクエリ {
                '演算子': {'カラム': 値},
                '演算子': [式, ...],
            }
        return:
            query(str): whereクエリ,
            binds(list): バインディングされた値(list)
        '''
        # binding values
        binds = []

        # SQLクエリ演算子定義
        self.operators = {
            '<': lambda x, y: QueryBuilder._operator(x, y, '<', binds), '<=': lambda x, y: QueryBuilder._operator(x, y, '<=', binds),
            '>': lambda x, y: QueryBuilder._operator(x, y, '>', binds), '>=': lambda x, y: QueryBuilder._operator(x, y, '>=', binds),
            '=': lambda x, y: QueryBuilder._operator(x, y, '=', binds), '!=': lambda x, y: QueryBuilder._operator(x, y, '!=', binds),
            'and': lambda x, y: QueryBuilder._operator(x, y, 'and', binds), 'or': lambda x, y: QueryBuilder._operator(x, y, 'or', binds),
            'like': lambda x, y: QueryBuilder._operator(x, y, 'like', binds)
        }
        
        # クエリ構築
        if type(s_exp) is not dict:
            return '', binds
        exp = self.build(s_exp)
        return 'where ' + self.eval(exp)[0].value, binds
