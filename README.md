# 简易拼音输入法（拼音转汉字）

## 一、使用介绍

以下是具体实现过程的介绍。

## 二、拼音划分

首先要解决的问题是，如何对长拼音序列进行划分。

由于我们只有文本语料，没有输入法语料（即用户的输入习惯），我们只能够通过编写规则的方式进行拼音划分。

- **普通情况**：完整的、无错的、没有歧义的拼音序列，例如 `kongqi` 只能划分为 `kong'qi`，即「空气」，并且是完整的、无错的、没有歧义的。这种情况处理起来比较简单，只需要按照「声母」和「韵母」的简单划分和匹配即可。
- **拼音简写**：用户在输入的时候，往往不会输入完整的拼音，而是输入一部分拼音。而缩写的情况又有几种类别，由于没有输入法语料，我就按照我自己使用的简写方式频率排列，以「中国」举例如下：
    - **先整后简**：`zhong'g`，也即「去尾字母完整划分」，我们在输入一个词语的时候，常常会输入了前一个字的完整拼音，又输入后一个字的开头拼音，输入法就会匹配到对应的词语，不需要输入完整的拼音。
    - **完全简写**：`z'g`，我们只输入词语的拼音首字母，也是比较常见的情况。
    - **先简后整**：`z'guo`，比较少见，一般出现在想要使用「完全简写」的方式输入，但是发现匹配不到，因此再输入后一个字的
    - **部分简写**：`zh'g`，不太常见，但是也存在这种情况。
- **顺序错误**：用户在输入拼音的时候，可能会因为打字打得比较快，有一些字的拼音的顺序弄反了，例如「小路」的 `xiao'lu` 打成了 `xaio'lu`，这时候输入法应该给予纠正。
- **存在歧义**：例如 `xianmianguan` 既可以划分为 `xian'mian'guan`，即「鲜面馆」，也可以划分为 `xi'an'mian'guan`，即「西安面馆」，这时候拼音划分就存在着歧义。如果涉及到拼音简写，则歧义会更多，如 `zhongguo` 甚至可以划分为 `z'hong'gu'o`。

我们需要将拼音划分分为两个不同的场景，不同场景的应用不同。第一个场景是「用户输入拼音序列划分」，第二个场景是「文字转拼音后划分」，前者用于预测，后者用于训练。

用户输入拼音序列划分只需要使用简单的动态规划即可实现，将所有合法的拼音序列划分方式都给列举出来，然后同时进行预测。

首先是输入拼音序列的划分，可以通过 `from pinyin.cut import cut_pinyin` 引入，具体的实现代码如下，使用了简单的动态规划，并加入了使用 `'` 分词的功能：

```python
# 加载完整拼音对应的拼音表 data/intact_pinyin.txt, 共 416 个
intact_pinyin_set = set()
with open('data/intact_pinyin.txt', 'r', encoding='utf-8') as f:
    intact_pinyin_set = set(s for s in f.read().split('\n'))

# 生成带残缺部分的拼音, 例如 'ruan' 对应的 'r', 'ru' 和 'rua', 共 504 个, 对应的拼音表为 data/all_pinyin.txt
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
    
    return: 拼音划分结果列表, 例如 `cut_pinyin('kongjian', True)`, 
            会返回 `[('kong', 'jian'), ('kong', 'ji', 'an')]`
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
```

在 `cut_pinyin` 函数的基础上，我们可以加入拼音纠错功能，从第二个字母开始依次交换连续的两个字母，看看是否能够进行完整拼音划分，能的话就加入最终结果，进而实现纠错功能。

```python
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
        # 避免交换分词符
        if pinyin[i] == '\'' or pinyin[i + 1] == ' ':
            continue
        key = pinyin[:i] + pinyin[i + 1] + pinyin[i] + pinyin[i + 2:]
        value = cut_pinyin(key, is_intact=True)
        if value:
            ans[key] = value
    ans['all'] = [p for t in ans.values() for p in t]
    return ans
```

最后加入去尾字母划分功能，最后聚合一下，就实现了全部的输入拼音序列划分功能。

```python
def cut_pinyin_with_strategy(pinyin: str):
    '''
    使用各种策略对拼音进行划分, 其中包括:
    1. 完整划分
    2. 去尾字母完整划分
    3. 纠错划分
    4. 去尾字母纠错划分
    5. 模糊划分
    6. 结果综合

    pinyin: 待划分的拼音
    '''
    ans = {
        'intact': cut_pinyin(pinyin, is_intact=True),
        'intact_tail': [] if pinyin[-1] not in all_pinyin_set else [t + (pinyin[-1],) for t in cut_pinyin(pinyin[:-1], is_intact=True)],
        'error_correction': cut_pinyin_with_error_correction(pinyin)['all'],
        'error_correction_tail': [] if pinyin[-1] not in all_pinyin_set else [t + (pinyin[-1],) for t in cut_pinyin_with_error_correction(pinyin[:-1])['all']],
        'fuzzy': cut_pinyin(pinyin, is_intact=False),
        'combine': [],
    }
    ans['combine'] = set(ans['intact'] + ans['intact_tail'] + ans['error_correction'] + ans['error_correction_tail'] + ans['fuzzy'])
    return ans
```

