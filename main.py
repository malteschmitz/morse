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

class ToneSound(pygame.mixer.Sound):
    def __init__(self, frequency, volume):
        self.frequency = frequency
	pygame.mixer.Sound.__init__(self, buffer=self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        period = int(round(pygame.mixer.get_init()[0] / self.frequency))
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
        key_up_length = time.time() - key_up_time
        if len(buffer) > 0 and key_up_length >= 1.5:
            new_word = True
            bit_string = "".join(buffer)
            w.text.insert(tk.INSERT, try_decode(bit_string))
            del buffer[:]
        elif new_word and key_up_length >= 4.5:
            new_word = False
            w.text.insert(tk.INSERT, " ")

pin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

tone_obj = ToneSound(frequency = 800, volume = .5)
key_up_time = 0
buffer = []

DASH = "-"
DOT = "."

def read_thread():
	key_down_time = 0
	key_down_length = 0
	while True:
		wait_for_keydown(pin)
		global key_up_time
		key_down_time = time.time() #record the time when the key went down
		tone_obj.play(-1) #the -1 means to loop the sound
		wait_for_keyup(pin)
		key_up_time = time.time() #record the time when the key was released
		key_down_length = key_up_time - key_down_time #get the length of time it was held down for
		tone_obj.stop()
		buffer.append(DASH if key_down_length > 0.15 else DOT)

class FullScreenApp(object):
	def __init__(self, master):
		self.master = master
		self.text = tk.Text(master, relief="flat", font=("DejaVu Sans Mono",50))
		self.text.pack(fill=tk.BOTH, expand=1)
		self.text.focus_set()
		self.master.attributes("-fullscreen", True)

w = FullScreenApp(tk.Tk())

thread.start_new_thread(decoder_thread, ())
thread.start_new_thread(read_thread, ())
		
w.master.mainloop()
