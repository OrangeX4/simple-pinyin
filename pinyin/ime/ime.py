import sys
sys.path.append('../')
from pinyin.cut import cut_pinyin_with_strategy, normlize_pinyin
from pinyin.hmm import viterbi

# 缓存结果, 加快判断
dp = {}
def ime(pinyin: str, limit=7):
    '''
    输入法函数, 综合分词和维特比算法的最终结果
    '''
    if pinyin in dp:
        return dp[pinyin][:limit]
    # 计算结果
    result = []
    # 获取分词结果
    cut = cut_pinyin_with_strategy(normlize_pinyin(pinyin))
    # 先尝试完整划分
    for pinyin in cut['intact'] + cut['intact_tail']:
        vit, remain_pinyin = viterbi(pinyin)
        if not remain_pinyin:
            result.extend([(pinyin,) + t for t in vit])
    # 如果完整划分的最小拼音大小小于等于 3, 则进行纠错
    if not result or min([len(pinyin) for pinyin in cut['intact'] + cut['intact_tail']]) <= 3:
        for pinyin in cut['error_correction'] + cut['error_correction_tail']:
            vit, remain_pinyin = viterbi(pinyin)
            if not remain_pinyin:
                result.extend([(pinyin,) + t for t in vit])
    # 如果结果为空, 则进行模糊划分
    if not result:
        for pinyin in cut['fuzzy']:
            vit, remain_pinyin = viterbi(pinyin)
            result.extend([(pinyin,) + t for t in vit])
    # 排序并取出前 limit 个
    dp[pinyin] = sorted(result, key=lambda x: x[2], reverse=True)
    return dp[pinyin][:limit]


if __name__ == '__main__':
    print(ime('jintian'))  # 基础功能
    print(ime('jintain'))  # 纠错功能
    print(ime('ji\'ntian'))  # 分词功能
    print(ime('jintiantianqibucuo'))  # 短句功能
    print(ime('jttqbc'))  # 首字母功能
    print(ime('nanjingdaxuerengongzhinengxueyuan'))  # 南京大学人工智能学院
    print(ime('nanjingdx'))  # 南京大学



