#!/usr/bin/python
import pygame
import time
from RPi import GPIO
import thread
from array import array
from pygame.locals import *
from morse_lookup import *
import Tkinter as tk

pygame.mixer.pre_init(44100, -16, 1, 1024)
pygame.init()

bpm = 30
dit_length = 6.0 / bpm
dit_dash = 2*dit_length
letter_break = 3*dit_length
word_break = 10*dit_length

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

def wait_for_keydown(pin):
    while GPIO.input(pin):
        time.sleep(0.01)

def wait_for_keyup(pin):
    while not GPIO.input(pin):
        time.sleep(0.01)

def decoder_thread():
    new_word = False
    while True:
        time.sleep(.01)
        key_up_length = time.time() - key_up_time if key_up_time > key_down_time else 0
        if len(buffer) > 0 and key_up_length >= letter_break:
            new_word = True
            bit_string = "".join(buffer)
            w.text.insert(tk.INSERT, try_decode(bit_string))
            del buffer[:]
        elif new_word and key_up_length >= word_break:
            new_word = False
            w.text.insert(tk.INSERT, " ")

pin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

tone_obj = ToneSound(frequency = 800, volume = .5)
key_up_time = 0
key_down_time = 0
buffer = []

DASH = "-"
DOT = "."

def read_thread():
    key_down_length = 0
    while True:
        wait_for_keydown(pin)
        global key_down_time
        key_down_time = time.time() #record the time when the key went down
        tone_obj.play(-1) #the -1 means to loop the sound
        wait_for_keyup(pin)
        global key_up_time
        key_up_time = time.time() #record the time when the key was released
        key_down_length = key_up_time - key_down_time #get the length of time it was held down for
        tone_obj.stop()
        buffer.append(DASH if key_down_length > dit_dash else DOT)

root = tk.Tk()
start_pos = root.winfo_screenwidth() - 200

class FullScreenApp(object):
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(height=100, relief=tk.FLAT, background="black")
        self.canvas.grid(sticky=tk.W+tk.E, row=0)
        
        self.text = tk.Text(root, relief=tk.FLAT, borderwidth=10, font=("DejaVu Sans Mono",50), width=1, height=1, wrap=tk.WORD)
        self.text.grid(sticky=tk.W+tk.E+tk.N+tk.S, row=1)
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        self.text.focus_set()
        self.root.attributes("-fullscreen", True)
        
        self.last_value = False
        self.lines = []
        self.update_canvas()
        
    def update_canvas(self):
        value = not GPIO.input(pin)
        if value:
            if not self.last_value:
                self.last_line = self.canvas.create_line(start_pos, 50, start_pos, 50, width=30, fill="white")
            coords = self.canvas.coords(self.last_line)
            coords[0] -= 1
            self.canvas.coords(self.last_line, *coords)
        if not value and self.last_value:
            self.lines.append(self.last_line)
        def f(line):
            self.canvas.move(line, -1, 0)
            coords = self.canvas.coords(line)
            if (coords[2] < 0):
                self.canvas.delete(line)
            return coords[2] >= 0
        self.lines = filter(f, self.lines)
        self.last_value = value
        self.root.after(10, self.update_canvas)

w = FullScreenApp(root)

thread.start_new_thread(decoder_thread, ())
thread.start_new_thread(read_thread, ())
    
w.root.mainloop()
