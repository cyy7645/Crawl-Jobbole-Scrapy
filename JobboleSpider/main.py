#-*- coding:utf-8 -*-
# author:cyy7645
# datetime:2019-03-09 14:57
# software: PyCharm

# for debug

from scrapy.cmdline import execute

import sys
import os

# print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
execute(["scrapy","crawl","jobbole"])