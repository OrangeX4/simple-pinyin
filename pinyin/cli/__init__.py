# -*- coding=utf8 -*-

'''
命令行接口
'''
import sys
sys.path.append('../')
from pinyin.cut import cut_pinyin, cut_pinyin_with_error_correction
from pinyin.ime import ime


def main():
    # 拼音输入法的 cli
    # 模式: select, cut, pinyin
    mode_list = ['pinyin', 'cut', 'exit']
    desc_list = ['拼音输入法', '拼音划分', '退出']
    mode = 'select'

    while True:
        print('-----------------------------------------------------')
        if mode == 'select':
            # 如果是选择模式, 则显示选择列表, 并且接受用户输入
            print('请选择一种模式:')
            for i in range(len(mode_list)):
                print(f'{i}. {mode_list[i]}: {desc_list[i]}')
            try:
                select_index = int(input('请输入序号: '))
            except ValueError:
                print('输入错误, 请重新输入')
                continue
            if select_index < 0 or select_index >= len(mode_list):
                print('输入错误, 请重新输入')
                continue
            mode = mode_list[select_index]
        elif mode == 'pinyin':
            print('已进入智能拼音输入法模式, 输入 exit 退出')
            while True:
                pinyin = input('请输入拼音: ')
                if pinyin == 'exit':
                    mode = 'select'
                    break
                for t in ime(pinyin, 3):
                    print(f"{t[1]} ({'-'.join(t[0])}): {t[2]}")
        elif mode == 'cut':
            # 如果是拼音划分模式, 则读取拼音内容, 进行处理
            print('已进入拼音划分模式, 输入 change 切换划分方式, 输入 exit 退出')
            cut_mode = '精确'
            while True:
                pinyin = input('输入拼音: ')
                if pinyin == 'exit':
                    mode = 'select'
                    break
                elif pinyin == 'change':
                    if cut_mode == '精确':
                        cut_mode = '模糊'
                    elif cut_mode == '模糊':
                        cut_mode = '纠错'
                    else:
                        cut_mode = '精确'
                    print(f'当前划分方式: {cut_mode}')
                else:
                    # 输出拼音划分结果
                    if cut_mode == '精确':
                        print('划分结果: ' + str(['\''.join(t)
                            for t in cut_pinyin(pinyin, is_intact=True)]))
                    elif cut_mode == '模糊':
                        print('划分结果: ' + str(['\''.join(t)
                            for t in cut_pinyin(pinyin, is_intact=False)]))
                    else:
                        print('划分结果:')
                        for k, v in cut_pinyin_with_error_correction(pinyin).items():
                            print(k + ': ' + str(['\''.join(t) for t in v]))
        elif mode == 'exit':
            print('退出程序')
            break
        else:
            print('未知模式')
            break


if __name__ == '__main__':
    main()
