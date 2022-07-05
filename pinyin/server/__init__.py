# -*- coding=utf8 -*-

'''
服务器 API 接口
'''

import sys
sys.path.append('../')
from flask import Flask, request, Response
from pinyin.ime import ime
import json

app = Flask(__name__)


@app.after_request
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Method'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp


@app.route("/", methods=['GET'])
def ime_api():
    '''
    输入法接口
    '''
    try:
        pinyin = request.args.get('pinyin')
        if not pinyin:
            return Response(json.dumps({'status': 'failure', 'error': 'pinyin is empty'}), mimetype='application/json')
        limit = request.args.get('limit', default=7, type=int)
        tuples = ime(pinyin, limit)
        result = {'status': 'success', 'raw_pinyin': pinyin, 'limit': limit}
        # [(('jin', 'tian'), '今天', -8.551883029536198), (('jin', 'tian'), '金田', -15.458916572771084), ...]
        result['result'] = [{
            'pinyin': '\''.join(t[0]),
            'word': t[1],
            'prob': t[2]
        } for t in tuples]
        return Response(json.dumps(result, indent=4, ensure_ascii=False), mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({'status': 'failure', 'error': str(e)}), mimetype='application/json')


def main():
    print("Url like http://localhost:3366/?pinyin=a&limit=7")
    app.run(debug=False, port=3366, host='0.0.0.0')

if __name__ == '__main__':
    main()