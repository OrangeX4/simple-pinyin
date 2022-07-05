import json

emoji_file_path = 'data/emoji.txt'
emoji_json_path = 'data/emoji.json'

def gen_emoji_json():
    emoji_dict = {}
    with open(emoji_file_path, 'r', encoding='utf-8') as f:
        emoji = ''
        for line in f:
            line = line.strip()
            # 跳过数字
            if all(ch in '1234567890' for ch in line):
                continue
            if emoji:
                # 去除前缀
                if line.startswith('旗: '):
                    line = line[3:]
                emoji_dict[line] = emoji
                emoji = ''
            else:
                emoji = line

    # save to data/emoji.json
    with open(emoji_json_path, 'w', encoding='utf-8') as f:
        json.dump(emoji_dict, f, ensure_ascii=False, indent=4)


def load_emoji_dict():
    return json.load(open(emoji_json_path, 'r', encoding='utf-8'))

    