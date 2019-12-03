# 写代码的一些记录

## 一些记录

记录一些方便粘贴的内容

```html
    <!-- jQuery -->
    <script src="/static/lib/jquery/jquery.min.js"></script>

    <!-- Bootstrap -->
    <link href="/static/lib/bootstrap/bootstrap.min.css" rel="stylesheet">
    <script src="/static/lib/bootstrap/bootstrap.bundle.min.js"></script>

    <!-- 自定义 -->
    <link href="/static/css/main.css" rel="stylesheet">
    <script src="/static/js/main.js"></script>
```

## 一些问题

### 关于静态文件引用

引用静态文件, 如: css, js, img等, 这里有两种方式(以css文件为例, js,img相同).

1. `<link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='path/to/file.css') }}"`

2. `<link rel="stylesheet" type="text/css" href="static/path/to/file.css">`

注意, static应该和templates文件在同一级目录下.

### DataTables的图片文件说明

查看`datatables.min.css`会发现里面`css`样式定义有一段: `background-image:url("DataTables-1.10.16/images/sort_both.png")`限定了图片资源路径, 所以这里会突兀的多出了一个这样的文件夹, 可以对该`css`源文件进行修改, 人工修改资源定位文件路径.

### 待做

1. 添加MySQL持久化(目前采用pymysql读写数据库,考虑使用SQLAlchemy)
    具体的: 目前连接数据库考虑的简单的pymysql进行读写,不是很原生,有些操作比较繁琐,
    后期建议换成SQLAlchemy, 定义model视图. 采用标准的MVC架构.
2. 保存某矿工节点的其它矿工节点.
    具体的: 矿工端 - 配置页, 该页面用于更新区块链交易信息, 选取最长的链作为官方链.但每次关机后本次保存的其它矿工节点信息丢失.
    因此选择持久化其它矿工节点信息, 并根据是否能ping通, 对矿工节点进行分类.
    保存两个表. 一个是当前节点保存过的所有矿工节点, 另一个是本次可以连通的矿工节点.
3. 用一个RNN模型拟合BCTS币的交易价格, 预测未来一天的交易价格
    具体的: 后台运行一个正弦函数加高斯噪声作为比特币价格波动. 使用一个RNN神经网络拟合该函数, 进行价格预测.
    由于这里不涉及比特币价格相关内容, 此任务可选做, 主要可以用来扩大工作量.
4. 查看每个钱包的BCTS币数量
    具体的: 每个钱包地址生成交易时, 需要验证是否满足余额限定.
    这一项不是很好做. 目前不是很清楚比特币的机制, 选做.
