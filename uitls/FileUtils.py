def replace_illegal_chars(s):
    illegal_chars = '<>:"/\|?*'
    for char in illegal_chars:
        s = s.replace(char, '.')
    return s
