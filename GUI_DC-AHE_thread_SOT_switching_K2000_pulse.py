
#********************** 2017/12/29 Version ********************#

# Note: Threading added in the measureMethod()
# Note: The listbox will now always show the latest measured data
# Note: Threading can avoid non-responsive problem, but will also cause
#       the intereference by clicking other buttons during measurement.
# Note: Keithley current option added.
# Note: All output will be shut down by clicking quit
# Note: Create the K2400 current stepping function
# Note: Voltage Protection added

#******************** 2017/07/16 K2400 pulse ******************#

# Note: Re-desgin pannel such that one can input pulse parameters
# Note: Remove lock-in stuff

#********************** 2018/01/12 Version ********************#
# Note: Cleaned up code for easier reading
# Note: Unnecessary variables removed
# Note: Amplifier protection added
# Note: Lock-in stuff removed along with Keithley 2400 stuff
# Note: Hz removed from measureMethod, Hz options commented out of GUI
# Note: outputMethod now outputs Hx field, not Hz
# Note: Save function updated to include sample name and initial measured resistance.
# Note: Read me added

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
from keithley import Keithley
import time
import multiprocessing
import threading
from datetime import datetime

root = Tk()

def main():

    global result, func, average, sense, DAC, DACx, signal, freq, directory, dot_size, dot_edge

    directory = os.getcwd()

    func='1st' #Set a default mode (1st or 2nd)
    sense='10mV' #Set a default sensitivity range (mV or uV)
    DAC=2 #Set a default DAC output channel for Hz
    DACx=3 #Set a default DAC output channel for Hx
    signal=1 #Set a default OSC signal voltage (V)
    freq=1171 #Set a default OSC frequency (Hz)

    read_me = 'This program uses Keithley2000 to run varying strength current pulses to the sample AND to measure SOT switching of the sample. \
    A Lock-in Amp is used to generate varying Hx fields to test current switching in. Hz is currently not used.'

    print(read_me)

    dot_size=10 #Set a default data dot size
    dot_edge=0.5 #Set a default data dot edge width
    
    result=['']
    values_y=[]
    values_x=[]

    createWidgit()

    root.protocol('WM_DELETE_WINDOW', quit) 
    root.mainloop()

#************************Main End Here***************************#

