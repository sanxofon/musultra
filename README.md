# Non Mus Ultra v0.6

Python music instrument for arduino with an Utrasonic Ranging Module HC SR04

## Author:

### Santiago Chávez Novaro ([@sanxofon](https://twitter.com/sanxofon))

## Install dependencies:

	pip install keyboard
	pip install pyserial
	pip install pyaudio

## Example use:

Python 2.7+

	$ python musultra.py -p -e Ryosen -d 3 -t C -a 440.0 -x COM11

Python 3.4+

	$ python musultra3.py -p -e Ryosen -d 3 -t C -a 440.0 -x COM11

## Show help:

Python 2.7+

	$ python musultra.py -h

Python 3.4+

	$ python musultra3.py -h


## Arduino set-up:

![circuito](circuito.png)