from uuid import uuid4
from urllib.parse import urlparse
import binascii
from collections import OrderedDict
from time import time
import json
import hashlib

import requests

# 加密模块
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

import rsa

MINING_SENDER = 'THE BLOCKCHAIN'
MINING_DIFFICULTY = 2

class BlockChain:

    def __init__(self):
        self.transactions = []
        self.chain = []
        self.nodes = set()
        # 使用uuid生成一个结点id
        self.node_id = str(uuid4()).replace('-', '')
        # 创世块
        self.create_block(0, "00")

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

    def submit_transaction(self, sender_address, recipient_address, value, signature):
        transaction = OrderedDict();
        transaction['sender_address'] = sender_address
        transaction['recipient_address'] = recipient_address
        transaction['value'] = value
        
        if sender_address == MINING_SENDER:
            self.transactions.append(transaction)
            return len(self.chain) + 1
        else:
            print('111', transaction)
            transaction_verification = self.verify_transaction_signature(sender_address, signature, transaction)
            if transaction_verification:
                self.transactions.append(transaction)
                return len(self.chain) + 1
            else:
                return False
    
    def create_block(self, nonce, previous_hash):
        block = {
            'block_number': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        }

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

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            transactions = block['transactions'][:-1]
            transaction_elements = ['sender_address', 'recipient_address', 'value']
            transactions = [OrderedDict((key, transaction[key]) 
                    for key in transaction_elements) for transaction in transactions]
            
            if not self.valid_proof(transactions, block['previous_hash'], block['nonce'], MINING_DIFFICULTY):
                return False

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
        
        return False
