# 加载完整拼音对应的拼音表 data/all_pinyin.txt
intact_pinyin_set = set()
with open('data/all_pinyin.txt', 'r', encoding='utf-8') as f:
    intact_pinyin_set = set(s for s in f.read().split('\n') if len(s) > 1) | {'a', 'o', 'e'}

# 生成带残缺部分的拼音, 例如 'ruan' 对应的 'r', 'ru' 和 'rua'
all_pinyin_set = set(s[:i] for s in intact_pinyin_set for i in range(1, len(s) + 1))

# 用于保存动态规划答案的字典
intact_cut_pinyin_ans = {}
all_cut_pinyin_ans = {}
# 动态规划判断进行拼音划分
def cut_pinyin(pinyin: str, is_intact=False, is_break=True):
    '''
    进行拼音划分, 返回拼音划分结果列表
    pinyin: 待划分的拼音, 并且是无空格字符串, 例如 `kongjian`
    is_intact: 拼音是否需要完整匹配, 默认为 False, 可以使用残缺部分的拼音进行分词
    is_break: 是否开启分隔符, 开启后可以使用 ' 进行分割, 例如 `kong'jian`
    
    return: 拼音划分结果列表, 例如 `cut_pinyin('kongjian', True)` 会返回 `[('kong', 'jian'), ('kong', 'ji', 'an')]`
    '''
    if is_intact:
        pinyin_set = intact_pinyin_set
        ans_dict = intact_cut_pinyin_ans    
    else:
        pinyin_set = all_pinyin_set
        ans_dict = all_cut_pinyin_ans
    # 如果保存有, 直接返回保存结果
    if pinyin in ans_dict:
        return ans_dict[pinyin]
    # 如果 is_break, 就进行分割
    if is_break and '\'' in pinyin:
        pinyins = pinyin.split('\'')
        components = [cut_pinyin(p, is_intact, False) for p in pinyins]
        ans = components[0]
        for i in range(1, len(components)):
            ans = [p1 + p2 for p1 in ans for p2 in components[i]]
        return ans
    # 如果没有, 递归地动态规划生成
    ans = [] if pinyin not in pinyin_set else [(pinyin,)]
    for i in range(1, len(pinyin)):
        # 进行划分 pinyin[:i], 如果是正确拼音, 就继续动态规划
        if pinyin[:i] in pinyin_set:
            appendices = cut_pinyin(pinyin[i:], is_intact, is_break=False)
            for appendix in appendices:
                ans.append((pinyin[:i],) + appendix)
    ans_dict[pinyin] = ans
    return ans

def cut_pinyin_with_error_correction(pinyin: str):
    '''
    纠错匹配, 从第二个字母开始, 依次交换两个连续字母并进行*完整划分*.
    如果完整划分返回非空列表, 即匹配成功, 并加入到返回字典中.
    pinyin: 待纠错划分的拼音

    return: 返回字典, 字典的 key 为纠错后的拼音序列, value 为匹配成功的划分结果.
            并且会包含一个 key = 'all' 的项, 包括了所有 value.
    '''
    ans = {}
    for i in range(1, len(pinyin) - 1):
        key = pinyin[:i] + pinyin[i + 1] + pinyin[i] + pinyin[i + 2:]
        value = cut_pinyin(key, is_intact=True)
        if value:
            ans[key] = value
    ans['all'] = [p for t in ans.values() for p in t]
    return ans

def cut_pinyin_with_strategy(pinyin: str):
    '''
    使用各种策略对拼音进行划分, 其中包括:
    1. 完整划分
    2. 去尾字母完整划分
    3. 纠错划分
    4. 去尾字母纠错划分
    5. 结果综合 (不含模糊划分)
    6. 模糊划分

    pinyin: 待划分的拼音

    return: {
        'intact': [...],
        'intact_tail': [...],
        'error_correction': [...],
        'error_correction_tail': [...],
        'combine': [...],
        'fuzzy': [...]
    }
    '''
    ans = {
        'intact': cut_pinyin(pinyin, is_intact=True),
        'intact_tail': [] if pinyin[-1] not in all_pinyin_set else [t + (pinyin[-1],) for t in cut_pinyin(pinyin[:-1], is_intact=True)],
        'error_correction': cut_pinyin_with_error_correction(pinyin)['all'],
        'error_correction_tail': [] if pinyin[-1] not in all_pinyin_set else [t + (pinyin[-1],) for t in cut_pinyin_with_error_correction(pinyin[:-1])['all']],
        'combine': [],
        'fuzzy': cut_pinyin(pinyin, is_intact=False)
    }
    ans['combine'] = ans['intact'] + ans['intact_tail'] + ans['error_correction'] + ans['error_correction_tail']
    return ans


if __name__ == '__main__':
    # print(cut_pinyin('kongjian', True))
    assert cut_pinyin('kongjian', True) == [('kong', 'jian'), ('kong', 'ji', 'an')]
    # print(cut_pinyin('zhang\'an\'gai', True))
    assert cut_pinyin('zhang\'an\'gai', True) == [('zhang', 'an', 'gai')]
    
    # print(cut_pinyin_with_error_correction('tain'))
    assert cut_pinyin_with_error_correction('tain') == {'tian': [('tian',), ('ti', 'an')], 'tani': [('ta', 'ni')], 'all': [('tian',), ('ti', 'an'), ('ta', 'ni')]}
    # print(cut_pinyin_with_strategy('kauil')['error_correction_tail'])
    assert cut_pinyin_with_strategy('kauil')['error_correction_tail'] == [('kuai', 'l'), ('ku', 'ai', 'l')]
