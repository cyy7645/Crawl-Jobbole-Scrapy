#-*- coding:utf-8 -*-
# author:cyy7645
# datetime:2019-03-09 15:44
# software: PyCharm

import hashlib

# zip urls to fixed length by md5 algorithms
def get_md5(url):
    if isinstance(url, str):
        # string is unicode in python3, convert it to utf-8
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()