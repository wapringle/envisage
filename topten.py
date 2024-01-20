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
import time
import copy

from dataclasses import dataclass, astuple
from browser import document, html, timer, window, alert, bind
from browser.html import *


top_ten_data = None
config = None

content_index = -1
previous_deck = None
current_stream = None
stop_flag = False
max_val = 100
rank_slots = []

def reset_globals():
    global top_ten_data, config, content_index, previous_deck, current_stream, stop_flag, max_val, rank_slots
    
    top_ten_data = None
    config = None
    
    content_index = -1
    previous_deck = None
    current_stream = None
    stop_flag = False
    max_val = 100
    rank_slots = []
    
    
@dataclass
class Base_Class():
    def name_str(self):
        pass
    def value_str(self):
        pass
    def bar_str(self):
        pass
    def make_html(self):
        return "".join([
            """<div class="header-container"><div class="card-header-text">""", 
            self.name_str(), 
            """</div><div class="card-header-text">""", 
            self.value_str(), 
            """</div><div class="card-header-text" style="width: """, 
            self.bar_str(), 
            """%; height: 50%;"><div class="bar"></div></div></div>"""
            ])

@dataclass
class PLdata(Base_Class):
    rank: int
    name: str
    key: str
    pts: int

    def name_str(self): return self.name
    def value_str(self): return str(self.pts)
    def bar_str(self):
        global max_val
        return f'{100 * float(self.pts) /max_val: 2.0f}'



    
@dataclass
class AQdata():
    key: str
    html: str
    
def make_rank(k):
    for r in topten[k]:
        q = PLdata(*r)
        yield astuple(AQdata(q.name, q.make_html()))
    
def make_it(top_ten_data):
    def make_league(year):
        i = 1
        for team,pts in sorted(filter(lambda a: a[1] != None, top_ten_data[year].items()), key=lambda a: float(a[1]), reverse=True):
            q = PLdata(i, team, team, pts)
            yield astuple(AQdata(q.name, q.make_html()))
            i += 1
            if i > 10:
                break
        # if too few, fill up with dummies
        while i <= 10:
            q = PLdata(i, f"-- {i}", f"-- {i}", 0)
            yield astuple(AQdata(q.name, q.make_html()))
            i += 1
            if i > 10:
                break
            
        

    return [(year, list(make_league(year))) for year in sorted(top_ten_data.keys()) ]

def transform(premier_league) :
    top_ten_data ={}
    for team, league in premier_league.items():
        for year, pts in league.items():
            if year not in top_ten_data:
                top_ten_data[year] = {}
            top_ten_data[year][team] = pts
    return make_it(top_ten_data)

    

def debug(*args):
    if True:
        print(*args)
    
def more_forwards():
    return content_index < len(top_ten_data) - 1

def more_backwards():
    return content_index > 0

def get_next_decade(forward=True):
    global content_date, content_deck, content_index, previous_deck

    if forward:
        if more_forwards():
            content_index += 1
        else:
            return False
    else:
        if more_backwards():
            content_index -= 1
        else:
            return False

    deck = top_ten_data[content_index]
    if previous_deck == None:
        previous_deck = copy.copy(deck[1])
    content_date = deck[0]
    content_deck = [AQContent(*p) for p in update(previous_deck, deck[1])]
    previous_deck = copy.copy(deck[1])
    return True


def update(old, new):
    def keys(l):
        return set(map(lambda a: a[0], l))

    olds = keys(old)
    news = keys(new)
    replacements = list(zip(news - olds, olds - news))
    debug(replacements)

    oldd = dict(((a[0], i) for i, a in enumerate(old)))
    for oldslot, newslot in replacements:
        oldd[oldslot] = oldd[newslot]
        
    ret = [(a[0], a[1], i, oldd[a[0]]) for i, a in enumerate(new)]
    return ret


def get_max_value():
    global top_ten_data
    for i in range(len(top_ten_data)):
        deck = top_ten_data[i]
        value = deck[1][0]
    return max(top_ten_data[i][1][0][1] for i in range(len(top_ten_data)))


