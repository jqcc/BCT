from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

import rsa
import base64

import binascii
from collections import OrderedDict

class Transaction:

    '''
    生成交易所需的数据
    sender_address: 交易发起方公钥
    sender_private_key: 交易发起方私钥
    recipient_address: 交易接收方公钥
    value: 交易金额
    '''
    def __init__(self, sender_address, sender_private_key, recipient_address, value):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.value = value

    # 生成有序字典
    def to_dict(self):
        # 按照加密需要,需要有序字典
        odict = OrderedDict();
        odict['sender_address'] = self.sender_address
        odict['recipient_address'] = self.recipient_address
        odict['value'] = self.value
        return odict

    # 根据交易发起方的私钥对交易信息进行签名
    def sign_transaction2(self):
        # 导入一个RSA的key(公钥或私钥)
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        # 返回一个签名对象, 可以用于签名或验证
        signer = PKCS1_v1_5.new(private_key)
        # 生成一个哈希对象的实例,其中携带了交易信息
        h = SHA.new(str(self.to_dict()).encode("utf-8"))
        # 对交易信息进行签名 返回对应十六进制的值
        return binascii.hexlify(signer.sign(h)).decode('ascii')

    # 使用rsa模块
    def sign_transaction(self):
        # 还原私钥对象
        private_key = rsa.PrivateKey.load_pkcs1(binascii.unhexlify(self.sender_private_key), format='DER')
        # 生成数字签名 如果验证成功返回值为hash算法名称 这里为'MD5'
        return binascii.hexlify(rsa.sign(str(self.to_dict()).encode(), private_key, 'MD5')).decode()