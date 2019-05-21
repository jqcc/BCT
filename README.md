# BCTS(BlockChain Transaction System)

区块链支付结算系统的设计与实现。

## 环境要求

* python3.5

## 使用

### 环境安装

1. 安装[python3](https://www.python.org/)
2. 安装依赖

```bash
pip install -i http://pypi.douban.com/simple -- trusted-host pypi.douban.com -r requirements.txt
```

## 待做

1. 添加MySQL持久化(目前采用pymysql读写数据库,考虑使用SQLAlchemy)
    目前每个节点对应一个数据库
    考虑更新为每个节点对应一个数据中的两个表
2. 持久化某矿工节点保存的其它矿工节点
3. 完善页面错误, 警告等提示
4. 增加一个区块链服务器, 调整系统逻辑为, 生成交易发送到区块链服务器, 由区块链服务器发送到各个矿工端.
    矿工端在生成时就应该到区块链服务器进行登记注册。

## 其他

### 相关资料

* ~~加密库Crypto相关文档: [Crypto](https://www.dlitz.net/software/pycrypto/api/current/Crypto-module.html "已换新加密模块rsa")~~
* pymysql教程: [pymysql-菜鸟教程](http://www.runoob.com/python3/python3-mysql.html)