def px(x):
    return str(x) + "px"


def init(init_top_ten_data, init_config):
    global top_ten_data, config, previous_deck, content_index, max_val
    
    reset_globals()
    
    top_ten_data = transform(init_top_ten_data)
    print(max_val)
    config = init_config

    get_next_decade()
    back_one = BUTTON("<", id="back_one", disabled=True, Class="selector")
    back_stream = BUTTON("<<", id="back_stream", disabled=True, Class="selector")

    forward_one = BUTTON(">", disabled=False, id="forward_one", Class="selector")
    forward_stream = BUTTON(">>", id="forward_stream", disabled=False, Class="selector")

    def sanity_check():
        # Either a button is active ore we'er waiting for a termination
        global stop_flag, current_stream
        if all_clear() and not current_stream:
            for e in [back_one, back_stream, forward_one, forward_stream]:
                if e.disabled == False:
                    return True
            #alert("consistency error")
            return False
        else:
            return True

    def disable_all():
        for e in [back_one, back_stream, forward_one, forward_stream]:
            e.disabled = True

    @bind(forward_one, "click")
    def on_forward_one_click(ev):
        disable_all()
        single_step(True)
        sanity_check()

    @bind(back_one, "click")
    def on_back_click(ev):
        disable_all()
        single_step(False)
        sanity_check()

    @bind(forward_stream, "click")
    def on_forward_stream_click(ev):
        disable_all()
        multi_step(ev, True)
        sanity_check()

    @bind(back_stream, "click")
    def on_back_stream_click(ev):
        disable_all()
        multi_step(ev, False)
        sanity_check()

    date_display = DIV(
        SPAN("Date", Class='control-text')
        + SPAN("8888", id='togo', Class='foreground') ,
        Class="Clock-Wrapper"
    )
    head = document["head"]
    debug(window.innerHeight, head.height)
    try:

        play_height = window.innerHeight - head.height - 50
    except:

        play_height = 0
        
    document["body_wrapper"].clear()

    document["body_wrapper"] <= DIV(
        TABLE(
            TR(
                TD(
                    DIV() + DIV(),
                    width="10%",
                    height=px(play_height),
                    style={"vertical-align": "baseline"}
                )
                    + TD(DIV(id="id_main", Class="play"), id="td_main", width="80%" , style={"vertical-align": "top", "background-color": "white", })
                + TD(
                        date_display +
                        DIV(back_stream + back_one + forward_one + forward_stream),
                        width="10%",
                        height=px(play_height),
                        style={"vertical-align": "baseline"}
                )
            ),
            id="body",

            Class="body"
        ),
        Class="border_bottom"
    )
    td_main = document['td_main']
    debug(td_main.width)

    init_rank_holder(document["id_main"], play_height, td_main.width)
    #arrangeCards()
    document['togo'].text = content_date

    xx = None

    @bind(".selector", "click")
    def on_click(ev):
        global xx
        xx = ev.currentTarget.id

    @bind(".selector", "mousedown")
    def on_mousedown(ev):
        ev.currentTarget.style["border-style"] = "inset"

    @bind(".selector", "mouseup")
    def on_mouseup(ev):
        ev.currentTarget.style["border-style"] = "outset"


