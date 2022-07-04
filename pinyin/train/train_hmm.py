'''
Author: OrangeX4
Date: 2022-07-04

本部分代码参考 https://github.com/LiuRoy/Pinyin_Demo
'''

from math import log
# 用于将汉字转化为拼音
from pypinyin import pinyin as get_pinyin, NORMAL
from tqdm import tqdm
# 用于加载词频数据
from pinyin.train.dataset import iter_word_and_freq
import json

# 以 JSON 格式保存稀疏矩阵的路径
# 分别是初始状态概率向量 π、转移矩阵 A 和发射矩阵 B
hmm_start_path = 'data/hmm_start.json'
hmm_transition_path = 'data/hmm_transition.json'
hmm_emission_path = 'data/hmm_emission.json'
hmm_start_counter_path = 'data/checkpoints/hmm_start_counter.json'
hmm_transition_counter_path = 'data/checkpoints/hmm_transition_counter.json'
hmm_emission_counter_path = 'data/checkpoints/hmm_emission_counter.json'

# 拼音简写的权重
_config = {
    'is_save_counter': True,
    'intact_weight': 5,
    'first_letter_weight': 3,
    'fuzzy_weight': 1,
}


def set_config(config):
    """
    设置拼音简写的权重, 默认为
    config = {
        'is_save_counter': True,
        'intact_weight': 5,
        'first_letter_weight': 3,
        'fuzzy_weight': 1,
    }
    """
    global _config
    _config = config


def json2file(obj, filename):
    with open(filename, mode='w', encoding='utf-8') as out_file:
        data = json.dumps(obj, indent=4, sort_keys=True, ensure_ascii=False)
        out_file.write(data)


def gen_start():
    """
    生成初始状态概率向量 π
    """
    start_counter = {}  # 用于计数
    total_count = 0
    for word, freq in tqdm(iter_word_and_freq()):
        total_count += freq
        start_counter[word[0]] = start_counter.get(word[0], 0) + freq
    start_vector = {}  # 需要保存的结果
    for ch, count in start_counter.items():
        # 除以总计数并取对数
        start_vector[ch] = log(count / total_count)
    if _config['is_save_counter']:
        json2file(start_counter, hmm_start_counter_path)  # 便于后续累计计算
    # 保存为 JSON 格式
    json2file(start_vector, hmm_start_path)
    


def gen_transition():
    """
    生成转移矩阵 A
    """
    transition_counter = {}  # 用于计数
    for word, freq in tqdm(iter_word_and_freq()):
        for i in range(len(word) - 1):
            # 保存从前一个字到后一个字的频率
            if word[i] in transition_counter:
                transition_counter[word[i]][word[i+1]] = \
                    transition_counter[word[i]].get(word[i+1], 0) + freq
            else:
                transition_counter[word[i]] = {word[i+1]: freq}
    transition_matrix = {}  # 需要保存的结果
    for previous, behind_map in transition_counter.items():
        sum_frequency = sum(behind_map.values())
        transition_matrix[previous] = {}
        for behind, freq in behind_map.items():
            transition_matrix[previous][behind] = log(freq / sum_frequency)
    if _config['is_save_counter']:
        json2file(transition_counter, hmm_transition_counter_path)  # 便于后续累计计算
    # 保存为 JSON 格式
    json2file(transition_matrix, hmm_transition_path)


def gen_emission():
    """
    生成发射矩阵 B
    """
    emission_counter = {}
    for word, freq in iter_word_and_freq():
        all_pinyins = get_pinyin(word, style=NORMAL)
        for ch, pinyins in zip(word, all_pinyins):
            count_of_pinyins = len(pinyins)
            if ch not in emission_counter:
                emission_counter[ch] = {}
            for py in pinyins:
                def add_to_counter(x, weight):
                    emission_counter[ch][x] = emission_counter[ch].get(x, 0) + \
                                        weight * freq // count_of_pinyins            
                if len(py) >= 1:
                    # 处理完整拼音情况
                    add_to_counter(py, _config['intact_weight'])
                if len(py) >= 2:
                    # 处理首字母情况
                    add_to_counter(py[0], _config['first_letter_weight'])
                if len(py) >= 3:
                    # 处理模糊拼音情况
                    for i in range(2, len(py)):
                        add_to_counter(py[:i], _config['fuzzy_weight'])
    emission_matrix = {}
    for ch, pinyin_map in emission_counter.items():
        sum_frequency = sum(pinyin_map.values())
        emission_matrix[ch] = {}
        for pinyin, freq in pinyin_map.items():
            emission_matrix[ch][pinyin] = log(freq / sum_frequency)
    if _config['is_save_counter']:
        json2file(emission_counter, hmm_emission_counter_path)  # 便于后续累计计算
    # 保存为 JSON 格式
    json2file(emission_matrix, hmm_emission_path)
