# -*- coding=utf8 -*-

'''
HMM 模型训练, 结果保存在 data 中.
训练数据使用的是 "北京语言大学 BCC 语料库 http://bcc.blcu.edu.cn" 和文献 (以bcc网站的最新引用说明为准).
最终解释权归北语大数据与教育技术研究所所有.
'''

import sys
sys.path.append('../')

from pinyin.train.dataset import (
    iter_word_and_freq
)
from pinyin.train.train_hmm import (
    set_config,
    gen_start,
    gen_transition,
    gen_emission
)

def train_hmm():
    print('Start training HMM model...')
    print('Generate start vector...')
    gen_start()
    print('Generate transition matrix...')
    gen_transition()
    print('Generate emission matrix...')
    gen_emission()
    print('Done.')

if __name__ == '__main__':
    train_hmm()
