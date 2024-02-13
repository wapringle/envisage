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
from browser import bind, window, document, html, alert, ajax, markdown, timer
from browser.html import *
from json import load, loads, JSONDecodeError, dumps
import javascript

from urllib.parse import urlparse, parse_qs

import topten, compare, parent, to_html

def px(x):
    return str(x) + "px"

json_data=None
cookie = None   
evx = 0
evy = 0

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
    return url.split("?")[0], gets
    
def message_handler():
    global json_data
    while window.syncFlag != 2:
        alert(window.syncFlag)
    data_buffer = document["data_buffer"]
    json_data = loads(data_buffer.text)
    #print(json_data.keys())
    
def report_error(*args):
    alert(*args)
    
def getfile(input_data=None):
    
    def validate_json_format(j_data):
        validate_python_format(j_data, False)
        
    def validate_python_format(data, python_format=True):
        global json_data, max_value
        
        try:
            if not python_format:
                json_data = loads(data)
            else:
                json_data = data
            if not isinstance(json_data, dict):
                raise TypeError("json structure is not a dictionary")
            if len(json_data) == 0:
                raise TypeError("json struct is empty")
            for k, v in json_data.items():
                if not isinstance(v, dict):
                    raise TypeError(f"row {k} is not a dictionary")
                for k1, v1 in list(v.items()):
                    try:
                        k1f = float(k1)
                        v1f = float(v1)
                    except:
                        #silently delete non numeric items
                        del v[k1]
                        #raise TypeError(f"item {k1},{v1} in row {k} cannot be converted to float")

                          
            max_value = max( v for _, k in json_data.items() for _, v in k.items())
            disable()
            on_topten_click(None)
        except JSONDecodeError as e:
            report_error(e)
        except TypeError as e:
            report_error(e)
        except Exception as e:
            report_error(e)
    
    global json_data, url
    wrapper = DIV(id="wrapper", style={"width": "100%", "height":"96vh"});
    wrapper <= DIV(
        DIV(H1("Envisage Data Visualisation")) + 
        INPUT(type="file", id="rtfile1", accept="*.json") +
        BUTTON("Top Ten",id="topten_button",disabled=True) + 
        BUTTON("Compare",id="compare_button",disabled=True) + 
        BUTTON("Raw Data",id="raw_button",disabled=True) + 
        BUTTON("Make URL",id="make_url_button",disabled=True) + 
        BUTTON("Make Wrapper",id="make_download_button",disabled=True) +
        BUTTON("Export Dataset",id="export_dataset_button",disabled=True) +
        BUTTON("About",id="about_button",disabled=False),
        
        Class="background header", style={'height': "20%", 'xwidth': '100%'}, 
        id="head"
        )
    

    
    body = DIV(DIV(id="body",  Class="background"), style={"height": "75%", "xwidth": "95%",}, Class="background", id="body_wrapper" )
    
    wrapper <= body
    
    document <= wrapper
    
    load_btn = document["rtfile1"]
    topten_button = document["topten_button"]
    compare_button = document["compare_button"]
    raw_button = document["raw_button"]
        
    make_url_button = document["make_url_button"]
    make_download_button = document["make_download_button"]
    export_dataset_button =  document["export_dataset_button"]
    about_button = document["about_button"]
    
    tooltip=DIV(SPAN("TT",id="tt_text",Class="tooltip"),Class="tooltip")
    document <=tooltip
    
    tooltips = {
        topten_button: "Animate the Top Ten entries through time",
        compare_button: "Compare selected entries",
        raw_button: "Display the  underlying dataset",
        make_url_button: "create URL for this dataset",
        make_download_button: "create webpage wrapper for dataset",
        export_dataset_button: "export dataset as json file",
        about_button: "About Envisage",
    }
    for k, v in tooltips.items():
        def mouse_move(ev):
            global cookie, evx, evy
            evx =ev.x
            evy = ev.y
            
        def mouse_in(ev):
            global cookie, evx, evy
            document["tt_text"].text=ev.target.tooltip
            tooltip.style.zindex=2
            def delayed(ev):
                tooltip.style.left=px(evx +7)
                tooltip.style.top=px(evy + 9)
                tooltip.style.visibility="visible"
            cookie = timer.set_timeout(delayed, 1000, ev)
                        
        def mouse_out(ev):
            global cookie
            timer.clear_timeout(cookie)
            tooltip.style.visibility="hidden"
            
        k.tooltip = v
        k.bind("mouseover", mouse_in)
        k.bind("mouseleave", mouse_out)
        k.bind("mousemove", mouse_move)
    
    all_buttons = {topten_button, compare_button, raw_button, make_url_button, make_download_button, export_dataset_button}
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
        
        def validate(data):
            if not isinstance(data, dict):
                raise TypeError("json structure is not a dictionary")
            for k, v in data.items():
                if not isinstance(v, dict):
                    raise TypeError(f"row {k} is not a dictionary")
                for k1, v1 in list(v.items()):
                    try:
                        k1f = float(k1)
                        v1f = float(v1)
                    except:
                        #silently delete non numeric items
                        del v[k1]                        
                        #raise TypeError(f"item {k1},{v1} in row {k} cannot be converted to float")
            return True
        
        filename = None
    
        def onload(event):
            global json_data
            """Triggered when file is read. The FileReader instance is  event.target.
            The file content, as text, is the FileReader instance's "result"    
            attribute."""
            
            validate_json_format(event.target.result)
            
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

    @bind(raw_button, "click")
    def on_raw_button(ev):
        body = document["body_wrapper"]
        #alert("click")
        def fun():
            body.clear()
            disable()
            body <= to_html.init(json_data, config)
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
            style={"margin": "auto",}
            ), 
            
        Class="border_bottom"
        )

    @bind(make_download_button, "click")
    def on_make_download_button(ev):
        body = document["body_wrapper"]
        body.clear()
        disable()
        parent.init(json_data, config)
        
        
    @bind(export_dataset_button, "click")
    def _(ev):
        body = document["body_wrapper"]
        body.clear()
        disable()
        parent.json_download(json_data, config)
        
    @bind(about_button, "click")
    def _(ev):
        body = document["body_wrapper"]
        body.clear()
        body <= to_html.readme()
        

        

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
    
    """ Finally get to process input line """
    
    
    if input_data != None:
        validate_json_format(input_data)
        return
    
    url, gets = parse_url()
    if gets != {}:
        
        def read(req):
            if req.json == None:
                report_error("Load error", gets["file"][0])
            else:
                validate_python_format(req.json)
               
        if "input" in gets:
            j_data = mangle(gets["input"][0])
            validate_json_format(j_data)
            return
            
        elif "file" in gets:
            try:
                #print(gets["file"])
                ajax.get(gets["file"][0], mode="json", oncomplete=read)
                return
            except:
                report_error("Load error", gets["file"][0])
                return
#        enable(compare_button)
#        on_topten_click(None)
        return


    
        
