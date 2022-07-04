'''
author: OrangeX4
date: 2022-07-04

维特比算法

代码参考 https://github.com/LiuRoy/Pinyin_Demo
'''

import json
import heapq
import sys
sys.path.append('../')

def file2json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# 加载数据
start_path = 'data/hmm_start.json'
reversed_transition_path = 'data/hmm_reversed_transition.json'
reversed_emission_path = 'data/hmm_reversed_emission.json'
start_vector = file2json(start_path)
reversed_transition_matrix = file2json(reversed_transition_path)
reversed_emission_matrix = file2json(reversed_emission_path)


def viterbi(pinyin, limit=10):
    """
    viterbi 算法

    pinyin: 拼音元组

    return: 返回 limit 个最可能的汉字序列, 但是是 1 个全局最优解和 limit - 1 个局部最优解
    """
    # 初始化, 找出第一个拼音对应的汉字以及 start 和 emission 概率之积 (对数下为相加)
    char_and_prob = ((ch, start_vector[ch] + reversed_emission_matrix[pinyin[0]][ch]) for ch in reversed_emission_matrix[pinyin[0]])
    # 取出概率最大的 limit 个
    V = {char: prob for char, prob in heapq.nlargest(limit, char_and_prob, key=lambda x: x[1])}

    for i in range(1, len(pinyin)):
        py = pinyin[i]

        prob_map = {}
        for phrase, prob in V.items():
            previous = phrase[-1]
            if py in reversed_transition_matrix[previous]:
                state, new_prob = reversed_transition_matrix[previous][py]
                prob_map[phrase + state] = new_prob + prob

        if prob_map:
            V = prob_map
        else:
            return V
    return V


if __name__ == '__main__':
    print(viterbi(('j', 't', 't', 'q', 'b', 'c')))