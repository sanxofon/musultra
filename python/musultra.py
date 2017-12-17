#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import pyaudio
import numpy as np
import time
import serial
import keyboard
import sys
import os

from escalas import escalas
"""
    EJECUTAR AYUDA:
cd C:\s\git\arduino\picumple\python
python musonic.py -h

    EJECUTAR EJEMPLO:
cd C:\s\git\arduino\picumple\python
python musonic.py -e Ryosen -d 3

    TODO:
- Enviar a arduino el máximo de medida
- Probar promediar tiker en arduino

"""

# MAGICA CONFIGURACIÓN DE CODECS SALIDA ----------------------
# FIX PARA WINDOWS CONSOLE, Usar: chcp 1252
import codecs,locale,sys
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
#--------------------------------------------------------------------------------
import argparse
# Inicializamos el "parser" de argumentos con la descripción general
parser = argparse.ArgumentParser(description=u"MusUltra v0.5 - Santiago Chávez")
parser.add_argument("-l", "--lista", help=u"Muestra un listado de las escalas definidas.", action="store_true")
parser.add_argument("-e", "--escala", help=u"Define la escala a usar por nombre o por índice.")
parser.add_argument("-c", "--continuo", help=u"No filtrar la salida con una escala.", action="store_true")
parser.add_argument("-a", "--akey", type=float, help=u"Define el tono de A central (440.0).")
parser.add_argument("-d", "--distancia", type=float, help=u"Distancia del intervalo en cm (2).")
parser.add_argument("-o", "--octava", type=int, help=u"Define la octava inicial (1-10).")
parser.add_argument("-s", "--subdiv", type=float, help=u"Subdivisiones en la octava (12).")
args = parser.parse_args()
if args.lista:
    os.system('cls' if os.name == 'nt' else 'clear')
    for i,l in enumerate(escalas.keys()):
        print((i+1),l.decode('utf-8'),escalas[l])
        if i>=12 and i/12.0 == float(round(i/12.0)):
            x=raw_input("")
            os.system('cls' if os.name == 'nt' else 'clear')
    sys.exit("")
#--------------------------------------------------------------------------------

# Iniciar sonando
streamOn = 0

# Arduino
arduino = serial.Serial('COM11', 9600, timeout=.1)
distancias = []
tiker = 3
maxdis = 80
escout = ""

# Globales
CHANNELS = 2
RATE = 44100
TT = time.time()
freq = 100.0
newfreq = 100.0
phase = 0
#continuo o afinado
if args.subdiv:
    escal = args.subdiv
else:
    escal = 12.0 # Subdivisiones en una octava
if args.octava:
    iniscal = args.octava - 4
else:
    iniscal = -3 # Octava más baja a partir de A central
troot = np.power(2.0,1.0/escal); # escal'ava raiz de 2
if args.akey:
    acentral = float(args.akey)
else:
    acentral = 434.0 # A central en Hz
# Lista de intervalos
listerval = []
listaFreq = []

# FUNCIONES ---------------------------------------------------------------------------
def setListerval(filtrar):
    global escal, escala, maxdis,listerval,escout
    # filtrar = "Be-Bop Semi-disminuida" #"Cromática", "Mayor", "Mixolidia", etc.
    listerval = []
    if filtrar in escalas.keys():
        escout = filtrar.decode('utf-8')
        # escala = escalas["Cromática"] # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        escala = escalas[filtrar]
        for i in xrange(int(escal*100)):
            r = i % 12
            while r<0:
                r+=12
            if r in escala:
                listerval.append(i)
        # La lista se corta en maxdist
        listerval = listerval[0:maxdis]
    else:
        escout = u"No se filtra la escala"
        # No se filtra la escala
        listerval = xrange(maxdis)

#continuo o afinado
def setLF():
    global listaFreq,listerval,maxdis,escal,iniscal
    listaFreq = []
    for i in listerval:
        if natural>0:
            listaFreq.append(calcStepFreqJ(i+(int(escal)*iniscal)))
        else:
            listaFreq.append(calcStepFreq(i+(int(escal)*iniscal)))
    if maxdis>len(listaFreq):
        maxdis = len(listaFreq)

def cabecera():
    global acentral,iniscal,escout
    os.system('cls' if os.name == 'nt' else 'clear')
    if escout.encode('utf-8') in escalas.keys():
        escout = escout+" ("+str(escalas.keys().index(escout.encode('utf-8'))+1)+")"
    print(" -----------------------\n|: Non Mus Ultra v0.5\n -----------------------\n|      A4: "+str(acentral)+" Hz\n|  Octava: "+str(iniscal+4)+"\n|  Escala: "+escout+"\n|  Interv: "+str(stepf)+"\n -----------------------\n|  [Space] - Play/Pausa\n|  [ESC]   - Salir\n -----------------------")
    print("|   cm      ", " Hz"," "*40,sep=" ")

