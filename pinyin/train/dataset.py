'''
数据集的接口, 读取数据集
'''

words_path = './data/test_words.txt'

def set_words_path(path):
    global words_path
    words_path = path

def is_Chinese(word):
    '''
    判断一个字符串是否全由汉字组成, 用于过滤文本
    '''
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def iter_word_and_freq():
    """
    词频数据集, 迭代地返回 (word, freq)
    """
    with open(words_path, 'r', ) as f:
        for line in f:
            word, frequency = line.split()
            # 进行过滤
            if is_Chinese(word):
                yield word, int(frequency)
