#!/usr/bin/env python3
"""
Watch clipboard for maps and check what whether it should be run based on mods, name, tier

Author: QuaziK
"""

import os
import re
import pprint
from tkinter import Tk, TclError, Button, Label, StringVar, GROOVE
import time
import requests
import threading

VER = '0.3.0 (may.2021)'
STOP = 0

RUN_PREF = { # 1=run, 0=dont run
    "Haewark Hamlet":   1,
    "Tirn's End":       1,
    "Lex Proxima":      1,
    "Lex Ejoris":       1,
    "New Vastir":       1,
    "Glennach Cairns":  1,
    "Valdo's Rest":     1,
    "Lira Arthain":     1
}

MOD_PREF = { # 1=care, 0=dont care
    'reflect':      1,
    'noregen':      1,
    'noleech':      1,
    'lessres':      1
}

def parse_map_info(text):
    """
    Parse item info (from clipboard, as obtained by pressing Ctrl+C hovering an item in-game).
    """
    m = re.findall(r'^Rarity: (\w+)\r?\n(.+?)\r?\n(.+?)\r?\n', text)
    if not m:
        return {}
    info = {'name': m[0][1], 'rarity': m[0][0], 'type': m[0][2]}
    m = re.findall(r'^Quality: +(\d+)%', text)
    reg = re.findall('Atlas Region: (\w+\s\w+)', text)
    if reg == []: reg = re.findall('Atlas Region: (\w+\W\w\s\w+)', text)
    info['region'] = reg[0]  
    info['quality'] = int(m[0]) if m else 0
    info['corrupted'] = bool(re.search('^Corrupted$', text, re.M))
    info['reflect'] = text.find('reflect')
    info['noregen'] = text.find('Players cannot Regenerate Life, Mana or Energy Shield')
    info['noleech'] = text.find('Cannot Leech Life from Monsters')
    info['lessres'] = text.find('% maximum Player Resistances')
    return info

def watch_clipboard(crt_area):

    # get current clipboard to ignore whatever is stored in it
    try:
        prev = Tk().clipboard_get()
    except TclError:
        prev = None
        
    while 1:
        if STOP:
            break
            
        try:
            text = Tk().clipboard_get()
        except TclError:     # ignore non-text clipboard contents
            continue
        try:
            if text != prev:
                info = parse_map_info(text)
                trade_info = None
                if info: # Interpret map info here
                    if RUN_PREF[info['region']] == 0:
                        crt_area.set("[++] {" + info['name'] + "} is in " + info['region'])
                        print("[++] {" + info['name'] + "} is in " + info['region'])                        
                    elif info['reflect'] > -1 and MOD_PREF['reflect']:
                        crt_area.set("[!!!] {" + info['name'] + "} REFLECT")
                        print("[!!!] {" + info['name'] + "} REFLECT")
                    elif info['noregen'] > -1:
                        crt_area.set("[!!] {" + info['name'] + "} NO REGEN")
                        print("[!!] {" + info['name'] + "} NO REGEN")
                    elif info['noleech'] > -1:
                        crt_area.set("[!!] {" + info['name'] + "} NO LEECH")                        
                        print("[!!] {" + info['name'] + "} NO LEECH")                        
                    elif info['lessres'] > -1:
                        crt_area.set("[!] {" + info['name'] + "} LESS RES")                           
                        print("[!] {" + info['name'] + "} LESS RES")                           
                    else:
                        crt_area.set("[*] {" + info['name'] + "} SAFE")
                        print("[*] {" + info['name'] + "} SAFE")
                prev = text
            time.sleep(.2)
        except KeyboardInterrupt:
            break

def quit(root):
    """
    Stop polling & the main UI loop.
    """
    print("[*] Quitting overlay")
    global STOP
    STOP = 1
    time.sleep(0.2)
    root.quit()

def map_ui():
    global STOP

    print("[*] Overlay window is running")

    # the overlay's main window
    root = Tk()

    # topmost, no borders, center horizontally, top-of-screen
    root.wm_attributes("-topmost", 1)
    root.attributes("-toolwindow", 1)
    w, h = 300, 60
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    root.geometry('{}x{}+{}+{}'.format(w, h, x, 0))
    root.update_idletasks()
    root.overrideredirect(True)

    # game status label
    crt_area = StringVar()
    l_area = Label(root, textvariable=crt_area, relief=GROOVE)
    crt_area.set('-')
    l_area.pack(pady=5)

    # quit button
    but = Button(root, command=lambda:quit(root), text='Quit')
    but.pack()

    threading.Thread(target=watch_clipboard, args=(crt_area,)).start()    
    root.mainloop()
    STOP = 1

if __name__ == '__main__':
    print('[*] Watching clipboard for MAPS (Ctrl+C to stop)')
    map_ui()
    # watch_clipboard()