def tryEscala(e):
    global filtrar
    try:
        filtrar = int(e)-1 # 1, 2, 3, 4, etc.
        if filtrar>=0:
            esk = escalas.keys()
            filtrar = esk[filtrar]
        else:
            filtrar = e #"Cromática", "Mayor", "Mixolidia", etc.
    except:
        filtrar = e #"Cromática", "Mayor", "Mixolidia", etc.
        pass
    setListerval(filtrar)
    setLF()
    cabecera()

def filterFreq(i):
    global listaFreq,stepf
    i = int(round(i/stepf))
    return listaFreq[i]


def callback(in_data, frame_count, time_info, status):
    global TT,phase,freq,newfreq
    if newfreq != freq:
        phase = 2*np.pi*TT*(freq-newfreq)+phase
        freq=newfreq
    left = (np.sin(phase+2*np.pi*freq*(TT+np.arange(frame_count)/float(RATE))))
    data = np.zeros((left.shape[0]*2,),np.float32)
    data[::2] = left
    data[1::2] = left
    TT+=frame_count/float(RATE)
    return (data, pyaudio.paContinue)

# Recibe la frecuencia en Hertz
# Regresa el numero de pasos desde A central
def calcFreqStep(f): 
    global troot,acentral
    d = 1000000.0 # six zeros before decimal point
    return np.round(d*(np.log(f/acentral)/np.log(troot)))/d;

# Recibe el numero de pasos (semitonos) desde A central (440)
# Regresa la frecuencia en Hertz
def calcStepFreq(s):
    global troot,acentral
    return acentral * np.power(troot,s)

# Recibe el numero de pasos (semitonos justos)
# Regresa la frecuencia en Hertz
def calcStepFreqJ(s):
    global acentral,escal,iniscal
    mo = (s % 12)
    di = np.floor(s / escal)
    if mo<0:
        mo = mo+12
    # Lista de racionales justos
    t = [
        1.0,        #Tonica
        25.0/24.0,  # Segunda menor
        9.0/8.0,    # Segunda mayor
        6.0/5.0,    # Tercera menor
        5.0/4.0,    # Tercera mayor
        4.0/3.0,    # Cuarta
        45.0/32.0,  # Quinta dim
        3.0/2.0,    # Quinta
        8.0/5.0,    # Sexta menor
        5.0/3.0,    # Sexta mayor
        9.0/5.0,    # Septima menor
        15.0/8.0,   #  Septima mayor
    ]
    return (acentral * t[mo]*np.power(2,di))
# FUNCIONES ---------------------------------------------------------------------------


if args.continuo:
    escout = u"Continua"
    afinado = 0
    basef = 22.5
    if args.distancia:
        stepf=distancia
    else:
        stepf = 5.0
else:
    afinado = 1
     # Pasos cada stepf centrimetros
    if args.distancia:
        stepf=args.distancia
    else:
        stepf = 2.0
    natural = 0
    # Filtrar por escala
    if args.escala:
        tryEscala(args.escala.strip())
    else:
        tryEscala("Cromática")

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                stream_callback=callback)

if streamOn>0:
    stream.start_stream()
else:
    stream.stop_stream()
cabecera()
try:
    while 1:
        if keyboard.is_pressed('esc'):#if space is pressed
            arduino.write('2')
            stream.stop_stream()
            stream.close()
            p.terminate()
            break
        elif keyboard.is_pressed('e'):
            e = raw_input(u"Nombre o índice de la escala: ")
            tryEscala(e)
        elif keyboard.is_pressed('1'):
            tryEscala("Cromática")
        elif keyboard.is_pressed('2'):
            tryEscala("Lidia")
        elif keyboard.is_pressed('3'):
            tryEscala("Mixolidia")
        elif keyboard.is_pressed('4'):
            tryEscala("Mayor")
        elif keyboard.is_pressed('5'):
            tryEscala("Dórica")
        elif keyboard.is_pressed('6'):
            tryEscala("Jónica")
        elif keyboard.is_pressed('7'):
            tryEscala("Menor")
        elif keyboard.is_pressed('8'):
            tryEscala("Frigia")
        elif keyboard.is_pressed('9'):
            tryEscala("Locria")
        elif keyboard.is_pressed('0'):
            tryEscala("Ryosen")
        elif keyboard.is_pressed('space'):#if space is pressed
            if streamOn>0: 
                streamOn = 0 
                arduino.write('2')
                stream.stop_stream()
            else:
                streamOn = 1 
                arduino.write('1')
                stream.start_stream()
        cm = arduino.readline()
        if cm:
            try:
                cm = int(cm.strip())/10.0
            except:
                continue
                pass

            if cm>maxdis:
                continue
            if len(distancias)<tiker:
                distancias.append(cm)
                continue
            else:
                dis = sum(distancias) / len(distancias)
                # newfreq=200+np.sin(2*np.pi*1/20.*dis)*100 #update the frequency This will depend on y on the future
                if afinado:
                    newfreq = filterFreq(dis)
                else:
                    newfreq=basef+(stepf*dis)
                dis = str(round(dis,1))
                print("|  "+dis, round(newfreq,2)," "*40,sep=" "*(10-len(dis)),end='\r')

                distancias = []

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()