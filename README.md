# morse
Visual [morse code](https://en.wikipedia.org/wiki/Morse_code) decoder for the [Raspberry Pi](https://en.wikipedia.org/wiki/Raspberry_Pi).

The code in this repository was inspired by and is partly based on the [Raspberry Pi Learning Resource **Morse Code Virtual Radio**](https://www.raspberrypi.org/learning/morse-code-virtual-radio/) whose code can be found on [GitHub](https://github.com/raspberrypilearning/morse-code-virtual-radio) as well.

![Screenshot](/screenshot.png?raw=true "Screenshot")

The decoder is written in Python3 and uses
 - [RPi.GPIO](https://pypi.python.org/pypi/RPi.GPIO) to read the GPIO port and
 - [PyGame](http://www.pygame.org) to generate the sidetone.

Connect a regular straight keyer such that it closes the connection from a GPIO input pin and ground. E.g. use pin number 39 (ground) and pin number 40 (BCM 21). See [Raspberry Pinout](https://pinout.xyz). The input pin can easily be set in the `main.py`. The state of this input pin is read every 10 ms which creates a sample rate of 100 Hz.

The GUI is written in [tkinter](https://docs.python.org/3/library/tkinter.html), Pythons interface to [Tcl/Tk](http://www.tcl.tk). The moving bars on the top and the visual decoding tree are painted using the [Tkinter Canvas Widget](http://effbot.org/tkinterbook/canvas.htm).

We also created a German [flyer explaining morse code](https://github.com/malteschmitz/morsecode) and how to decode morse code using the binary search tree, which is used in the visualization of this application as well.

# further ideas
- Add support for iambic paddles
- Improve automatic speed detection
- Experiment with higher speeds
- Add support for morse code generation
- Add support for recording and playback
