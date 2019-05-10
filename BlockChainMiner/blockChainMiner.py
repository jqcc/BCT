from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from collections import OrderedDict

from blockChain import BlockChain

app = Flask(__name__)
CORS(app)  # 支持跨域请求

MINING_SENDER = 'THE BLOCKCHAIN'
MINING_REWARD = 1

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', default=5000, type=int, help='运行端口')
parser.add_argument('-t', '--host', default='127.0.0.1', type=str, help='运行服务器ip')
parser.add_argument('-d', '--debug', default=True, type=bool, help='开启debug模式')

args = parser.parse_args()
port = args.port
host = args.host
debug = args.debug

blockchain = BlockChain(port)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/configure')
def configure():
    return render_template('configure.html')

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
    required = ['sender_address', 'recipient_address', 'amount', 'signature']
    if not all(k in values for k in required):
        return '缺少必要信息', 400
    transaction_result = blockchain.submit_transaction(values['sender_address'], values['recipient_address'],
            values['amount'], values['signature'])

    if transaction_result == False:
        response = {'message': '验签失败!'}
        return jsonify(response), 400
    else:
        response = {'message': '交易会被添加到区块: ' + str(transaction_result)}
        return jsonify(response), 201

# 获取未验证的交易信息
@app.route('/transactions/get')
def get_transactions():
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200

# 返回区块链信息
@app.route('/chain')
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/mine')
def mine():
    # 可以挖空节点
    if len(blockchain.transactions) <= 0:
        empty_transaction = OrderedDict();
        empty_transaction['sender_address'] = MINING_SENDER
        empty_transaction['recipient_address'] = blockchain.node_id
        empty_transaction['value'] = 1
        blockchain.transactions.append(empty_transaction)
        blockchain.ins_t(empty_transaction)

    last_block = blockchain.chain[-1]
    nonce = blockchain.proof_of_work()

    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(nonce, previous_hash)

    response = {
        'message': '生成新的区块',
        'block_number': block['block_number'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form
    nodes = values.get('nodes').replace(' ', '').split(',')

    if nodes is None:
        return 'Error: 请提供有效的节点链接', 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': '成功加入新的区块链节点',
        'total_nodes': [node for node in blockchain.nodes]
    }
    return jsonify(response), 201

@app.route('/nodes/resolve')
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': '本地链被替换',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': '本地链是有效的',
            'chain': blockchain.chain
        }
    return jsonify(response), 200

@app.route('/nodes/get')
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200

# 添加404页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# 添加500页面
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/500error')
def er():
    return render_template('500.html'), 500


if __name__ == '__main__':

    app.run(debug=debug, host=host, port=port)