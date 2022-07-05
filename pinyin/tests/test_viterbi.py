from pinyin.hmm import viterbi

def test_viterbi():
    assert viterbi(('jin', 'tian', 'tian', 'qi', 'bu', 'cuo'))[0][0][0] == '今天天气不错'
    assert viterbi(('ni', 'h'))[0][0][0] == '你好'