#Runs varying strength current pulses using Keithley2000 over a range of Hx fields. 
def measureMethod(_current, _step, _Hx, _dHx, _intervalx, _sense, _switchwidth, _sensewidth, _switchsense, _period, _sample):
    
    #i=float(_interval) #Hz calibration factor
    ix=float(_intervalx) #Hx calibration factor

    def event():

        Hx_start=float(_Hx) #Hx starting field
        Hx_end=float(_Hx)*(-1) #Hx ending field
        Hx_step=float(_dHx) #Hx step

        keith2000=Keithley(f) #Initiate K2000
        amp = lockinAmp(func, sense, signal, freq) #Initiate Lock-in

        while Hx_start>=Hx_end:

            amp.dacOutput((Hx_start/ix), DACx)

            current_max=float(_current)
            current_min=float(_current)*(-1)
            current_step=float(_step)
    
            #while current_start>=current_end:

            ax.clear()
            ax.grid(True)
            ax.set_title("Realtime Resistance vs I Plot")
            ax.set_xlabel("Applied Current (mA)")
            ax.set_ylabel("Hall Resistance (Ohm)")

            listbox_l.insert('end',"Now measuring with Hx = %f (Oe)" %Hx_start)
            listbox_l.see(END)
            
            #Prepare data entries
            global values_x, values_y, result

            values_y=[]
            values_x=[]
            result=[]
            
            #Setup K2400 for current output and resistance measurement

            current=0 #starting current amplitude
            current_sense=float(_sense) #sensing current amplitude (mA)

            keith.fourWireOff() #Set 2-wire mode
            keith.setCurrent(current_sense) #Use 2-wire method to measure DC resistance 
            keith.outputOn()

            index=1
            data=[]

            while index<=5: #Average of five measurements
                data=data+keith.measureOnce()
                index+=1
        
            print("Measured current: %f mA" %(1000*data[2]))
            print("Measured voltage: %f V" %data[1])
            print("Measured resistance: %f Ohm" %(data[1]/data[2]))

            save = (data[1]/data[2])

            keith.outputOff()

            #Pulse train parameters
            write_pulse_width=float(_switchwidth) #switching pulse width
            read_pulse_width=float(_sensewidth) #sensing pulse width
            write_read_pause=float(_switchsense) #interval between switching and sesnsing pulses
            period=float(_period) #interval between stepping events

            keith.outputOn()
    
            while current < current_max :

                #keith.outputOn()
                keith.setCurrent(current) # Set switching current
                time.sleep(write_pulse_width)
                keith.setCurrent(0) # Reduce current amplitude to zero
                #keith.outputOff()

                time.sleep(write_read_pause)

                #keith.outputOn()
                keith.setCurrent(current_sense) # Set sensing current
                time.sleep(read_pulse_width)
                data=keith2000.measureOnce()
                keith.setCurrent(0) # Reduce current amplitude to zero
                #keith.outputOff()
                
                tmp=double(1000*data[1]/current_sense) # Voltage from K2000 / sensing current
                result.append(tmp)
                values_y.append(tmp)
                values_x.append(current)
                #ax.scatter(values_x[-1], values_y[-1], s=50, alpha=0.5)
                ax.plot(values_x, values_y,'b-o', ms=dot_size, mew=dot_edge, alpha=0.5)
                canvas.draw()
                listbox_l.insert('end', tmp)
                current+=current_step
                listbox_l.see(END)

                time.sleep(period)

            while current > current_min :

                #keith.outputOn()
                keith.setCurrent(current) # Set switching current
                time.sleep(write_pulse_width)
                keith.setCurrent(0) # Reduce current amplitude to zero
                #keith.outputOff()

                time.sleep(write_read_pause)

                #keith.outputOn()
                keith.setCurrent(current_sense) # Set sensing current
                time.sleep(read_pulse_width)
                data=keith2000.measureOnce()
                keith.setCurrent(0) # Reduce current amplitude to zero
                #keith.outputOff()
                
                tmp=double(1000*data[1]/current_sense) # Voltage from K2000 / sensing current
                result.append(tmp)
                values_y.append(tmp)
                values_x.append(current)
                #ax.scatter(values_x[-1], values_y[-1], s=50, alpha=0.5)
                ax.plot(values_x, values_y,'b-o', ms=dot_size, mew=dot_edge, alpha=0.5)
                canvas.draw()
                listbox_l.insert('end', tmp)
                current-=current_step
                listbox_l.see(END)

                time.sleep(period)

            while current <= 0 :

                #keith.outputOn()
                keith.setCurrent(current) # Set switching current
                time.sleep(write_pulse_width)
                keith.setCurrent(0) # Reduce current amplitude to zero
                #keith.outputOff()

                time.sleep(write_read_pause)

                #keith.outputOn()
                keith.setCurrent(current_sense) # Set sensing current
                time.sleep(read_pulse_width)
                data=keith2000.measureOnce()
                keith.setCurrent(0) # Reduce current amplitude to zero
                #keith.outputOff()
                
                tmp=double(1000*data[1]/current_sense) # Voltage from K2000 / sensing current
                result.append(tmp)
                values_y.append(tmp)
                values_x.append(current)
                #ax.scatter(values_x[-1], values_y[-1], s=50, alpha=0.5)
                ax.plot(values_x, values_y,'b-o', ms=dot_size, mew=dot_edge, alpha=0.5)
                canvas.draw()
                listbox_l.insert('end', tmp)
                current+=current_step
                listbox_l.see(END)

                time.sleep(period)

            #scat=ax.scatter(values_x, values_y, s=50, alpha=0.5)
            #canvas.draw()

            stamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
            listbox_l.insert('end', str(stamp))

            file = open(str(directory)+'/'+str(_sample)+"SOT_switching_"+str(Hx_start)+"Oe_"+str(stamp), "w")
            file.write("" + str(_sample) + "\n")
            file.write("Applied in-plane field: "+str(Hx_start)+"(Oe)\n\n")
            file.write("Initial resistance: "+str(save)+"Ohm \n")
            file.write("Number"+" "+"Current(mA)"+" "+"Resistance(Ohm)"+"\n")

            cnt=1
            #output all data 
            for a in range(len(values_y)):

                file.write(str(cnt)+" "+str(values_x[a])+" "+str(values_y[a])+"\n")
                cnt +=1

            file.closed

            listbox_l.insert('end', "The Measurement data is saved.")
            listbox_l.see(END)

            #keith.outputOff()

            time.sleep(1) #Sleep between each scan

            Hx_start=Hx_start-Hx_step

        amp.dacOutput(0, DACx)
        amp.dacOutput(0, DAC)

        keith.fourWireOff()
        keith.outputOff()
        
        listbox_l.insert('end',"Measurement finished")
        listbox_l.see(END)

    if (double(_output)/i)< 1 and (float(_Hx)/ix)<12:
        
        th = threading.Thread(target=event)
        th.start()

    else:
        
        listbox_l.insert('end',"Your output field is TOO LARGE!")
        listbox_l.see(END)
        print("Your output field is TOO LARGE!")