def init_rank_holder(main, play_height, width):
    global rank_slots
    slot_count = config["slot_count"]
    slot_margin = 10
    slot_height = play_height / slot_count - slot_margin
    card_top = 0
    card_left = 0
    card_width = width * 0.9
    card_height = slot_height

    background = DIV(
        DIV(Class="background-item")
        + DIV(Class="background-item")
        + DIV(Class="background-item")
        + DIV(Class="background-item")
        + DIV(Class="background-item"),
        Class="background-container",
        style={"position": "absolute", "height": px(play_height), "width": px(width)}
    )
    #main <= background
    for i in range(slot_count):
        row = i

        left = 0
        top = (slot_height + slot_margin) * i

        rank_id = f'R{i + 1}'
        seq_id = f'W{i + 1}'
        detail = TABLE(
            TR(
                TD(SPAN(), width="50%") +
                TD(SPAN(Class="rank_detail"), width="12.5%") +
                TD(SPAN(Class="rank_detail"), width="12.5%") +
                TD(SPAN(Class="rank_detail"), width="12.5%") +
                TD(SPAN(Class="rank_detail"), width="12.5%")
            ), width="100%"
        )

        sz = DIV(detail, Class="rank_hook")
        rank = DIV(
            TABLE(
              TR(
                  TD(
                      DIV(f'{i+1:2d}', Class="index"),
                      width="1%"
                    ) +
                  TD(sz)
              ),
                width="100%"
                ),
            id=rank_id,
            Class='rank',
            style={"left": px(left), "top": px(top), "width": px(width), "height": px(slot_height), },
        )
        rank_slots.append(rank)
        cardpos = content_deck[i].Prev_rank
        card = content_deck[cardpos].create_card(i, card_top, card_left, card_width, card_height)
        sz <= card

        main <= rank



@dataclass
class AQContent():
    key: str
    html: str
    Current_rank: int
    Prev_rank: int

    def make_header(self, cardno):
        global max_value
        header_id = f'H{cardno}'
        bar_id = f'B{cardno}'
        barwid = self.Value / max_value * 100 # bar is 50% of window

        header = DIV(
            DIV(self.key, id=f'Q{cardno}', Class="card-header-text") +
                    DIV('{:4.1f}'.format(self.Value), id=f'V{cardno}', Class="card-header-text") +
            DIV(
                        DIV(id=bar_id, Class="bar"), Class="card-header-text",
                        style={"width": f"{barwid}%", "height": "50%", }
            ), id=header_id, Class="header-container"
        )
        return header

    def create_card(self, cardno, top, left, width, height):

        card_id = f'C{cardno}'
        self.card = card_id

        card = DIV(self.html,
                   id=card_id,
                   Class="card",
                   style={"position": "absolute", "height": px(height), "top": px(0), })
        return card


def whenever(function, state, do):
    _time = None

    def local():
        if function() == state:
            timer.clear_interval(_time)
            do()
    _time = timer.set_interval(local, 100)
    local()




def all_clear():
    for c in document.select(".card"):
        state = getattr(c, "busy", False)
        #debug(f" card {c.id} {state}")
        if state:
            return False
    return True


def done_arrange():
    global current_stream
    if current_stream != None:
        if more_backwards() and more_forwards():
            current_stream.disabled = False
            return

    button_set = {"forward_one", "forward_stream", "back_one", "back_stream"}

    disable_set = copy.copy(button_set)
    if more_forwards():
        disable_set -= {"forward_one", "forward_stream"}
    if more_backwards():
        disable_set -= {"back_one", "back_stream"}

    enable_set = button_set - disable_set
    debug("disable", disable_set)

    for b in disable_set:
        document[b].disabled = True

    for b in button_set - disable_set:
        document[b].disabled = False


def single_step(forward=True):
    global content_date, content_deck

    get_next_decade(forward)

    document['togo'].text = content_date
    debug(content_date)

    mp = [(rank_slots[c.Prev_rank].select_one(".card").id, c.Current_rank, c.Prev_rank) for c in content_deck]

    for card_id, c, p in mp:
        newt = content_deck[c].html
        oldh = document[card_id].select_one(".header-container")
        #debug(card_id, c, p, oldh.text, newt.text)
        #alert("replace")
        c = document[card_id]
        c.clear()
        c <= DIV(newt)
        
        
        #oldh.replaceWith(document.createElement(newt))

    move_card([(card_id, c, p) for (card_id, c, p) in mp if c != p])
    whenever(all_clear, True, done_arrange)


