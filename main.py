#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame
import time
import math
from RPi import GPIO
from array import array
from pygame.locals import *
import Tkinter as tk

pygame.mixer.pre_init(44100, -16, 1, 1024)
pygame.init()

class ToneSound(pygame.mixer.Sound):
    def __init__(self, frequency, volume):
        self.frequency = frequency
        pygame.mixer.Sound.__init__(self, buffer=self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        mixer_init = pygame.mixer.get_init()
        if mixer_init == None:
            raise Exception("Mixer not available!")
        period = int(round(mixer_init[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
        for time in xrange(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples

class Node:
    def __init__(self, value, dot = None, dash = None):
        self.value = value
        self.dot = dot
        self.dash = dash
        self.oval = None
        self.line = None

PIN = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

TREE_LEFT_OFFSET = 10
TREE_LEVEL_DEPTH = 60
TREE_DIAMETER = 22
TREE_LINE_WIDTH = 1.5
TREE_SELECTED_LINE_WITH = 2.5
TREE_SIBLING_DISTANCE = lambda level: 2**max(5-level, 0)*25
TREE_INIT_Y = 450
TREE_DRAW = "black"
TREE_SELECTED_DRAW = "red"
TREE_FILL = "light blue"
TREE_SELECTED_FILL = "light pink"

class DecodeTree:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, width=500, height=500, background="white", highlightthickness=0)

        self.root_node = Node("",
            Node("E",
                Node("I",
                    Node("S",
                        Node("H", Node("5"), Node("4")),
                        Node("V", None, Node("3"))),
                    Node("U",
                        Node("F"),
                        Node("Ü", None, Node("2")))),
                Node("A",
                    Node("R",
                        Node("L"),
                        Node("Ä", Node("+"))),
                    Node("W",
                        Node("P"),
                        Node("J", None, Node("1"))))),
            Node("T",
                Node("N",
                    Node("D",
                        Node("B", Node("6"), Node("=")),
                        Node("X", Node("/"))),
                    Node("K",
                        Node("C"),
                        Node("Y"))),
                Node("M",
                    Node("G",
                        Node("Z", Node("7")),
                        Node("Q")),
                    Node("O",
                        Node("Ö", Node("8")),
                        Node("CH", Node("9"), Node("0"))))))

        self.plot_tree(self.root_node, 1, TREE_INIT_Y)

        self.reset()

    def reset(self):
        self.clear()
        self.current_node = self.root_node
        self.mark()

    def clear_tree(self, node):
        if node.oval != None:
            self.canvas.itemconfig(node.oval, fill=TREE_FILL)
            self.canvas.itemconfig(node.oval, outline=TREE_DRAW)
            self.canvas.itemconfig(node.oval, width=TREE_LINE_WIDTH)
        if node.line != None:
            self.canvas.itemconfig(node.line, fill=TREE_DRAW)
            self.canvas.itemconfig(node.line, width=TREE_LINE_WIDTH)
        if node.dash != None:
            self.clear_tree(node.dash)
        if node.dot != None:
            self.clear_tree(node.dot)

    def clear(self):
        self.current_node = None
        self.clear_tree(self.root_node)
    
    def mark(self):
        if self.current_node != None:
            if self.current_node.oval != None:
                self.canvas.itemconfig(self.current_node.oval, fill=TREE_SELECTED_FILL)
                self.canvas.itemconfig(self.current_node.oval, outline=TREE_SELECTED_DRAW)
                self.canvas.itemconfig(self.current_node.oval, width=TREE_SELECTED_LINE_WITH)
            if self.current_node.line != None:
                self.canvas.itemconfig(self.current_node.line, fill=TREE_SELECTED_DRAW)
                self.canvas.itemconfig(self.current_node.line, width=TREE_SELECTED_LINE_WITH)

    def dash(self):
        if self.current_node != None and self.current_node.dash != None:
            self.current_node = self.current_node.dash
            self.mark()
        else:
            self.clear()

    def dot(self):
        if self.current_node != None and self.current_node.dot != None:
            self.current_node = self.current_node.dot
            self.mark()
        else:
            self.clear()

    def is_char_available(self):
        return self.current_node != self.root_node

    def current_char(self):
        if self.current_node != None and self.current_node.value != "":
            return self.current_node.value
        else:
            return "?"

    def plot_tree(self, node, level, y):
        if node.dot != None:
            node.dot.line = self.canvas.create_line(TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH + TREE_DIAMETER/2, y + TREE_DIAMETER/2, TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH + TREE_LEVEL_DEPTH + TREE_DIAMETER/2, y + TREE_SIBLING_DISTANCE(level)/2 + TREE_DIAMETER/2, width=TREE_LINE_WIDTH, dash=(3,3))
            self.plot_tree(node.dot, level + 1, y + TREE_SIBLING_DISTANCE(level)/2)
        if node.dash != None:
            node.dash.line = self.canvas.create_line(TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH + TREE_DIAMETER/2, y + TREE_DIAMETER/2, TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH + TREE_LEVEL_DEPTH + TREE_DIAMETER/2, y - TREE_SIBLING_DISTANCE(level)/2 + TREE_DIAMETER/2, width=TREE_LINE_WIDTH, dash=(9,3))
            self.plot_tree(node.dash, level + 1, y - TREE_SIBLING_DISTANCE(level)/2)
        node.oval = self.canvas.create_oval(TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH, y, TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH + TREE_DIAMETER, y + TREE_DIAMETER, width=TREE_LINE_WIDTH, fill="light blue")
        self.canvas.create_text(TREE_LEFT_OFFSET + level * TREE_LEVEL_DEPTH + TREE_DIAMETER / 2, y + TREE_DIAMETER / 2, text=node.value, font=("DejaVu Sans Mono",18))  

class FullScreenApp(object):
    def __init__(self, root):
        self.root = root

        self.tone_obj = ToneSound(frequency = 800, volume = .5)
        self.start_pos = root.winfo_screenwidth() - 200
        
        self.cpm = tk.StringVar()
        self.cpm.trace("w", self.cpm_changed)
        
        self.cpm.set(30)

        self.canvas = tk.Canvas(height=100, relief=tk.FLAT, highlightthickness=0, background="black")
        self.canvas.grid(sticky=tk.W+tk.E, row=0, columnspan=2)
        
        self.text = tk.Text(self.root, relief=tk.FLAT, borderwidth=10, highlightthickness=0, font=("DejaVu Sans Mono",50), width=1, height=1, wrap=tk.WORD)
        self.text.grid(sticky=tk.W+tk.E+tk.N+tk.S, row=1)

        self.tree = DecodeTree(root)
        self.tree.canvas.grid(sticky=tk.N+tk.S, row=1, column=1, rowspan=2)
        
        self.foot = tk.Frame(root, borderwidth=10, background="white")
        self.foot.grid(sticky=tk.N+tk.W+tk.E+tk.S, row=2, column=0)
        
        tk.Label(self.foot, text="Speed:", font=("DejaVu Sans Mono",24), background="white").pack(side=tk.LEFT)
        self.cpmEdit = tk.Entry(self.foot, font=("DejaVu Sans Mono",24), width=4, justify=tk.RIGHT, textvar=self.cpm, highlightthickness=0, relief=tk.FLAT)
        self.cpmEdit.pack(side=tk.LEFT)
        tk.Label(self.foot, text=" CpM ", font=("DejaVu Sans Mono",24), background="white").pack(side=tk.LEFT)
        tk.Button(self.foot, text="+", command=self.cpm_plus, font=("DejaVu Sans Mono",24)).pack(side=tk.LEFT)
        tk.Label(self.foot, text=" ", font=("DejaVu Sans Mono",24), background="white").pack(side=tk.LEFT)
        tk.Button(self.foot, text="−", command=self.cpm_minus, font=("DejaVu Sans Mono",24)).pack(side=tk.LEFT)
        
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        self.text.focus_set()
        self.root.attributes("-fullscreen", True)
        
        self.last_value = False
        self.lines = []
        self.key_down_time = 0
        self.key_up_time = 0
        self.new_word = False
        self.read_input()
        
    def cpm_changed(self, *args):
        value = self.cpm.get()
        valid = len(value) < 4
        if valid:
            try:
                if value:
                    cpm = int(self.cpm.get())
                    if cpm < 0:
                        valid = False
                    elif cpm > 0:
                        self.cpm_update(cpm)
            except ValueError:
                valid = False
        if valid:
            self.cpmOld = self.cpm.get()
        else:
            self.cpm.set(self.cpmOld)
        
    def cpm_update(self, cpm):
        self.cpmValue = cpm
        self.dit_length = 6.0 / self.cpmValue
        self.dit_dash = 2 * self.dit_length
        self.letter_break = 3 * self.dit_length
        self.word_break = 7 * self.dit_length
        
    def cpm_plus(self, *args):
        cpm = int(math.floor(self.cpmValue / 5.0)) * 5
        if (cpm < 995):
            self.cpm.set(cpm + 5)
        
    def cpm_minus(self, *args):
        cpm = int(math.ceil(self.cpmValue / 5.0)) * 5
        if (cpm > 5):
            self.cpm.set(cpm - 5)

    def create_new_line(self):
        self.last_line = self.canvas.create_line(self.start_pos, 50,
            self.start_pos, 50, width=30, fill="white")

    def move_last_line(self):
        coords = self.canvas.coords(self.last_line)
        coords[0] -= 1
        self.canvas.coords(self.last_line, *coords)

    def move_lines(self):
        def f(line):
            self.canvas.move(line, -1, 0)
            coords = self.canvas.coords(line)
            if (coords[2] < 0):
                self.canvas.delete(line)
            return coords[2] >= 0
        self.lines = filter(f, self.lines)

    # Call this method as long as the key is up
    def decode_is_up(self, key_up_length):
        if key_up_length >= self.letter_break:
            if self.tree.is_char_available():
                self.text.insert(tk.INSERT, self.tree.current_char())
                self.new_word = True
                self.tree.reset()
        if key_up_length >= self.word_break:
            if self.new_word:
                self.text.insert(tk.INSERT, " ")
                self.new_word = False

    # Call this method if the key is released
    def decode_was_down(self, key_down_length):
        if key_down_length > self.dit_dash:
            self.tree.dash()
        else:
            self.tree.dot()

    def read_input(self):
        value = not GPIO.input(PIN)
        if value:
            # key is down
            if not self.last_value:
                # key just went down
                self.tone_obj.play(-1) #the -1 means to loop the sound
                self.key_down_time = time.time()
                self.create_new_line()
            self.move_last_line()
        
        if not value:
            # key is up
            if self.last_value:
                # key just went up
                self.tone_obj.stop()
                self.key_up_time = time.time()
                key_down_length = self.key_up_time - self.key_down_time
                self.decode_was_down(key_down_length)
                self.lines.append(self.last_line)
            key_up_length = time.time() - self.key_up_time
            self.decode_is_up(key_up_length)
        
        self.move_lines()
        self.last_value = value
        self.root.after(10, self.read_input)

root = tk.Tk()
w = FullScreenApp(root)
    
w.root.mainloop()
