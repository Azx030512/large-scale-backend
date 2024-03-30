from flask import Flask, jsonify
from flask import make_response
from flask import request
from flask import abort
from database_connect import *
import json

import logging
logger = logging.getLogger("console_logger")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
api = Flask('account_api')


@api.route('/api/account_api/register', methods=['POST', 'get'])
def register():
    # request.json里面包含请求数据，如果不是JSON或者里面没有包含title字段

    try:
        session = Session()


        new_account_json = request.json
        new_account = Account(
            new_account_json['user_name'], new_account_json['password'], new_account_json['email'],  new_account_json['md5'],  new_account_json['phone'])
        session.add(new_account)
        session.commit()

        return jsonify({'message': "New account has been created successfully!",
                        'signal': "success"
                        }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "New account creation failed!",
                        'signal': "fail"}), 200


@api.route('/api/account_api/login', methods=['POST', 'get', 'OPTIONS'])
def login():
    try:
        session = Session()
        request_json = json.loads(request.data.decode())
        # results = session.query(Account).filter_by(
        #     user_name=request_json['user_name'], password=request_json['password']).all()  # 查找表的所有数据
        results = session.query(Account).filter_by(
            user_name=request_json['user_name'], md5=request_json['md5']).all()  # 查找表的所有数据
        print("login query result: " + str(results))

        session.close()
        if len(results) == 1:
            print(results[0].show_info(), ' login success')
            return jsonify({'message': "Login successfully, welcome back my friend!",
                            'signal': "success"
                            }), 200
        else:
            return jsonify({'message': "Wrong user name or password",
                            'signal': "fail"
                            }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "There is something wrong leading to failure!",
                        'signal': "fail"}), 200


@api.route('/api/account_api/showinfo', methods=['POST', 'get', 'OPTIONS'])
def show_info():
    try:
        session = Session()
        request_json = json.loads(request.data.decode())

        results = session.query(Account).filter_by(
            user_name=request_json['user_name']).all()  # 查找表的所有数据
        print("login query result: " + str(results))

        session.close()
        if len(results) == 1:
            user = results[0].show_info()
            print(results[0].show_info(), ' login success')
            return jsonify({'message': "Login successfully, welcome back my friend!",
                            'signal': "success",
                            'user': user
                            }), 200
        else:
            return jsonify({'message': "Wrong user name or password",
                            'signal': "fail",
                            'user': {}
                            }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "There is something wrong leading to failure!",
                        'signal': "fail"}), 200


if __name__ == '__main__':
    api.run(debug=False, port=5000, host='127.0.0.1')
