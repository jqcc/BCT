from flask import Flask, render_template, jsonify, request

import Crypto.Random
from Crypto.PublicKey import RSA

import rsa

import binascii

from transaction import Transaction

app = Flask(__name__)

# 主页面
@app.route('/')
def index():
    return render_template('index.html')

# 生成交易页面
@app.route('/make/transaction')
def make_transaction():
    return render_template('make_transaction.html')

# 查看交易页面
@app.route('/view/transactions')
def view_transaction():
    return render_template('view_transaction.html')

# 生成一个钱包逻辑, 其实就是生成了一个rsa的非对称加密秘钥
@app.route('/wallet/new0')
def new_wallet0():
    # 返回一个类文件(file-like)的对象,包含用于加密随机文字
    # 注意这里read没加括号,是个函数对象
    random_gen = Crypto.Random.new().read
    # random_gen会接受一个数字N(即第一个参数),生成一个长度为N的字符串
    # RSA.generate会利用这个字符串通过RSA非对称加密生成一个秘钥对象
    # 其中N应该是不小于1024且为256的倍数的数
    # 返回RSA秘钥对象
    private_key = RSA.generate(2048, random_gen)
    # 获取公钥对象
    public_key = private_key.publickey()
    response = {
        # format指定了编码方式,DER表示使用二进制,这里使用二进制是方便生成十六进制的公钥私钥
        # 默认方式是PEM,会生成除了数字还包含26个字母和特殊字符的秘钥
        'private_key': binascii.hexlify(private_key.export_key(format='DER')).decode('ascii'),
        'public_key': binascii.hexlify(public_key.export_key(format='DER')).decode('ascii')
    }
    return jsonify(response), 200

# 在生成钱包页面，通过rsa内置算法生成一对公钥与私钥
# 通过binascii转换为16进制的数字串
# 更换为rsa模块后的生成秘钥算法
@app.route('/wallet/new')
def new_wallet():
    # 使用rsa的算法模块生成秘钥，序列化后返回到前端
    # 512比较小 算的比较快
    # nbits: the number of bits required to store `n = p*q`
    public_key, private_key = rsa.newkeys(nbits=512)
    resonse = {
        'private_key':  binascii.hexlify(private_key.save_pkcs1('DER')).decode(),
        'public_key': binascii.hexlify(public_key.save_pkcs1('DER')).decode()
    }
    return jsonify(resonse), 200

# BCT客户端生成交易路由
@app.route('/generate/transaction', methods=['POST'])
def generate_transaction():
    sender_address = request.form['sender_address']
    sender_private_key = request.form['sender_private_key']
    recipient_address = request.form['recipient_address']
    value = request.form['amount']

    transaction = Transaction(sender_address, sender_private_key, recipient_address, value)
    response = {
        'transaction': transaction.to_dict(),
        'signature': transaction.sign_transaction()
    }
    print(response)
    return jsonify(response), 200

if __name__ == '__main__':
    import argparse

    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int, help='运行端口号')
    parser.add_argument('-t', '--host', default='127.0.0.1', type=str, help='运行服务器ip')
    parser.add_argument('-d', '--debug', default=True, type=bool, help='开启debug模式')
    args = parser.parse_args()
    
    # 提取参数
    port = args.port
    # 当host = '0.0.0.0'时,接受公网接口上的连接
    host = args.host
    debug = args.debug

    # 运行flask实例
    app.run(debug=debug, host=host, port=port)