# DAC: Which DAC output channel for Hz (Out-of-plane field)
def dacMethod(val):

    global DAC

    DAC = val

    print("DAC channel for Hz:",DAC)
    print("Don't forget to change the calibration factor H(Oe)/DAC(V)")

# DAC: Which DAC output channel for Hx (In-plane field)
def dacxMethod(val):

    global DACx

    DACx = val

    print("DAC channel for Hx:",DACx)
    print("Don't forget to change the calibration factor H(Oe)/DAC(V)")


def dirMethod():

    global directory

    directory = filedialog.askdirectory()
    
    listbox_l.insert('end', directory)
    listbox_l.see(END)

#outputs Hx field!
def outputMethod(_interval, _output):

    i=float(_interval)
    
    amp = lockinAmp(func, sense, signal, freq)
    
    if _output.replace('.','').replace('-','').isdigit() :
        #print(entry_output.get())
        amp.dacOutput((double(_output)/i), DAC)

        listbox_l.insert('end', "Single output Hx field: "+_output+" Oe.")
        listbox_l.see(END)
    else:
        listbox_l.insert('end', "\""+_output+"\" is not a valid Hx output value.")
        listbox_l.see(END)

def clearMethod():
    
    ax.clear()
    ax.grid(True)
    ax.set_title("Realtime Resistance vs I Plot")
    ax.set_xlabel("Applied Current (mA)")
    ax.set_ylabel("Hall Resistance (Ohm)")
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

    listbox_l.insert('end', "All fields set to zero.")
    listbox_l.see(END)
    time.sleep(1)
    
    global root

    root.quit()

