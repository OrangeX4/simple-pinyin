# -*- coding=utf8 -*-

'''
简易拼音输入法
'''

import sys
sys.path.append('../')


def main():
    mode = input('选择命令行模式或服务器模式 (cli / server): ')
    if mode == 'cli':
        from pinyin.cli import main as cli_main
        cli_main()
    elif mode == 'server':
        from pinyin.server import main as server_main
        server_main()
    else:
        print('未知模式')


if __name__ == '__main__':
    main()
