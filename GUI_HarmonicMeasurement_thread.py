
#********************** 2017/01/27 Version ********************#

# Note: Threading added in the measureMethod()
# Note: The listbox will now always show the latest measured data
# Note: Threading can avoid non-responsive problem, but will also cause
#       the intereference by clicking other buttons during measurement.
# 01/29: Keithley current option added.
# 01/29: All output will be shut down by clicking quit

from tkinter import *
from tkinter import ttk
import tkinter
from tkinter import filedialog
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import pylab
from pylab import *
import os
import math
import numpy
from LockinAmp import lockinAmp
from keithley2400_I import Keithley2400
import time
import multiprocessing
import threading

root = Tk()

def main():

    global result, func, average, sense, DAC, signal, freq, qx, qy

    qx = multiprocessing.Queue()
    qy = multiprocessing.Queue()

    func='1st' #Set a default mode (1st or 2nd)
    sense='10mV' #Set a default sensitivity range (mV or uV)
    DAC=1 #Set a default DAC output channel
    signal=1 #Set a default OSC signal voltage (V)
    freq=1171 #Set a default OSC frequency (Hz)
    
    result=['']
    values_y=[]
    values_x=[]

    createWidgit()

    root.protocol('WM_DELETE_WINDOW', quit) 
    root.mainloop()

#************************Main End Here***************************#

def updateplot():

    global ax, frame, qx, qy

    try:

        x=qx.get_nowait()
        y=qy.get_nowait()
        #print ("%s" %time.ctime(time.time()*1000))
        if y != 'Q':
            ax.scatter(x, y, s=50, alpha=0.5)
            frame.after(1,updateplot)

        else:
            canvas.draw()
            print ("done")
    except:
        #print ("empty")
        frame.after(1,updateplot)


def measureUpdate(i,lim):

    global qx, qy
    t=0
    a=0.0 #initial amplitude

    while t <= lim :
        #print ("%s" %time.ctime(time.time()*1000-t0))
        #print ("%.2f" %float(time.time()*1000-t0))
        amp = lockinAmp()
        
        tmp=1000*double(amp.readX(average))
        qy.put(tmp)
        qx.put(a)
        #print(tmp[1])
        #time.sleep(i/1000)
        t+=i
        #print(tmp[1])
    qy.put('Q')
    qx.put('Q')


def measureMethod( _inteval, _number, _output, _average, _signal, _frequency, _current):
    
    global values_x, values_y, result

    values_y=[]
    values_x=[]
    result=[]

    i=float(_inteval)
    n=int(_number)
    average=int(_average)
    signal=float(_signal)
    freq=int(_frequency)
    current=float(_current)

    #Setup Keithley2400 for current output and resistance measurement
    keith=Keithley2400(f)
    keith.setCurrent(current)
    keith.outputOn()

    index=1
    data=[]

    while index<=5: #Average of five measurements
        data=data+keith.measureOnce()
        index+=1
        
    print("Measured current: %f mA" %(1000*data[2]))
    print("Measured voltage: %f V" %data[1])
    print("Measured resistance: %f Ohm" %(data[1]/data[2]))
    
    
    ax.clear()
    ax.grid(True)
    ax.set_title("Realtime Hall voltage vs H Plot")
    ax.set_xlabel("Applied Field (Oe)")
    ax.set_ylabel("Lock-In X (mV)")
    #ax.axis([0, i*n, -10, 10])

    def event():

        t=0
        a=0.0

        amp = lockinAmp(func, sense, signal, freq)
        step = (double(_output)/i)/n
        
        while t < n :

            amp.dacOutput(a, DAC)
            tmp=1000*double(amp.readX(average)) #in units of mV
            result.append(tmp)
            values_y.append(tmp)
            values_x.append(a*i)
            ax.scatter(values_x[-1], values_y[-1], s=50, alpha=0.5)
            canvas.draw()
            listbox_l.insert('end', tmp)
            t+=1
            a+=step
            listbox_l.see(END)

        while t < 3*n :

            amp.dacOutput(a, DAC)
            tmp=1000*double(amp.readX(average))
            result.append(tmp)
            values_y.append(tmp)
            values_x.append(a*i)
            ax.scatter(values_x[-1], values_y[-1], s=50, alpha=0.5)
            canvas.draw()
            listbox_l.insert('end', tmp)
            t+=1
            a-=step
            listbox_l.see(END)

        while t <= 4*n :

            amp.dacOutput(a, DAC)
            tmp=1000*double(amp.readX(average))
            result.append(tmp)
            values_y.append(tmp)
            values_x.append(a*i)
            ax.scatter(values_x[-1], values_y[-1], s=50, alpha=0.5)
            canvas.draw()
            listbox_l.insert('end', tmp)
            t+=1
            a+=step
            listbox_l.see(END)

        #scat=ax.scatter(values_x, values_y, s=50, alpha=0.5)
        #canvas.draw()

        keith.outputOff()
        
        listbox_l.insert('end',"Measurement finished")
        listbox_l.see(END)

    th = threading.Thread(target=event)
    th.start()
    

