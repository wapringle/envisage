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
import copy

from browser import document, html, alert, window
from browser.html import * 
from browser.widgets.dialog import InfoDialog
#from aq_data import decade_index, decade_data

import brycharts

testing = False

def px(x):
    return str(x) + "px"

def TRTD(*args,**kwargs):
    return TR(TD(*args, **kwargs))

def init(json_data, config):
    global decade_data
    """
    Present list of cities.
    Select up to 3 and show in separate list - chosen
    Go button when  done
    Cant select city if in chosen list
    Cant select city if chosen full
    Cant press go button if chosen empty
    City can be deleted from chosen list
    """
    choices = ["one","two","three","four","five", "six", "seven"]
    
    decade_data = {}
    city_list = SELECT(id="city_list", size=10, multiple=True, Class="select_list")
    for item in sorted(json_data.keys()):
        decade_data[item] = {}
        city_list <= OPTION(item)
        for x in sorted(json_data[item].keys()):
            try:
                decade_data[item][x] = float(json_data[item][x])
            except:
                pass #ignore bad data or None
    """
    for x in json_data.keys():
        for y in x.keys():
            json_data[x][y] = float(json_data[x][y])
    decade_data = copy.copy(json_data)
    """    
    #print(decade_data)
        
    select = BUTTON("+", disabled=True, Class="selector")
    
    chosen = SELECT(size=4, Class="select_list")
    
    remove = BUTTON("-", disabled=True, Class="selector")
    
    go = BUTTON("Compare", disabled=not testing, Class="selector")
    

    def layout():
        paragraph1 = """
Data is the concentration of particulate matter (e.g. soot particles) extracted from the UK Earth System  Model and averaged per decade. 
"""

        inner = DIV(
            select+
            remove
        )
        main= DIV(SPAN("Graph"), style={"width": "100%", "height": "10%"} ) + DIV(
            DIV(
                SVG(style={"width": "95%", "height": "85%", "background-color": "white",}),
                Class="chart"
            ), 
            id="chartarea",style={"width": "100%", "height": "90%"})  

        document["body_wrapper"].clear()
        
        document["body_wrapper"] <= DIV(
            
            TABLE(
                TR(
                    TD(
                        SPAN("Items to Compare") +
                        DIV(city_list, id="city_list")+
                        DIV(inner) + 
                        DIV("Selected Items") +
                        DIV(chosen) + DIV(go),
                        Class="td_left"
                    ) +
                    TD(main, Class="td_right")
                    ),
                Class="body"
                ),
            Class="border_bottom"
            )

    def already_chosen():
        chosen_values = [v.value for v in chosen.options]
        candidate = city_list.selectedIndex
        item = city_list.options[candidate].value
        
        print(item,  chosen_values)
        return item in  chosen_values
        
    def on_select_click(ev):
        if already_chosen():
            return
        
        dropdown = ev.target
        num = city_list.selectedIndex
        item = city_list.options[num].value
        chosen <= OPTION(item)
        go.disabled = False
        select.disabled = True
    
    def on_remove_click(ev):
        dropdown = ev.target
        
        selected = [(i, option.value) for i, option in enumerate(chosen) if option.selected]
        for (num, item) in reversed(selected):
            
            chosen.remove(num)
        if len(chosen.options) == 0:
            go.disabled = True
        remove.disabled = True
        
    def on_city_list_change(ev):
        select.disabled = (already_chosen() or len(chosen.options) >=4) 

    def on_chosen_change(ev):
        remove.disabled = False
        
    def on_go_click(ev):
        """
        print(len(document.getElementsByClassName("chart")))
        for div in document.getElementsByClassName("chart"):
            print("removing", div)
            div.remove()
        """
            
        chartarea = document["chartarea"]
        chartarea.clear()

        chart2 = DIV(Class="chart", style={"width": "100%", "height": px(window.innerHeight *2 /3)})   
        document["chartarea"] <= chart2
        
        if not testing:
            chosen_values = [v.value for v in chosen.options]
            fields = chosen_values
            title = "Comparison between " + '; '.join(fields)
            if False:
                
                # for some strange reason, this doesnt order items in proper date order
                data = dict([(k, decade_data[k]) for k in chosen_values ])
                  
                print(data)
                ldd = brycharts.LabelledDataDict(data, "Particulate Concentration")
                brycharts.GroupedBarChart(chart2, ldd, title, direction="vertical", height="45%")
                #brycharts.GroupedBarChart(document, ldd, title, direction="vertical", height="45%")
            else:
                data = dict([(k, decade_data[k]) for k in chosen_values ])
                res = {}
                for team in data:
                    res[team] = [( int(k), float(v)) for k, v in data[team].items()]
                data = res
                
                paireddatadict = brycharts.PairedDataDict("Year", "Title", data)
                brycharts.LineGraph(chart2, paireddatadict, title)            
            
        else:
            
            
            livingcostdata = {'Cost of Living Index': {'Adelaide': 86.02, 'Athens': 64.67, 'Hong Kong': 78.72, 'Nairobi': 42.06, 'Rio De Janeiro': 57.14, 'San Francisco': 97.84}, 'Rent Index': {'Adelaide': 36.56, 'Athens': 13.97, 'Hong Kong': 79.54, 'Nairobi': 12.27, 'Rio De Janeiro': 21.61, 'San Francisco': 115.36}}              
            data = {'Beijing, China': {'185': 9.995012560808409, '186': 9.684169062767799, '187': 9.527474806309987, '188': 9.714275055322798, '189': 9.979191312496239, '190': 10.177958068932714, '191': 11.031791079141199, '192': 11.509275657221055, '193': 11.941068405106662, '194': 12.114836913552136, '195': 16.172985960357515, '196': 20.692509427692123, '197': 25.700616795911138, '198': 35.253043300417566, '199': 43.20706760305601, '200': 55.58410470065227, '201': 69.20189618388066}, 'London, United Kingdom': {'185': 7.85060554803318, '186': 9.134226935862253, '187': 9.912712084762754, '188': 10.752737952060066, '189': 11.495180835625778, '190': 12.447836011815816, '191': 12.899655091909693, '192': 11.631724848687648, '193': 12.18617366203635, '194': 12.079535494446134, '195': 13.198102365141427, '196': 12.250948169676278, '197': 8.238790169622593, '198': 7.057462987826206, '199': 5.696491046180793, '200': 4.3652121481206265, '201': 3.985589388189527}}
            fields = ['Beijing, China', 'ZZZ']
            
            data={'Liverpool': {'2011': 58.0, '2012': 52.0, '2013': 61.0, '2014': 84.0, '2015': 62.0, '2016': 60.0, '2017': 76.0, '2018': 75.0, '2019': 97.0, '2020': 99.0, '2021': 69.0, '2022': 92.0}}
            fields = ['Liverpool']
            
            res = {}
            for team in data:
                res[team] = [( int(k), float(v)) for k, v in data[team].items()]
            data = res
            
            title = "Change in rental costs over a 10 year period"
            paireddatadict = brycharts.PairedDataDict("Year", "Monthly rent (€)", data)
            brycharts.LineGraph(chart2, paireddatadict, title)            
      
    layout()

    city_list.bind("change", on_city_list_change )
    chosen.bind("change", on_chosen_change)
    select.bind("click", on_select_click)
    remove.bind("click", on_remove_click)
    
        
    go.bind("click", on_go_click)
        
    
#init()    