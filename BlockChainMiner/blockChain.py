from uuid import uuid4
from urllib.parse import urlparse
import binascii
from collections import OrderedDict
from time import time
import json
import hashlib

import requests
import pymysql

# 加密模块
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

import rsa

MINING_SENDER = 'THE BLOCKCHAIN'
MINING_DIFFICULTY = 2

class BlockChain:

    def __init__(self, port):
        self.transactions = []
        self.chain = []
        self.nodes = set()
        # 使用uuid生成一个结点id
        self.node_id = str(uuid4()).replace('-', '')
        self.port = port
        self.database = "bct"+str(port)

        self.init_from_db()

    def init_from_db(self):
        # 连接数据库
        conn = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="root",
                database=self.database
            )

        # 创建一个执行sql的游标
        cursor = conn.cursor()

        sql1 = """
        select * from blockchain order by block_number;
        """
        sql2 = """
        select * from transactions order by block_number;
        """

        try:
            cursor.execute(sql1)
            data = cursor.fetchall()
            # print(data, len(data))
            if len(data) > 0:
                for row in data:
                    block = {
                        'block_number': row[1],
                        'timestamp': float(row[2]),
                        'transactions': [],
                        'nonce': row[3],
                        'previous_hash': row[4]
                    }
                    self.chain.append(block)
            else:
                # 创世块
                self.create_block(0, "00")

            cursor.execute(sql2)
            data = cursor.fetchall()

            block, row, lim_block, lim_row = 0, 0, len(self.chain), len(data)

            while block < lim_block and row < lim_row:
                transaction = OrderedDict();
                transaction['sender_address'] = data[row][2]
                transaction['recipient_address'] = data[row][3]
                transaction['value'] = data[row][4]
                if data[row][1] == -1:
                    self.transactions.append(transaction)
                    row += 1
                elif data[row][1] == self.chain[block]['block_number']:
                    self.chain[block]['transactions'].append(transaction)
                    row += 1
                else:
                    block += 1
        except:
            print("error: init_from_db")

        conn.close()

    def register_node(self, node_url):
        # 解析url后面跟的参数 返回一个字典
        parsedUrl = urlparse(url=node_url)
        if parsedUrl.netloc:
            self.nodes.add(parsedUrl.netloc)
        elif parsedUrl.path:
            self.nodes.add(parsedUrl.path)
        else:
            raise ValueError("无效的url")

    # 原验签算法
    def verify_transaction_signature0(self, sender_address, signature, transaction):
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifer = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf-8'))
        return verifer.verify(h, signature)

    # 换成rsa算法验签 如果正确会返回hash算法的名称，这里是'MD5'
    def verify_transaction_signature(self, sender_address, signature, transaction):
        signature = binascii.unhexlify(signature)
        sender_address = rsa.PublicKey.load_pkcs1(binascii.unhexlify(sender_address), format='DER')
        
        try:
            shaAlgo = rsa.verify(str(transaction).encode(), signature, sender_address)
            print('algo: ', shaAlgo)
            return shaAlgo == 'MD5'
        except Exception as e:
            print('error: ', e)
            return False

    # insert transaction表
    # 由于还未验证, block_number均为-1
    def ins_t(self, transaction):
        # 连接数据库
        conn = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="root",
                database=self.database
            )

        # 创建一个执行sql的游标
        cursor = conn.cursor()

        # 插入
        sql = " \
        insert into \
        transactions(block_number, sender_address, recipient_address, value) \
        values(%i, '%s', '%s', '%s');" % (-1, transaction['sender_address'], 
        transaction['recipient_address'], transaction['value'])

        # print(sql)
        try:
            cursor.execute(sql)
            conn.commit()
        except:
            print("error: ins_t")
            conn.rollback()
        
        conn.close()

    # BCT客户端发来的验证交易请求
    def submit_transaction(self, sender_address, recipient_address, value, signature):
        transaction = OrderedDict();
        transaction['sender_address'] = sender_address
        transaction['recipient_address'] = recipient_address
        transaction['value'] = value
        
        if sender_address == MINING_SENDER:
            self.transactions.append(transaction)
            return len(self.chain) + 1
        else:
            # print('submit_transaction: ', transaction)
            transaction_verification = self.verify_transaction_signature(sender_address, signature, transaction)
            if transaction_verification:
                self.transactions.append(transaction)
                # 插入transaction到数据库中
                self.ins_t(transaction)
                return len(self.chain) + 1
            else:
                return False
    
    # insert blockchain表, update transactions表
    # transaction表中block_number为-1的均换为当前block_number
    def ins_bct_upd_t(self, block):
        # 连接数据库
        conn = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="root",
                database=self.database
            )

        # 创建一个执行sql的游标
        cursor = conn.cursor()
        # 插入
        sql1 = " \
        insert into \
        blockchain(block_number, timestamp, nonce, previous_hash) \
        values(%i, '%s', %i, '%s');" % (block['block_number'], block['timestamp'],
        block['nonce'], block['previous_hash'])
        sql2 = "update transactions set block_number = %i where block_number = -1;"%(block['block_number'])

        try:
            cursor.execute(sql1)
            cursor.execute(sql2)
            conn.commit()
        except:
            print("error: ins_bct_upd_t")
            conn.rollback()
        
        conn.close()

    def create_block(self, nonce, previous_hash):
        block = {
            'block_number': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        }
        
        # 把block插入到数据库中, 并把transactions表清空
        self.ins_bct_upd_t(block)
        
        # 之前的交易已经被打包放到block里面了
        # 现在的transactions里应该是空的
        self.transactions = []

        self.chain.append(block)
        return block

    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()
    
    def proof_of_work(self):
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        nonce = 0
        while self.valid_proof(self.transactions, last_hash, nonce) is False:
            nonce += 1
        return nonce

    def valid_proof(self, transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
        guess = (str(transactions)+str(last_hash)+str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0' * difficulty

    # 验证链的有效性
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False
            print("ok11")
            transactions_list = block['transactions'][:]
            # transaction_elements = ['sender_address', 'recipient_address', 'value']
            # transactions = [OrderedDict((key, transaction[key]) 
            #         for key in transaction_elements) for transaction in transactions]

            transactions = []
            for tr in transactions_list:
                transaction = OrderedDict();
                transaction['sender_address'] = tr['sender_address']
                transaction['recipient_address'] = tr['recipient_address']
                transaction['value'] = tr['value']
                transactions.append(transaction)
            
            print(transactions)
            
            if not self.valid_proof(transactions, block['previous_hash'], block['nonce'], MINING_DIFFICULTY):
                return False
            print("ok2")
            last_block = block
            current_index += 1
        return True
    
    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get('http://' + node + '/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            # 还没成功
            # 把新链写入数据库, 先删库, 后写入, 主要针对blockchain表
            # 连接数据库
            conn = pymysql.connect(
                    host="127.0.0.1",
                    user="root",
                    password="root",
                    database=self.database
                )

            # 创建一个执行sql的游标
            cursor = conn.cursor()
            # 删除原有的链
            sql1 = "delete from blockchain;"
            sql3 = "delete from transactions;"

            try:
                # 删除无效数据
                cursor.execute(sql1)
                cursor.execute(sql3)
                # 插入新链
                for block in self.chain:
                    # 插入区块信息
                    sql2 = " \
                        insert into \
                        blockchain(block_number, timestamp, nonce, previous_hash) \
                        values(%i, '%s', %i, '%s');" % (block['block_number'], block['timestamp'],
                        block['nonce'], block['previous_hash'])
                    cursor.execute(sql2)
                    for tr in block['transactions']:
                        # 插入区块中的交易信息
                        sql4 = "\
                            insert into \
                            transactions(block_number, sender_address, recipient_address, value) \
                            values(%i, '%s', '%s', '%s');" % (block['block_number'], tr['sender_address'],
                            tr['recipient_address'], tr['value'])
                        cursor.execute(sql4)
                
                conn.commit()
            except:
                print("error: ins_bct_upd_t")
                conn.rollback()
            
            conn.close()

        
        return False
