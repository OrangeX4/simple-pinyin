# -*- coding=utf8 -*-

'''
命令行接口
'''
import sys
sys.path.append('../')

from pinyin.cut import cut_pinyin

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
        # TODO: 拼音输入法
        mode = 'select'
    elif mode == 'cut':
        # 如果是拼音划分模式, 则读取拼音内容, 进行处理
        print('已进入拼音划分模式, 输入 change 切换划分方式, 输入 exit 退出')
        is_intact = True
        while True:
            pinyin = input('输入拼音: ')
            if pinyin == 'exit':
                mode = 'select'
                break
            elif pinyin == 'change':
                is_intact = not is_intact
                print(f'当前划分方式: {"精确" if is_intact else "模糊"}')
            else:
                # 输出拼音划分结果
                print('划分结果: ' + str(['\''.join(t) for t in cut_pinyin(pinyin, is_intact)]))
    elif mode == 'exit':
        print('退出程序')
        break
    else:
        print('未知模式')
        break