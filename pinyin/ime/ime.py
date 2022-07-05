import sys
sys.path.append('../')
from pinyin.cut import cut_pinyin_with_strategy, normlize_pinyin
from pinyin.hmm import viterbi
from pinyin.ime.emoji import load_emoji_dict

# 加载 emoji 字典
emoji_dict = load_emoji_dict()

# 缓存结果, 加快判断
dp = {}
def ime(pinyin: str, limit=7):
    '''
    输入法函数, 综合分词和维特比算法的最终结果, 并且会加入 emoji
    '''
    def replace_with_emoji(tuples):
        '''
        如果第一个中文有对应 emoji, 则使用 emoji 将其替换
        '''
        if tuples and tuples[0][1] in emoji_dict:
            return [tuples[0], (tuples[0][0], emoji_dict[tuples[0][1]], tuples[0][2] - 1e-5)] + tuples[1:-1]
        else:
            return tuples
    
    if pinyin in dp:
        return replace_with_emoji(dp[pinyin][:limit])
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
    return replace_with_emoji(dp[pinyin][:limit])


if __name__ == '__main__':
    print(ime('jintian', limit=1))  # 基础功能
    print(ime('jintain', limit=1))  # 纠错功能
    print(ime('ji\'ntian', limit=1))  # 分词功能
    print(ime('jintiantianqibucuo', limit=1))  # 短句功能
    print(ime('jttqbc', limit=1))  # 首字母功能
    print(ime('xiaolian', limit=1))  # emoji 功能
    print(ime('nanjingdaxuerengongzhinengxueyuan', limit=1))  # 南京大学人工智能学院
    print(ime('nanjingdx', limit=1))  # 南京大学



