# -*- coding=utf8 -*-

'''
HMM 模型训练, 结果保存在 data 中.
训练数据使用的是 "北京语言大学 BCC 语料库 http://bcc.blcu.edu.cn" 和文献 (以bcc网站的最新引用说明为准).
最终解释权归北语大数据与教育技术研究所所有.
'''

from pinyin.train.dataset import (
    iter_word_and_freq
)
# from pinyin.train.hmm import 

