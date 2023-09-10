def replace_illegal_chars(s):
    illegal_chars = '<>:"/\|?*'
    for char in illegal_chars:
        s = s.replace(char, '.')
    return s


def redlines(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    # 去除每行末尾的换行符
    lines = [line.strip() for line in lines]
    return lines
