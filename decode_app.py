# -*- coding: utf-8 -*-

from tone_sound import ToneSound
import Tkinter as tk
from decode_tree import DecodeTree
from RPi import GPIO
import time
import math

class DecodeApp(object):
    def __init__(self, pin):
        self.pin = pin
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.root = tk.Tk()

        self.tone_obj = ToneSound(frequency = 800, volume = .5)
        self.start_pos = self.root.winfo_screenwidth() - 200
        
        self.cpm = tk.StringVar()
        self.cpm.trace("w", self.cpm_changed)
        self.cpm.set(30)
        self.auto_speed = tk.IntVar()
        self.auto_speed.set(0)

        self.canvas = tk.Canvas(height=100, relief=tk.FLAT, highlightthickness=0, background="black")
        self.canvas.grid(sticky=tk.W+tk.E, row=0, columnspan=2)
        
        self.text = tk.Text(self.root, relief=tk.FLAT, borderwidth=10, highlightthickness=0, font=("DejaVu Sans Mono",50), width=1, height=1, wrap=tk.WORD)
        self.text.grid(sticky=tk.W+tk.E+tk.N+tk.S, row=1)

        self.tree = DecodeTree(self.root)
        self.tree.canvas.grid(sticky=tk.N+tk.S, row=1, column=1, rowspan=2)
        
        self.foot = tk.Frame(self.root, borderwidth=10, background="white")
        self.foot.grid(sticky=tk.N+tk.W+tk.E+tk.S, row=2, column=0)
        
        tk.Label(self.foot, text="Speed:", font=("DejaVu Sans Mono",24), background="white").pack(side=tk.LEFT)
        self.cpmEdit = tk.Entry(self.foot, font=("DejaVu Sans Mono",24), width=4, justify=tk.RIGHT, textvar=self.cpm, highlightthickness=0, relief=tk.FLAT)
        self.cpmEdit.pack(side=tk.LEFT)
        tk.Label(self.foot, text=" CpM ", font=("DejaVu Sans Mono",24), background="white").pack(side=tk.LEFT)
        tk.Button(self.foot, text="+", command=self.cpm_plus, font=("DejaVu Sans Mono",24), padx=12, pady=2).pack(side=tk.LEFT)
        tk.Label(self.foot, text=" ", font=("DejaVu Sans Mono",24), background="white").pack(side=tk.LEFT)
        tk.Button(self.foot, text="−", command=self.cpm_minus, font=("DejaVu Sans Mono",24), padx=12, pady=2).pack(side=tk.LEFT)
        tk.Label(self.foot, text="  ", font=("DejaVu Sans Mono",24), background="white").pack(side=tk.LEFT)
        tk.Checkbutton(self.foot, text="Auto", font=("DejaVu Sans Mono",24), indicatoron=False, padx=12, pady=2, variable=self.auto_speed).pack(side=tk.LEFT)
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        self.text.focus_set()
        self.root.attributes("-fullscreen", True)

        self.root.bind("<Escape>", self.clear_all)
        
        self.last_value = False
        self.lines = []
        self.key_down_time = 0
        self.key_up_time = 0
        self.new_word = False
        self.read_input()
        
    def clear_all(self, *args):
        self.text.delete(1.0, tk.END)
        
    def run(self):
        self.root.mainloop()
        
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
                char = self.tree.current_char()
                if not char:
                    char = "�"
                self.text.insert(tk.INSERT, char)
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
            if self.auto_speed.get():
                self.cpm.set(int(round(6.0 / (key_down_length / 3.0))))
        else:
            self.tree.dot()
            if self.auto_speed.get():
                self.cpm.set(int(round(6.0 / key_down_length)))

    def read_input(self):
        value = not GPIO.input(self.pin)
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
