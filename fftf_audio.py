#!/usr/bin/env python
# encoding: utf-8

## Module infomation ###
# Python (3.4.4)
# numpy (1.10.2)
# PyAudio (0.2.9)
# matplotlib (1.5.1)
# All 32bit edition
########################

import numpy as np
import pyaudio

import matplotlib.pyplot as plt

import rospy

from keyboard.msg import Key
import pickle
import uuid

import scipy.fftpack
rospy.init_node('listener', anonymous=True)

some_name=str(uuid.uuid1())


class SpectrumAnalyzer:
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 1000
    RATE= 16384
    CHUNK = 8192
    #CHUNK = 1024
    START = 0
    N = 8192
    #N= 1024

    wave_x = 0
    wave_y = 0
    spec_x = 0
    spec_y = 0
    data = []
    xx=[]

    yy=[]
    big_labels=[]
    types_of_signal=[]
    button=0
    last_audio=np.array([])
    all_audios=[]
    def __init__(self):


        self.rate = rospy.Rate(10)
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format = self.FORMAT,
            channels = self.CHANNELS, 
            rate = self.RATE, 
            input = True,
            output = False,
            frames_per_buffer = self.CHUNK)
        button_subscriber= rospy.Subscriber("/keyboard/keydown",Key,self.buttondown)
        button_down_subscriber= rospy.Subscriber("/keyboard/keyup",Key,self.buttonup)
        self.loop()

    def buttondown(self,button): # this is event
        self.button=button.code

    def buttonup(self,button):

        if(button.code==32 or button.code==13):
            self.big_labels.append(button.code)
            self.all_audios.append(self.last_audio)
            self.save_experiment()
            self.last_audio=np.array([])
        self.button=0

    def save_experiment(self):
        print("saving to file ",some_name)
        pickle.dump({ "x":self.xx,
                      "freq":self.yy,
                      "y":self.types_of_signal,
                      "audio":(self.all_audios,self.big_labels)},
                    open(some_name+".p","wb"))    
    
    def loop(self):
        try:
            while not rospy.is_shutdown():
                self.data = self.audioinput()
                self.fft()
                #self.graphplot()

                if(self.button ==32 or self.button==13):
                  self.xx.append(self.spec_x)
                  self.yy.append(self.data)
                  self.types_of_signal.append(self.button)
                  self.last_audio=np.concatenate((self.last_audio,self.data))
                  
                  print("added new signal")
                self.rate.sleep()
        except KeyboardInterrupt:
            self.pa.close()

        print("End...")

    def audioinput(self):
        ret = self.stream.read(self.CHUNK)
        ret = np.fromstring(ret, np.float32)
        return ret

    def fft(self):
        self.wave_x = range(self.START, self.START + self.N)
        self.wave_y = self.data[self.START:self.START + self.N]
        self.spec_x = np.fft.rfftfreq(self.N, d = 1.0 / self.RATE)  
        y = np.fft.rfft(self.data[self.START:self.START + self.N])    
        self.spec_y = y #np.abs(y) #
        
    def graphplot(self):
        plt.clf()
        # wave
        plt.subplot(311)
        plt.plot(self.wave_x, self.wave_y)
        plt.axis([self.START, self.START + self.N, -0.5, 0.5])
        plt.xlabel("time [sample]")
        plt.ylabel("amplitude")
        #Spectrum
        plt.subplot(312)
        plt.plot(self.spec_x, self.spec_y, marker= 'o', linestyle='-')
        plt.axis([0, self.RATE / 2, 0, 50])
        plt.xlabel("frequency [Hz]")
        plt.ylabel("amplitude spectrum")
        #Pause
        #plt.pause(.01)

if __name__ == "__main__":
    spec = SpectrumAnalyzer()
