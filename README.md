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
    5. 结果综合 (不含模糊划分)
    6. 模糊划分

    pinyin: 待划分的拼音
    '''
    ans = {
        'intact': cut_pinyin(pinyin, is_intact=True),
        'intact_tail': [] if pinyin[-1] not in all_pinyin_set 
            else [t + (pinyin[-1],) for t in cut_pinyin(pinyin[:-1], is_intact=True)],
        'error_correction': cut_pinyin_with_error_correction(pinyin)['all'],
        'error_correction_tail': [] if pinyin[-1] not in all_pinyin_set 
            else [t + (pinyin[-1],) for t in cut_pinyin_with_error_correction(pinyin[:-1])['all']],
        'combine': [],
        'fuzzy': cut_pinyin(pinyin, is_intact=False)
    }
    ans['combine'] = ans['intact'] + ans['intact_tail'] 
        + ans['error_correction'] + ans['error_correction_tail']
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



## 四、训练隐马尔可夫模型

由于训练集十分庞大，因此我们可以直接使用频率当作概率使用。
