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
    for pinyin in cut['combine']:
        try:
            result.extend([(pinyin,) + t for t in viterbi(pinyin)])
        except Exception as e:
            pass
    # 排序并取出前 limit 个
    dp[pinyin] = sorted(result, key=lambda x: x[2], reverse=True)
    return dp[pinyin][:limit]


if __name__ == '__main__':
    print(ime('jintian'))
    print(ime('jintain'))
    print(ime('ji\'ntian'))
    print(ime('jintiantianqibucuo'))
    print(ime('jttqbc'))


