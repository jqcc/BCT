from reportlab.pdfbase import pdfmetrics  
from reportlab.pdfbase.cidfonts import UnicodeCIDFont  
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
from reportlab.pdfbase.ttfonts import TTFont 
pdfmetrics.registerFont(TTFont('msyh', 'msyh.ttf'))  
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
import time
import os

def wallet_report(pub_key, pri_key):
    # 生成一个存储的对象集合
    story=[]
    # 生成样式表
    stylesheet=getSampleStyleSheet()
    # 字体的样式
    normalStyle = stylesheet['Normal']

    curr_date = time.strftime("%Y-%m-%d", time.localtime())

    #标题：段落的用法详见reportlab-userguide.pdf中chapter 6 Paragraph
    rpt_title = '<para autoLeading="off" fontSize=15 align=center><b><font face="msyh">钱包 : {0}</font></b><br/><br/><br/></para>'.format(curr_date)
    
    # 将我们的标题文本样式追加到story
    story.append(Paragraph(rpt_title,normalStyle)) 

    text = '''<para autoLeading="off" fontSize=8><font face="msyh" >钱包地址：</font><br/>
    <font face="msyh" color=red>1.pub_key：{0}</font><br/>
    <font face="msyh" color=orange>2.pri_key：{1}</font><br/>
    </para>'''.format(pub_key, pri_key)

    # 生成的段落文本样式加到story
    story.append(Paragraph(text,normalStyle))

    tm = str(time.time()).split('.')[1]
    print(os.getcwd())
    doc = SimpleDocTemplate('./pdfs/wallet_' + tm + '.pdf')
    doc.build(story)

    # 只需要返回文件名
    return 'wallet_' + tm + '.pdf'

if __name__ == '__main__':
    wallet_report('123', '321')