# Option:1st or 2nd harmonic
def optionMethod(val):

    global func 

    func = val

    print("Detecting the %s harmonic voltage" %func)
    

# Sensitivity: How many mVs or uVs
def senseMethod(val):

    global sense 

    sense = val

    print("Sensing range set to:",sense)

# DAC: Which DAC output channel
def dacMethod(val):

    global DAC

    DAC = val

    print("DAC channel:",DAC)
    print("Don't forget to change the calibration factor H(Oe)/DAC(V)")

def keithOutMethod(val):

    
    keith=Keithley2400(f)
    
    if val =='ON':
        keith.outputOn()

    else:
        keith.outputOff()
        
    

def saveMethod():

    global result

    if result == ['']:
        listbox_l.insert('end', "No Data can save.")
        listbox_l.see(END)

    else:

        f =  filedialog.asksaveasfile(mode='w', defaultextension=".txt")

        f.write(func+":\n\n")
        cnt=1
        #output all data 
        for a in range(len(values_y)):

               f.write(str(cnt)+" "+str(values_x[a])+" "+str(values_y[a])+"\n")
               cnt +=1

        f.closed

        listbox_l.insert('end', "The Measurement Data is saved.")
        listbox_l.see(END)

def outputMethod(_interval, _output, _signal, _frequency):

    i=float(_interval)
    signal=float(_signal)
    freq=int(_frequency)
    
    amp = lockinAmp(func, sense, signal, freq)
    
    if _output.replace('.','').replace('-','').isdigit() :
        #print(entry_output.get())
        amp.dacOutput((double(_output)/i), DAC)

        listbox_l.insert('end', "Single output field: "+_output+" Oe.")
        listbox_l.see(END)
    else:
        listbox_l.insert('end', "\""+_output+"\" is not a valid ouput value.")
        listbox_l.see(END)

def clearMethod():
    ax.clear()
    ax.grid(True)
    ax.set_title("Realtime Hall voltage vs H Plot")
    ax.set_xlabel("Applied Field (Oe)")
    ax.set_ylabel("Lock-In X (mV)")
    ax.axis([-1, 1, -1, 1])
    
    canvas.draw()
    listbox_l.delete(0, END)
    
    print("clear all")

def quitMethod():

    amp = lockinAmp(func, sense, signal, freq)
    amp.dacOutput(0, 1)
    amp.dacOutput(0, 2)
    amp.dacOutput(0, 3)
    amp.dacOutput(0, 4)

    keith=Keithley2400(0)
    keith.setCurrent(0)
    keith.outputOff()

    listbox_l.insert('end', "All fields set to zero.")
    listbox_l.see(END)
    
    global root

    root.quit()

