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
from browser import bind, window, document, html, alert, ajax
from browser.html import *
from json import load, loads, JSONDecodeError, dumps
import javascript

from urllib.parse import urlparse, parse_qs

import topten, compare, parent

def px(x):
    return str(x) + "px"

json_data=None


config = {
    "slot_count": 10, 
    "paragraph1": "paragraph1", 
    "paragraph2": "paragraph2", 

}

def mangle(text):
    if False:
        return text
    r = ''
    for x in str(text): r += chr(ord(x) ^ 5)
    return r

def parse_url():
    url = document.URL
    pr = urlparse(url)
    gets = parse_qs(pr.query)
    return url, gets
    
def message_handler():
    global json_data
    """
    def receive_message(event):
        #alert('Received message: ' + event.data)
        return
        
        
    window.bind('message', receive_message)
    if window.parent == window.self:
        print("NO")
        return False
    print("YES")
    return True
    """
    while window.syncFlag != 2:
        alert(window.syncFlag)
    data_buffer = document["data_buffer"]
    json_data = loads(data_buffer.text)
    print(json_data.keys())
    
    
def getfile(input_data=None):
    global json_data, url
    wrapper = DIV(id="wrapper", style={"width": "100%", "height":"96vh"});
    wrapper <= DIV(
        DIV(H1("Data Visualisation")) + 
        INPUT(type="file", id="rtfile1", accept="*.json") +
        BUTTON("Top Ten",id="topten_button",disabled=True) + 
        BUTTON("Compare",id="compare_button",disabled=False) + 
        BUTTON("Make URL",id="make_url_button",disabled=True) + 
        BUTTON("Make Download",id="make_download_button",disabled=True),
        
        Class="background header", style={'height': "20%", 'xwidth': '100%'}, 
        id="head"
        )
    
    
    """
    document <= DIV(head, Class="background")
    
    play_height = window.innerHeight - head.height - 50
    
    """
    
    body = DIV(DIV(id="body",  Class="background"), style={"height": "75%", "xwidth": "95%",}, Class="background", id="body_wrapper" )
    
    wrapper <= body
    
    document <= wrapper
    
    load_btn = document["rtfile1"]
    topten_button = document["topten_button"]
    compare_button = document["compare_button"]
    make_url_button = document["make_url_button"]
    make_download_button = document["make_download_button"]
    
    all_buttons = {topten_button, compare_button, make_url_button, make_download_button}
    def enable(*button_list):
        for b in all_buttons:
            b.disabled = b not in button_list
        return
    def disable(*button_list):
        for b in all_buttons:
            b.disabled = b in button_list
        return
        
    def whenPossible(fun):
        topten.whenever(topten.all_clear, True, fun)
        
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
                disable()
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
        disable(topten_button)
        topten.init(json_data, config)
        
    @bind(compare_button, "click")
    def on_compare_click(ev):
        body = document["body_wrapper"]
        def fun():
            body.clear()
            disable()
            compare.init(json_data, config)
        whenPossible(fun)

    @bind(make_url_button, "click")
    def on_make_url_button(ev):
        body = document["body_wrapper"]
        body.clear()
        #make_url.init(url, json_data, config)
        
        content = window.encodeURIComponent(mangle(dumps(json_data)))
        result = f'{url}?input={content}'
        document["body_wrapper"] <= DIV(
            DIV(
                DIV(LABEL("Cut and paste this url", For="rt1"))+ 
                DIV(TEXTAREA(result, id="rt1", rows="80", cols="80", autocomplete="off", readonly=True)), 
            Class="Body",
            style={"margin": "auto"}
            ), 
            
        Class="border_bottom"
        )

    @bind(make_download_button, "click")
    def on_make_download_button(ev):
        body = document["body_wrapper"]
        body.clear()
        disable()
        parent.init(json_data, config)


    #bind(save_btn, "mousedown")
    def mousedown(evt):
        """Create a "data URI" to set the downloaded file content
        Cf. https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs
        """
        save_btn = document["save_file"]
        content = window.encodeURIComponent(document['rt1'].value)
        # set attribute "href" of save link
        save_btn.attrs["href"] = "data:text/plain," + content
        return
    
    if input_data != None:
        json_data = javascript.JSON.parse(input_data)
        #print(json_data)
        disable()
        on_topten_click(None)
        return
    
    url, gets = parse_url()
    if gets != {}:
        
        def read(req):
            global json_data
            print(req.json)
            json_data = req.json
            enable(compare_button)
            on_topten_click(None)
        
               
        if "input" in gets:
            print(gets['input'][0])
            json_data = loads(mangle(gets["input"][0]))
        elif "file" in gets:
            try:
                print(gets["file"])
                ajax.get(gets["file"][0], mode="json", oncomplete=read)
                return
            except:
                alert("Load error", gets["file"])
                return
        enable(compare_button)
        on_topten_click(None)
        return


    
        
