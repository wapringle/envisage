"""
MIT License

Copyright (c) 2024 William A Pringle

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from browser import bind, window, document, html, alert
from browser.html import *
from json import loads, JSONDecodeError, dumps

from urllib.parse import urlparse, parse_qs

import topten, compare

def px(x):
    return str(x) + "px"

json_data=None

head = DIV(
    DIV(H1("Data Visualisation")) + 
    INPUT(type="file", id="rtfile1") +
    BUTTON("Top Ten",id="topten_button",disabled=True) + 
    BUTTON("Compare",id="compare_button",disabled=True) + 
    BUTTON("Make URL",id="make_url_button",disabled=True), 
    Class="header", 
    id="head"
    )


document <= DIV(head, Class="background")

play_height = window.innerHeight - head.height - 50

body = DIV(DIV(id="body", style={"height": px(play_height)}, Class="background"), id="body_wrapper" )

document <= body

config = {
    "slot_count": 10, 
    "paragraph1": "paragraph1", 
    "paragraph2": "paragraph2", 

}

def mangle(text):
    r = ''
    for x in str(text): r += chr(ord(x) ^ 4)
    return r

def parse_url():
    url = document.URL
    pr = urlparse(url)
    gets = parse_qs(pr.query)
    return url, gets
    
def getfile():
    global json_data, url
    load_btn = document["rtfile1"]
    topten_button = document["topten_button"]
    compare_button = document["compare_button"]
    make_url_button = document["make_url_button"]
    
    url, gets = parse_url()
    if gets != {}:
        print(gets['input'][0])
        json_data = loads(mangle(gets["input"][0]))
        print(json_data)
        topten_button.disabled = False
        compare_button.disabled = False
        load_btn.disabled = True



    @bind(load_btn, "input")
    def file_read(ev):
        filename = None
    
        def onload(event):
            global json_data
            """Triggered when file is read. The FileReader instance is  event.target.
            The file content, as text, is the FileReader instance's "result"    
            attribute."""
            
            #alert("Failed to load json file " + load_btn.files[0] )
            try:
                json_data = loads(event.target.result)
                topten_button.disabled = False
                compare_button.disabled = False
                make_url_button.disabled = False
            except JSONDecodeError as e:
                alert(e)
            except Exception as e:
                alert(e)
                
            """
            gotjson(json_data, config)
            document['rt1'].value = event.target.result
            # display "save" button
            save_btn.style.display = "inline"
            # set attribute "download" to file name
            save_btn.attrs["download"] = file.name
            """
            
        # Get the selected file as a DOM File object
        file = load_btn.files[0]
        # Create a new DOM FileReader instance
        reader = window.FileReader.new()
        # Read the file content as text
        filename = file
        reader.readAsText(file)
        reader.bind("load", onload)
    
    
    @bind(topten_button, "click")
    def on_topten_click(ev):
        body = document["body_wrapper"]
        body.clear()
        topten.init(json_data, config)
        
    @bind(compare_button, "click")
    def on_compare_click(ev):
        body = document["body_wrapper"]
        body.clear()
        compare.init(json_data, config)

    @bind(make_url_button, "click")
    def on_make_url_button(ev):
        body = document["body_wrapper"]
        body.clear()
        #make_url.init(url, json_data, config)
        
        content = window.encodeURIComponent(mangle(dumps(json_data)))
        result = f'{url}?input={content}'
        document["body_wrapper"] <= DIV(
            DIV(
                LABEL("Cut and paste this url", For="rt1") + 
                TEXTAREA(result, id="rt1", rows="20", cols="80", autocomplete="off", readonly=True), 
            Class="Body",
            style={'height': px(play_height)}
            ), 
            
        Class="border_bottom"
        )


    #bind(save_btn, "mousedown")
    def mousedown(evt):
        """Create a "data URI" to set the downloaded file content
        Cf. https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs
        """
        save_btn = document["save_file"]
        content = window.encodeURIComponent(document['rt1'].value)
        # set attribute "href" of save link
        save_btn.attrs["href"] = "data:text/plain," + content
        