def multi_step(ev, forward=True):
    global stop_flag, current_stream
    t = ev.target
    if current_stream != None:
        #t.text = t.saveText
        stop_flag = True
        return
    current_stream = t
    stop_text = "||"

    t.saveText = t.text
    t.text = stop_text
    t.disabled = False

    def can_move():
        if forward:
            return more_forwards()
        else:
            return more_backwards()

    def local():
        global stop_flag, current_stream

        def busy_check():
            whenever(all_clear, True, local)

        def funny():
            timer.set_timeout(local, 5000)

        if stop_flag:
            stop_flag = False
            current_stream = None
            ev.target.text = ev.target.saveText
            done_arrange()
        else:
            if can_move():
                if True:
                    timer.set_timeout(busy_check, 5000)
                    single_step(forward)
                else:
                    whenever(all_clear, True, funny)
                    single_step(forward)
            else:
                current_stream = None
                ev.target.text = ev.target.saveText
                done_arrange()
    local()


def snapon(rank, card):
    targetRank = document[rank_slots[rank].id].select_one(".rank_hook")
    targetRank <= card


def move_card(it):
    single = False
    if len(it) > 0:
        card_id, c, p = it[0]
        debug(f"move {card_id} {p} to {c}")
        rank_id = f'R{c+1}'

        shuffleSrc = p
        to = c
        origin_rank = document[rank_slots[shuffleSrc].id]
        target_rank = document[rank_slots[to].id]
        delta_top = target_rank.top - origin_rank.top
        delta_left = target_rank.left - origin_rank.left
        frameCount = 20 * abs(p - c)
        shuffleFrom = to
        src = document[card_id]
        margin = 0
        src.busy = True

        def shuffle2(src):
            #src.style.left = px(margin)
            #alert(src.style.top)
            src.style.top = px(margin)
            snapon(to, src)

            #debug("Done")
            if single:
                move_card(it[1:])
            src.busy = False
        animateCSS(src, frameCount, 30, {
            "top": lambda frame, time: px(delta_top / frameCount * frame + margin),
            "left": lambda frame, time: px(delta_left / frameCount * frame + margin),
        }, shuffle2)
        if not single:
            move_card(it[1:])

    else:
        debug("alldone")


def TRTD(*args, **kwargs):
    return TR(TD(*args, **kwargs))


def animateCSS(element, numFrames, timePerFrame, animation, whendone=None):
    """ Adapted from Flanagan's javascript version
    """
    # park these variables inside element - naughty
    element.frame = 0  # // Store current frame number
    element.time = 0.0  # // Store total elapsed time
    """
    // Arrange to call displayNextFrame() every timePerFrame milliseconds.
    // This will display each of the frames of the animation.
    """
    element.intervalId = None

    def displayNextFrame():
        if element.frame >= numFrames:  # // First, see if we're done
            timer.clear_interval(element.intervalId)  # // If so, stop calling ourselves
            """
            del element.frame
            del element.time
            del element.intervalId
            """
            if whendone:
                whendone(element)  # // Invoke whendone function
            return

        for cssprop in animation:
            """
                // For each property, call its animation function, passing the
                // frame number and the elapsed time. Use the return value of the
                // function as the new value of the corresponding style property
                // of the specified element. Use try/catch to ignore any
                // exceptions caused by bad return values.
            """
            element.style[cssprop] = animation[cssprop](element.frame, element.time)

        element.frame += 1  # // Increment the frame number
        element.time += timePerFrame  # // Increment the elapsed time

    element.intervalId = timer.set_interval(displayNextFrame, timePerFrame)

    """
    // The call to animateCSS() returns now, but the previous line ensures that
    // the following nested function will be invoked once for each frame
    // of the animation.

    // Now loop through all properties defined in the animation object
    """

ttt = { 'Wigan Athletic': {'2011': 42, '2012': 43, '2013': 36},
 'Wolverhampton Wanderers': {'2011': 40,
                             '2012': 25,
                             '2019': 57,
                             '2020': 59,
                             '2021': 45,
                             '2022': 51}}
config = {
    "slot_count": 10, 
    "paragraph1": "paragraph1", 
    "paragraph2": "paragraph2", 

}