def createWidgit():

    global ax, canvas, listbox_l, result, func, frame, sense

    fig = pylab.figure(1)

    ax = fig.add_subplot(111)
    ax.grid(True)
    ax.set_title("Realtime Resistance vs I Plot")
    ax.set_xlabel("Applied Current (mA)")
    ax.set_ylabel("Hall Resistance (Ohm)")
    ax.axis([-1, 1, -1, 1])


    content = ttk.Frame(root, padding=(3,3,12,12))

    #plotting area 
    frame = ttk.Frame(content, borderwidth=0, relief="sunken",padding=(3,3,12,12))
    frame_setting = ttk.Frame(content)
    frame_information = ttk.Frame(content, padding = (3,3,12,12)) 
    frame_buttomArea = ttk.Frame(content)

    #Save Variables
    entry_sample = ttk.Entry(frame_information); entry_sample.insert(0, "sample name")

    #Function Variables
    #entry_interval = ttk.Entry(frame_setting);entry_interval.insert(0,"1022")
    #entry_output = ttk.Entry(frame_setting); entry_output.insert(0,"200")
    entry_sense = ttk.Entry(frame_setting); entry_sense.insert(0,"1") #K2400 sensing current
    entry_current = ttk.Entry(frame_setting); entry_current.insert(0,"0")
    entry_step = ttk.Entry(frame_setting); entry_step.insert(0,"0.5")
    entry_Hx = ttk.Entry(frame_setting); entry_Hx.insert(0,"0")
    entry_dHx = ttk.Entry(frame_setting); entry_dHx.insert(0,"100")
    entry_intervalx = ttk.Entry(frame_setting);entry_intervalx.insert(0,"396.59")
    entry_switch_width = ttk.Entry(frame_setting);entry_switch_width.insert(0,"0.05")
    entry_sense_width = ttk.Entry(frame_setting);entry_sense_width.insert(0,"0.05")
    entry_switch_sense = ttk.Entry(frame_setting);entry_switch_sense.insert(0,"0.05")
    entry_period = ttk.Entry(frame_setting);entry_period.insert(0,"0.05")

    value3 = tkinter.IntVar() #dac
    value4 = tkinter.IntVar() #dacx

    #dac = [2,1,2,3,4]
    dacx = [3,1,2,3,4]

    #option_dac = ttk.OptionMenu(frame_setting, value3, *dac, command = dacMethod)
    option_dacx = ttk.OptionMenu(frame_setting, value4, *dacx, command = dacxMethod)

    listbox_l = Listbox(frame_information,height=5)
    scrollbar_s = ttk.Scrollbar(frame_information, orient=VERTICAL, command=listbox_l.yview)

    #label_interval = ttk.Label(frame_setting, text="Hz(Oe)/DAC(V):") #calibration factor
    #label_output = ttk.Label(frame_setting, text="Hz field (Oe):")
    label_sense = ttk.Label(frame_setting, text="Sense current (mA):")
    #label_dac = ttk.Label(frame_setting, text="Hz DAC Channel:")
    label_dacx = ttk.Label(frame_setting, text="Hx DAC Channel:")
    label_current = ttk.Label(frame_setting, text="Write current (mA):")
    label_step = ttk.Label(frame_setting, text="Current step (mA):")
    label_Hx = ttk.Label(frame_setting, text="Hx field (Oe):")
    label_dHx = ttk.Label(frame_setting, text="Hx step (Oe):")
    label_intervalx = ttk.Label(frame_setting, text="Hx(Oe)/DAC(V):")
    label_switch_width = ttk.Label(frame_setting, text="Write pulse width (s):")
    label_sense_width = ttk.Label(frame_setting, text="Sense pulse width (s):")
    label_switch_sense = ttk.Label(frame_setting, text="Write-sense pause (s):")
    label_period = ttk.Label(frame_setting, text="Period (s):")
    label_empty = ttk.Label(frame_setting, text="")
    
    button_measure = ttk.Button(frame_buttomArea, text ="Measure",\
     command = lambda : measureMethod(entry_current.get(),entry_step.get(),entry_Hx.get(),\
        entry_dHx.get(),entry_intervalx.get(),entry_sense.get(),entry_switch_width.get(),\
        entry_sense_width.get(),entry_switch_sense.get(),entry_period.get(),entry_sample.get()))

    button_dir  = ttk.Button(frame_buttomArea, text="Change directory", command = dirMethod)
    button_quit = ttk.Button(frame_buttomArea, text="Quit", command = quitMethod)
    button_output = ttk.Button(frame_buttomArea, text="Output", command = lambda : outputMethod(entry_intervalx.get(),entry_Hx.get()))
    button_clear = ttk.Button(frame_buttomArea, text="Clear", command = clearMethod)

    #Attatch Plot 
    canvas = FigureCanvasTkAgg(fig, frame)
    canvas.get_tk_widget().grid(row=0, column =0, pady =0, padx =0,sticky='nsew')
    content.grid(column=0, row=0, sticky=(N, S, E, W))
    frame.grid(column=0, row=0, columnspan=3, rowspan=30, sticky=(N, S, E, W))


    frame_setting.grid(column=3, row=0, columnspan=2, rowspan=30, sticky=(N, S, E, W))

    #Frame setting grid
    
    #Save setings
    label_sample = ttk.Label(frame_information, text = "Sample Name")

    #Hz settings
    #label_dac.grid(column=0, row=1, columnspan=2, sticky=(N, W), padx=5)
    #option_dac.grid(column=0, row=2, columnspan=2, sticky=(N, W), padx=5)
    #label_interval.grid(column=0, row=3, columnspan=2, sticky=(N, W), padx=5)
    #entry_interval.grid(column=0, row=4, columnspan=2, sticky=(N, W), padx=5)
    #label_output.grid(column=0, row=5, columnspan=2, sticky=(N, W), padx=5)
    #entry_output.grid(column=0, row=6, columnspan=2, sticky=(N, W), padx=5)

    #Hx settings
    label_dacx.grid(column=0, row=7, columnspan=2, sticky=(N, W), padx=5)
    option_dacx.grid(column=0, row=8, columnspan=2, sticky=(N, W), padx=5)
    label_intervalx.grid(column=0, row=9, columnspan=2, sticky=(N, W), padx=5)
    entry_intervalx.grid(column=0, row=10, columnspan=2, sticky=(N, W), padx=5)
    label_Hx.grid(column=0, row=11, columnspan=2, sticky=(N, W), padx=5)
    entry_Hx.grid(column=0, row=12, columnspan=2, sticky=(N, W), padx=5)
    label_dHx.grid(column=0, row=13, columnspan=2, sticky=(N, W), padx=5)
    entry_dHx.grid(column=0, row=14, columnspan=2, sticky=(N, W), padx=5)

    #Current settings
    label_sense.grid(column=0, row=15, columnspan=2, sticky=(N, W), padx=5)
    entry_sense.grid(column=0, row=16, columnspan=2, sticky=(N, W), padx=5)
    label_current.grid(column=0, row=17, columnspan=2, sticky=(N, W), padx=5)
    entry_current.grid(column=0, row=18, columnspan=2, sticky=(N, W), padx=5)
    label_step.grid(column=0, row=19, columnspan=2, sticky=(N, W), padx=5)
    entry_step.grid(column=0, row=20, columnspan=2, sticky=(N, W), padx=5)

    label_switch_width.grid(column=0, row=21, columnspan=2, sticky=(N, W), padx=5)
    entry_switch_width.grid(column=0, row=22, columnspan=2, sticky=(N, W), padx=5)
    label_sense_width.grid(column=0, row=23, columnspan=2, sticky=(N, W), padx=5)
    entry_sense_width.grid(column=0, row=24, columnspan=2, sticky=(N, W), padx=5)
    label_switch_sense.grid(column=0, row=25, columnspan=2, sticky=(N, W), padx=5)
    entry_switch_sense.grid(column=0, row=26, columnspan=2, sticky=(N, W), padx=5)
    label_period.grid(column=0, row=27, columnspan=2, sticky=(N, W), padx=5)
    entry_period.grid(column=0, row=28, columnspan=2, sticky=(N, W), padx=5)

    label_empty.grid(column=0, row=31, columnspan=2, sticky=(N, W), padx=5)


    frame_information.grid(column=0, row=31,columnspan=3,sticky=(N,W,E,S))

    listbox_l.grid(column=0, row=0,columnspan=3,sticky=(N,W,E,S))
    scrollbar_s.grid(column=1, row=0, sticky=(N,S))

    listbox_l['yscrollcommand'] = scrollbar_s.set

    label_sample.grid(column=0, row=2, columnspan=1, sticky=(N,W,E,S), padx=5)
    entry_sample.grid(column=0, row=3, columnspan=1, sticky=(N,W,E,S), padx=5)

    frame_information.grid_columnconfigure(0, weight=1)
    frame_information.grid_rowconfigure(0, weight=1)
    

    frame_buttomArea.grid(column =3, row=31,columnspan=2,sticky=(N, S, E, W))

    button_output.grid(column=0, row=0,columnspan = 2,sticky=(N, S, E, W))
    button_measure.grid(column =0, row=1, columnspan = 2,sticky=(N, S, E, W))
    button_clear.grid(column = 0, row = 3, columnspan = 1, sticky=(N, S, E, W))
    button_dir.grid(column=0, row=2,columnspan = 2,sticky=(N, S, E, W))
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





