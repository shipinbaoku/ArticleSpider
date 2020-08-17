import hashlib


def get_md5(string):
    """
    将不定长的字符串生成md5
    :param string:
    :return:
    """
    if isinstance(string, str):
        url = string.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()
