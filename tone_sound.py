import pygame
from pygame.locals import *
from array import array

class ToneSound(pygame.mixer.Sound):
    def __init__(self, frequency, volume):
        pygame.mixer.pre_init(44100, -16, 1, 1024)
        pygame.init()
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
        for time in range(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples
