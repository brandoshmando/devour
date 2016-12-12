import ujson
import simplejson
import json
import cjson
import time

def test(input):
    types = {
        json: ['dumps','loads'],
        ujson: ['dumps','loads'],
        simplejson: ['dumps','loads'],
        cjson: ['encode', 'decode']
    }
    dumps_ret = []
    loads_ret = []
    for key,val in types.items():
        for i,v in enumerate(val):
            if i == 0:
                lstart = time.time()
                loaded = getattr(key, v)(input)
                lend = time.time()
                loads_ret.append("%s: %s" % (key.__name__, str(lend-lstart)))
            if i == 1:
                dstart = time.time()
                loaded = getattr(key, v)(input)
                dend = time.time()
                dumps_ret.append("%s: %s" % (key.__name__, str(dend-dstart)))
    for item in dumps_ret:
        print item
    for item in loads_ret:
        print item
