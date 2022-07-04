# -*- coding=utf8 -*-

'''
HMM 模型训练, 结果保存在 data 中 `hmm_xxx.json` 文件中.
训练数据使用的是 "北京语言大学 BCC 语料库 http://bcc.blcu.edu.cn" 和文献 (以bcc网站的最新引用说明为准).
最终解释权归北语大数据与教育技术研究所所有.
'''

import json
import sys
sys.path.append('../')

from pinyin.train.dataset import (
    iter_word_and_freq
)
from pinyin.train.train_hmm import (
    set_config,
    gen_start,
    gen_transition,
    gen_emission,
    gen_reversed_matrix
)

def file2json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def train_hmm():
    print('Start training HMM model...')
    # print('Generate start vector...')
    # gen_start()
    # print('Generate transition matrix...')
    # gen_transition()
    # print('Generate emission matrix...')
    # gen_emission()
    # print('Generate reversed emission matrix...')
    transition_path = 'data/hmm_transition.json'
    emission_path = 'data/hmm_emission.json'
    transition_matrix = file2json(transition_path)
    emission_matrix = file2json(emission_path)
    gen_reversed_matrix(emission_matrix, transition_matrix)
    print('Done.')

if __name__ == '__main__':
    train_hmm()
