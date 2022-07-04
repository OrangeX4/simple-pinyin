'''
拼音划分单元测试
'''

from pinyin.cut import (
    cut_pinyin,
    cut_pinyin_with_error_correction,
    cut_pinyin_with_strategy
)

def test_cut_pinyin():
    # print(cut_pinyin('kongjian', True))
    assert cut_pinyin('kongjian', True) == [('kong', 'jian'), ('kong', 'ji', 'an')]
    # print(cut_pinyin('zhang\'an\'gai', True))
    assert cut_pinyin('zhang\'an\'gai', True) == [('zhang', 'an', 'gai')]

def test_cut_pinyin_with_error_correction():
    # print(cut_pinyin_with_error_correction('tain'))
    assert cut_pinyin_with_error_correction('tain') == {'tian': [('tian',), ('ti', 'an')], 'tani': [('ta', 'ni')], 'all': [('tian',), ('ti', 'an'), ('ta', 'ni')]}

def test_cut_pinyin_with_strategy():
    # print(cut_pinyin_with_strategy('kauil')['error_correction_tail'])
    assert cut_pinyin_with_strategy('kauil')['error_correction_tail'] == [('kuai', 'l'), ('ku', 'ai', 'l')]
