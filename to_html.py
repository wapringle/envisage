from browser import bind, window, document, html, alert, ajax, markdown
from browser.html import *
import time

def px(x):
    return str(x) + "px"

def kv(a):
    return a[0]
def ss(lst):
    return sorted(lst, key=lambda a: a[0])
def get_cols(json_data):
    res =set( [ k1  for (k, v) in ss(json_data.items()) for (k1, v1) in ss(v.items())])
    return sorted(res)

def make_row(item, row, columns):
    def rc(row1, columns):
        for c in columns:
            if c in row1:
                #print(item, c, row1[c])
                yield TD(row1[c])
            else:
                yield TD("--")
    tr = TR()
    tr <= TD(item)
    for td in rc(row, columns):
        tr <= td
    return tr
        
    
    
def init(json_data, config):
    
    head = document["head"]
    try:

        play_height = window.innerHeight - head.height - 50
    except:

        play_height = 0
        
    columns = get_cols(json_data)
    
    decade_data = {}
    table = TABLE(Class="dump")
    tr = TR()
    tr <= TH(" ", Class="dump")
    table <= tr
    for c in columns:
        tr <= TH(c, Class="dump")
    for item in sorted(json_data.keys()):
        table <= make_row(item, json_data[item], columns)
    return DIV(table, style={"overflow": "scroll", "background-color": "white", "width": "100%","height": px(play_height),})
            

def readme():
    head = document["head"]
    try:

        play_height = window.innerHeight - head.height - 50
    except:

        play_height = 0
    fname = "readme.html"

    fake_qs = '?foo=%s' %time.time()
    value = open(fname+fake_qs).read()    
    div = DIV(style={"overflow": "scroll", "background-color": "white", "width": "100%","height": px(play_height),})
    div.html = value
    return div


