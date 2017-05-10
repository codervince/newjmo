from datetime import datetime, date
import re
import csv
import logging
import unicodedata
from urllib.parse import urljoin
import pprint
from collections import *
import operator

def clean_prizemoney(prizemoney):
    return float(''.join(re.findall("[-+]?\d+[\.]?\d*", prizemoney)))

def try_int(value):
    try:
        return int(value)
    except:
        return 0

def get_sec(s):
    l = s.split('.')
    if len(l)==3:
        return int(l[0]) * 60 + int(l[1]) * 1 + int(l[2]) * 0.01

def get_prio_val(str):
    if type(str) != type([]):
        return try_int(str)
    if str is None:
        return []
    return [int(s) for s in str.split() if s.isdigit()][0]


def cleanescapes(s):
    s = s.replace(u'\r', u'')
    s = s.replace(u'\t', u'')
    s = s.replace(u'\n', u'')
    s = s.replace(u' ', u'')
    return s
'''
use cases: u'\r\n2\r\n\t\t\t\t\t'
also remove '\xa0'
'''
def cleanstring(s):
    # s = unicode(s)
    r = unicodedata.normalize('NFD', s)
    r = r.encode('ascii', 'ignore').decode('ascii')
    r = cleanescapes(r)
    r = r.replace(u'\xa0',u'')
    pattern = re.compile(r'\s+')
    return re.sub(pattern, u' ',r)

def tf(values, encoding="utf-8"):
    value = ""
    for v in values:
        if v is not None and v != "":
            value = v
            break
    return value.encode(encoding).strip()
