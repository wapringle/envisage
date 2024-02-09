import copy

from browser import document, html, alert, window, bind
from browser.html import * 
from browser.widgets.dialog import InfoDialog
import json

iframe="""
<!DOCTYPE html>
<html>
<head>
    <title>Envisage</title>
</head>
<body>
<script>
    const jbuf='{:s}';
    function receiveMessage(event) {{
        event.source.postMessage(jbuf,event.origin);
    }}
    window.addEventListener('message', receiveMessage, false);
    
</script>
<iframe id="if1" src='{:s}' style="border:none;width: 95%; height:95vh" title="Viz"></iframe>
</body>
</html>
"""

def json_download(json_data, config):
    txt = json.dumps(json_data)
    content = window.encodeURIComponent(txt)
    href = "data:text/json,"+content

    filename = INPUT("", id="filename") 
    download = A("download", id="download", download="", disabled=True)

    @bind(filename, "blur")
    def on_filename_blur(ev):
        if len(ev.target.value) > 0:
            fullname = filename.value + ".json"
            download.download = fullname
            download.text = "download " + fullname
            download.href = href
            download.disabled = False
        else:
            download.disabled = True

    @bind(filename, "focus")
    def on_filename_focus(ev):
        download.disabled = True
        

    print("Loading")
    document["body_wrapper"] <= DIV(
        DIV("Download", Class="border_bottom") + 
        DIV(
            SPAN("export json dataset json file") +
            DIV(SPAN("Filename") + filename +SPAN(".json"))+
            DIV(download), 
            style={"borderStyle": 'solid', "margin": "auto", "width": "fit-content",} 

        
        ), 
        
    Class="body border_bottom"
    )
    
#download("filename", "json_data", "url")

def init(json_data, config):
    url="https://wapringle.github.io/envisage/index.html"
    txt = iframe.format(json.dumps(json_data), url)
    content = window.encodeURIComponent(txt)
    href = "data:text/html,"+content

    filename = INPUT("", id="filename") 
    download = A("download", id="download", download="", disabled=True)

    @bind(filename, "blur")
    def on_filename_blur(ev):
        if len(ev.target.value) > 0:
            fullname = filename.value + ".html"
            download.download = fullname
            download.text = "download " + fullname
            download.href = href
            download.disabled = False
        else:
            download.disabled = True

    @bind(filename, "focus")
    def on_filename_focus(ev):
        download.disabled = True
        

    print("Loading")
    document["body_wrapper"] <= DIV(
        DIV("Download", Class="border_bottom") + 
        DIV(
            SPAN("download json dataset as a html file") +
            DIV(SPAN("Filename") + filename +SPAN(".html"))+
            DIV(download), 
            style={"borderStyle": 'solid', "margin": "auto", "width": "fit-content",} 

        
        ), 
        
    Class="body border_bottom"
    )
    
#download("filename", "json_data", "url")    