顺带一提，很多人误认为「略」的拼音是 `lue`，实际上应该是 `lve`，因此我们需要对拼音进行规范化：

```python
def normlize_pinyin(pinyin: str):
    """
    规范化拼音
    将所有 ue 转化为 ve
    """
    return pinyin.replace('ue', 've', -1)
```

其次是文字转拼音后划分, 这时候拼音划分是已知的, 所以只需进行简写处理, 然后给不同简化方式 **划分权重** 即可. 这一步需要在生成发射矩阵的时候设置.


## 三、获取语料

这里我们直接使用了「北京语言大学 BCC 语料库 http://bcc.blcu.edu.cn」的词频语料 `global_wordfreq.release.txt`，最终解释权归北语大数据与教育技术研究所所有。

其中的语料格式大致为：

```text
第	2002074595
的	943370349
了	255733044
在	197672850
是	171296602
我	169391220
~	44057380
非常	8056541
一直	8013106
不会	8010572
应该	8001472
```

即「词语 + 词频」的组合，不过注意到有一些非中文的词语，例如 `~	44057380`，因此我们需要进行过滤，最后再使用 Python 的生成器功能，我们就能解耦合地进行数据的读入，具体代码位于 `train/dataset.py`。

```python
def is_Chinese(word):
    '''
    判断一个字符串是否全由汉字组成, 用于过滤文本
    '''
    return all('\u4e00' <= ch <= '\u9fff' for ch in word)

def iter_word_and_freq():
    """
    词频数据集, 迭代地返回 (word, freq)
    """
    with open(words_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                word, frequency = line.split()
                # 进行过滤
                if is_Chinese(word):
                    yield word, int(frequency)
            except Exception as e:
                pass
```


## 四、隐马尔可夫模型

**隐马尔可夫模型** (Hidden Markov Model, HMM) 是一种统计模型，用来描述一个含有隐含未知参数的马尔可夫过程。

隐马尔可夫模型有两个关键的概念：**状态** (state) 和 **观测** (observation)。隐马尔可夫链随机生成的状态的序列，称为状态序列；每个状态生成一个观测，由此产生的随机的观测的序列，称为观测序列。序列的每一个位置又可以看作一个时刻。

![](images/2022-07-04-20-23-37.png)

对于拼音输入法来说，**状态就是一个个汉字**，**观测就是对应的拼音**。作为状态的汉字是不知道的，唯一知道的只有用户输入的观测，也就是拼音。

隐马尔可夫模型由初始状态概率向量 $\pi$、状态转移概率矩阵 $A$ 和观测概率矩阵（也称为发射矩阵）$B$ 决定。因此，隐马尔可夫模型 $\lambda$ 可以用三元组符号表示，即

$$
\lambda = (\pi, A, B)
$$

$\pi, A, B$ 称为隐马尔可夫模型三要素。

由定义可知，隐马尔可夫模型有两个重要的基本假设：

- **齐次马尔可夫性假设**：隐马尔可夫链在任意时刻 $t$ 的状态只依赖于前一时刻 $t-1$ 的状态，与其他时刻的状态及观测无关，也与时刻 $t$ 的数值无关。
- **观测独立性假设**：任意时刻的观测只与该时刻的状态有关，与其他观测及状态无关，也与时刻 $t$ 的数值无关。

要使用隐马尔可夫模型来实现智能拼音输入法，我们 **首先要通过语料生成对应的隐马尔可夫模型**。

要生成隐马尔可夫模型也十分简单，根据 **极大似然估计法** 的结果，我们只需要用 **频率** 代替 **概率** 即可，也就是要统计语料中的频率，从而生成 $(\pi, A, B)$。

对应的统计频率的代码相对简单，这里就不过多赘述，需要看的话可以看看 `train/train_hmm.py` 这个文件的代码。

不过值得一提的是，由于状态转移矩阵 $A$ 和发射矩阵 $B$ 都是稀疏矩阵，即大部分位置均为 $0$，如果用普通的保存方式会十分占据空间，因此我们使用 JSON 格式将 Python 的字典保存下来。后续使用的时候，只需要加载 JSON 文件，就能重新恢复为位于内存中的 Python 字典了。对应生成的 JSON 文件位于 `data/hmm_xxx.json`.

另外，由于后续概率计算数字可能越算越小，导致计算机无法计算，所以我们对所有概率都进行了自然对数运算处理。

生成的 `hmm_start.json` 的部分内容：