def createWidgit():

    global ax, canvas, listbox_l, result, func, frame, sense

    fig = pylab.figure(1)

    ax = fig.add_subplot(111)
    ax.grid(True)
    ax.set_title("Realtime Hall voltage vs H Plot")
    ax.set_xlabel("Applied Field (Oe)")
    ax.set_ylabel("Lock-In X (mV)")
    ax.axis([-1, 1, -1, 1])


    content = ttk.Frame(root, padding=(3,3,12,12))

    #plotting area 
    frame = ttk.Frame(content, borderwidth=0, relief="sunken",padding=(3,3,12,12))
    frame_setting = ttk.Frame(content)
    frame_information = ttk.Frame(content, padding = (3,3,12,12)) 
    frame_buttomArea = ttk.Frame(content)

    entry_number = ttk.Entry(frame_setting); entry_number.insert(0,"10")
    entry_interval = ttk.Entry(frame_setting);entry_interval.insert(0,"470.58")
    entry_output = ttk.Entry(frame_setting); entry_output.insert(0,"200")
    entry_average = ttk.Entry(frame_setting); entry_average.insert(0,"3")
    entry_signal = ttk.Entry(frame_setting); entry_signal.insert(0,"1")
    entry_frequency = ttk.Entry(frame_setting); entry_frequency.insert(0,"1171")
    entry_current = ttk.Entry(frame_setting); entry_current.insert(0,"0")

    value = tkinter.StringVar() #mode
    value2 = tkinter.StringVar() #sensitivity
    value3 = tkinter.IntVar() #dac
    value4 = tkinter.StringVar() #keithOut

    mode = ["1st","1st","2nd"]
    sensitivity = ["10mV","1mV","2mV","5mV","10mV","20mV","50mV","100mV","200mV","10uV","20uV","50uV","100uV"]
    dac = [1,1,2,3,4]
    keithOut = ["OFF", "ON", "OFF"]

    option_mode = ttk.OptionMenu(frame_setting, value, *mode, command = optionMethod)
    option_sensitivity = ttk.OptionMenu(frame_setting, value2, *sensitivity, command = senseMethod)
    option_dac = ttk.OptionMenu(frame_setting, value3, *dac, command = dacMethod)
    option_keithOut = ttk.OptionMenu(frame_setting, value4, *keithOut, command = keithOutMethod)

    listbox_l = Listbox(frame_information,height=5)
    scrollbar_s = ttk.Scrollbar(frame_information, orient=VERTICAL, command=listbox_l.yview)

    label_mode = ttk.Label(frame_setting, text="Voltage Harmonic Mode:")
    label_sensitivity = ttk.Label(frame_setting, text="Sensitivity:")
    label_interval = ttk.Label(frame_setting, text="Calib. H(Oe)/DAC(V):") 
    label_number = ttk.Label(frame_setting, text="Number:")
    label_output = ttk.Label(frame_setting, text="Field (Oe):")
    label_average = ttk.Label(frame_setting, text="Averages:")
    label_signal = ttk.Label(frame_setting, text="Lock-in OSC (V):")
    label_frequency = ttk.Label(frame_setting, text="Lock-in Freq (Hz):")
    label_dac = ttk.Label(frame_setting, text="DAC Channel:")
    label_keithOut = ttk.Label(frame_setting, text="Keithley2400 Output:")
    label_current = ttk.Label(frame_setting, text="Current (mA):")
    
    
    button_measure = ttk.Button(frame_buttomArea, text ="Measure", command = lambda : measureMethod(entry_interval.get(),entry_number.get(),entry_output.get(),entry_average.get(),entry_signal.get(),entry_frequency.get(),entry_current.get()))

    button_save  = ttk.Button(frame_buttomArea, text="Save", command = saveMethod)
    button_quit = ttk.Button(frame_buttomArea, text="Quit", command = quitMethod)
    button_output = ttk.Button(frame_buttomArea, text="Output", command = lambda : outputMethod(entry_interval.get(),entry_output.get(),entry_signal.get(),entry_frequency.get()))
    button_clear = ttk.Button(frame_buttomArea, text="Clear", command = clearMethod)

    #Attatch Plot 
    canvas = FigureCanvasTkAgg(fig, frame)
    canvas.get_tk_widget().grid(row=0, column =0, pady =0, padx =0,sticky='nsew')
    content.grid(column=0, row=0, sticky=(N, S, E, W))
    frame.grid(column=0, row=0, columnspan=3, rowspan=25, sticky=(N, S, E, W))


    frame_setting.grid(column=3, row=0, columnspan=2, rowspan=25, sticky=(N, S, E, W))

    #Frame setting grid
    label_mode.grid(column=0, row=1, columnspan=2, sticky=(N, W), padx=5)
    option_mode.grid(column=0, row=2, columnspan=2, sticky=(N, W), padx=5)
    label_sensitivity.grid(column=0, row=3, columnspan=2, sticky=(N, W), padx=5)
    option_sensitivity.grid(column=0, row=4, columnspan=2, sticky=(N, W), padx=5)
    label_interval.grid(column=0, row=5, columnspan=2, sticky=(N, W), padx=5)
    entry_interval.grid(column=0, row=6, columnspan=2, sticky=(N, W), padx=5)
    label_number.grid(column=0, row=7, columnspan=2, sticky=(N, W), padx=5)
    entry_number.grid(column=0, row=8, columnspan=2, sticky=(N, W), padx=5)
    label_output.grid(column=0, row=9, columnspan=2, sticky=(N, W), padx=5)
    entry_output.grid(column=0, row=10, columnspan=2, sticky=(N, W), padx=5)
    label_average.grid(column=0, row=11, columnspan=2, sticky=(N, W), padx=5)
    entry_average.grid(column=0, row=12, columnspan=2, sticky=(N, W), padx=5)
    label_signal.grid(column=0, row=13, columnspan=2, sticky=(N, W), padx=5)
    entry_signal.grid(column=0, row=14, columnspan=2, sticky=(N, W), padx=5)
    label_frequency.grid(column=0, row=15, columnspan=2, sticky=(N, W), padx=5)
    entry_frequency.grid(column=0, row=16, columnspan=2, sticky=(N, W), padx=5)
    label_dac.grid(column=0, row=17, columnspan=2, sticky=(N, W), padx=5)
    option_dac.grid(column=0, row=18, columnspan=2, sticky=(N, W), padx=5)
    label_keithOut.grid(column=0, row=19, columnspan=2, sticky=(N, W), padx=5)
    option_keithOut.grid(column=0, row=20, columnspan=2, sticky=(N, W), padx=5)
    label_current.grid(column=0, row=21, columnspan=2, sticky=(N, W), padx=5)
    entry_current.grid(column=0, row=22, columnspan=2, sticky=(N, W), padx=5)


    frame_information.grid(column=0, row=25,columnspan=3,sticky=(N,W,E,S))

    listbox_l.grid(column=0, row=0,columnspan=3,sticky=(N,W,E,S))
    scrollbar_s.grid(column=1, row=0, sticky=(N,S))

    listbox_l['yscrollcommand'] = scrollbar_s.set

    frame_information.grid_columnconfigure(0, weight=1)
    frame_information.grid_rowconfigure(0, weight=1)



    frame_buttomArea.grid(column =3, row=25,columnspan=2,sticky=(N, S, E, W))

    button_output.grid(column=0, row=0,columnspan = 2,sticky=(N, S, E, W))
    button_measure.grid(column =0, row=1, columnspan = 2,sticky=(N, S, E, W))
    button_clear.grid(column = 0, row = 2, columnspan = 2, sticky=(N,S,E,W))
    button_save.grid(column=0, row=3,columnspan = 1,sticky=(N, S, E, W))
    button_quit.grid(column=1, row=3,columnspan = 1,sticky=(N, S, E, W))


    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    content.columnconfigure(0, weight=3)
    content.columnconfigure(1, weight=3)
    content.columnconfigure(2, weight=3)
    content.columnconfigure(3, weight=1)
    content.columnconfigure(4, weight=1)
    content.rowconfigure(1, weight=1)

if __name__ == '__main__':
    main()