```json
{
    "一": -5.081293678906249,
    "丁": -9.192433659783104,
    "丂": -19.34085746030175,
    "七": -10.159009715890134,
    "丄": -16.747217610377284,
    "丅": -16.301496324358553,
    "丆": -19.25047339883348,
    "万": -8.7175005342102
}
```

生成的 `hmm_transition.json` 的部分内容：

```json
{
    "渗": {
        "入": -2.439070674759006,
        "出": -1.9373713062580147,
        "性": -4.919727895519666,
        "析": -5.954770052141584,
        "水": -3.190476888777123,
        "流": -3.756776835259451,
        "漏": -2.4294073791727087,
        "透": -0.5143045447650618,
    },
    "渚": {
        "乡": -4.32027991176323,
        "停": -6.5756121199067294,
        "公": -4.33654043263501,
        "山": -4.052965142135882,
        "文": -0.50469675623453,
        "村": -4.877881600326951,
        "港": -2.8828938894856275,
        "湖": -2.9667753734663296,
        "镇": -1.7247845019528727,
    }
}
```

生成的 `hmm_emission.json` 的部分内容：

```json
{
    "一": {
        "y": -0.9808292530117262,
        "yi": -0.4700036292457356
    },
    "模": {
        "m": -0.9808292530117262,
        "mo": -0.5430199262500778,
        "mu": -3.12336226291328
    }
}
```

训练完隐马尔可夫模型后，我们就要进行预测了。

隐马尔可夫模型的预测问题，也称为解码 (decoding) 问题，就是在已知隐马尔可夫模型 $\lambda=(\pi, A, B)$ 和观测序列 $O=(o_1, o_2, \cdots, o_{T})$ 的情况下，求使得观测序列条件概率 $P(I|O)$ 最大的状态序列 $I=(i_1, i_2, \cdots, i_{T})$. 即给定观测序列，求最有可能的状态序列。

这里我们使用维特比算法 (Viterbi algorithm) 来进行预测。

为了加速维特比算法, 我们要先通过倒查表的方式计算出 `reversed_emission_matrix` 和 `reversed_transition_matrix`.

```python
def gen_reversed_matrix(emission_matrix, transition_matrix):
    '''
    生成 emission_matrix 的倒查表, 即 reversed_emission_matrix[拼音] = {汉字: 概率}

    生成 transition_matrix 和 emission_matrix 的联合倒查表,
    即 reversed_transition_matrix[前一个汉字][拼音] = (后一个汉字, 最大概率)
    '''
    # 生成 emission_matrix 的倒查表, 即 reversed_emission_matrix[拼音] = {汉字: 概率}
    reversed_emission_matrix = {}
    for char in tqdm(emission_matrix):
        for pinyin, prob in emission_matrix[char].items():
            if pinyin not in reversed_emission_matrix:
                reversed_emission_matrix[pinyin] = {}
            reversed_emission_matrix[pinyin][char] = prob
    json2file(reversed_emission_matrix, hmm_reversed_emission_path)

    # 生成 transition_matrix 和 emission_matrix 的联合倒查表,
    # 即 reversed_transition_matrix[前一个汉字][拼音] = (后一个汉字, 最大概率)
    reversed_transition_matrix = {}
    for previous in tqdm(transition_matrix):
        reversed_transition_matrix[previous] = {}
        for behind in transition_matrix[previous]:
            for pinyin in emission_matrix[behind]:
                prob = transition_matrix[previous][behind] + emission_matrix[behind][pinyin]
                if pinyin not in reversed_transition_matrix[previous]:
                    reversed_transition_matrix[previous][pinyin] = (behind, prob)
                elif prob > reversed_transition_matrix[previous][pinyin][1]:
                    reversed_transition_matrix[previous][pinyin] = (behind, prob)
    json2file(reversed_transition_matrix, hmm_reversed_transition_path)
```

然后是维特比算法的具体代码:

```python
def viterbi(pinyin, limit=10):
    """
    viterbi 算法

    pinyin: 拼音元组, 例如 ('jin', 'tian')

    return: 返回 limit 个最可能的汉字序列, 但是是 1 个全局最优解和 limit - 1 个局部最优解
            并且返回剩余未搜索的拼音
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
            if previous in reversed_transition_matrix and py in reversed_transition_matrix[previous]:
                state, new_prob = reversed_transition_matrix[previous][py]
                prob_map[phrase + state] = new_prob + prob

        if prob_map:
            V = prob_map
        else:
            # 没有概率, 因此没有完全搜索, 返回目前结果和未搜索拼音 pinyin[i:]
            return sorted(V.items(), key=lambda x: x[1], reverse=True), pinyin[i:]
    return sorted(V.items(), key=lambda x: x[1], reverse=True), ''
```

最后综合我们的分词功能和维特比算法，即可得到一个较为智能的输入法了。

```python
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
```


