
#********************** 2017/12/11 Version ********************#

# Note: Threading added in the measureMethod()
# Note: The listbox will now always show the latest measured data
# Note: Threading can avoid non-responsive problem, but will also cause
#       the intereference by clicking other buttons during measurement.
# Note: Keithley current option added.
# Note: All output will be shut down by clicking quit
# Note: Create the K2400 current stepping function

#********************** 2018/01/12 Version ********************#
# Note: Voltage Protection added 2017/12/19
# Note: Cleaned up code for easier reading
# Note: Unnecessary variables removed
# Note: Save function updated to include sample name and voltage sensitivity.
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
from Keithley2400_V import Keithley2400
import time
import multiprocessing
import threading
import pyscreenshot as ImageGrab

root = Tk()

def main():

    global result, func, average, sense, DAC, DACx, signal, freq, directory, dot_size, dot_edge, V_max

    directory = os.getcwd()

    func='1st' #Set a default mode (1st or 2nd)
    sense='10mV' #Set a default sensitivity range (mV or uV)
    DAC=2 #Set a default DAC output channel for Hz
    DACx=3 #Set a default DAC output channel for Hx
    signal=1 #Set a default OSC signal voltage (V)
    freq=1171 #Set a default OSC frequency (Hz)
    V_max=1 #Set a default maximum DAC output voltage (V) to protect DC-amp

    read_me = 'This program uses Keithley2400 to provide trigger pulses to the pulse generator. The Lock-in Amp measures\
    voltage of the sample after the current is applied.  The Lock-in Amp also provides varying strength Hx fields and a reset Hz field.'

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

#takes in two VOLT measurements, compares, returns whether switching occured or not
def compareSwitch(VOLT1, VOLT2, sensitivity):
    switched = False
    if abs(VOLT1 - VOLT2) >= sensitivity:
        switched = True

    return switched

# measures pulse switching events for a set number of pulses at a given Hx field strength. 
def measureMethod(_interval, _number, _output, _average, _signal, _frequency, _volt_sensitivity, \
	_step,_pulse_length,_rest_length,_Hx, _dHx, _intervalx, _pulse_amp, _sample, _pulse_duration, _Hx_init):

    #_pulse_length is length of pulse sent from Keithley 2400
    #_rest_length is trigger delay on Keithley 2400
    #_pulse_amp is the manually set value on the pulse generator
    #_pulse_duration is the manually set value on the pulse generator
    i=float(_interval) # Hz calibration factor
    ix=float(_intervalx) # Hx calibration factor
    number=int(_number) # number of times pulses are sent and measured per field strength
    average=int(_average) # number of measurements averaged by Lock-in Amp
    signal=float(_signal) # Lock-in Amp signal strength (MAX 5 V)
    freq=int(_frequency) # Lock-in Amp frequency (Hz)
    Hz=float(_output) # Hz field 
    Hx_end=float(_Hx) # Hx field final

    def event():

        Hx_start=float(_Hx_init) # Initial Hx field strength
        Hx_step=float(_dHx) # Hx step for loop

        keith=Keithley2400() #Initiate K2400
        amp = lockinAmp(func, sense, signal, freq) #Initiate Lock-in

        #Prepare data entries
        global values_x, values_y, result, dot_size, dot_edge

        values_y=[]
        values_x=[]
        result=[]
        dot_size=10 #Set a default data dot size
        dot_edge=0.5 #Set a default data dot edge width


        while Hx_start<=Hx_end:

            amp.dacOutput((Hx_start/ix), DACx)

            volt_sensitivity=float(_volt_sensitivity) # sensitivity requirement to count as successful switching event

            ax.clear()
            ax.grid(True)
            ax.set_title("Switching Probability vs Applied Field Plot")
            ax.set_xlabel("Applied Field (Oe)")
            ax.set_ylabel("Switching Probability (HV %)")

            listbox_l.insert('end',"Now measuring with Hx = %f (Oe)" %Hx_start)
            listbox_l.see(END)

            index=1
            data=[]



            #Setup Keithley for Voltage Pulse
            voltage = 0
            voltage_max = 3
            #initialize while loop, set count to compare
            n = 0
            total = 0

            trigger_delay=float(_rest_length)
            source_delay=float(_pulse_length)

            while n < number :

                #RUN setZfield 
                amp.dacOutput((Hz/i), DAC)
                time.sleep(1)
                amp.dacOutput(0, DAC)
                time.sleep(2) #necessary to allow reset field to clear before measurement is taken
                #voltage running in X direction
                take1 = 1000*double(amp.readX(average)) 
                #RUN setAppliedField
                amp.dacOutput((Hx_start/ix), DACx)
                #RUN triggerPulse
                keith.vpulse(2,voltage_max, trigger_delay, source_delay)
                #reset AppliedField
                amp.dacOutput(0, DACx)
                #voltage running in X direction
                take2 = 1000*double(amp.readX(average)) 
                #RUN compareSwitch
                if compareSwitch(take1, take2, volt_sensitivity) == True:
                    total += 1

                n += 1

            tmp = (total / n) * 100
            result.append(tmp)
            values_y.append(tmp)
            values_x.append(Hx_start)
            ax.plot(values_x, values_y,'b-o', ms=dot_size, mew=dot_edge, alpha=0.5)
            canvas.draw()
            listbox_l.insert('end', tmp)

            listbox_l.see(END)

            keith.outputOff()

            time.sleep(1) #Sleep between each scan

            Hx_start=Hx_start+Hx_step

        amp.dacOutput(0, DACx)
        amp.dacOutput(0, DAC)
        listbox_l.insert('end',"Measurement finished")
        listbox_l.see(END)


        file = open(str(directory)+"/"+str(_sample)+str(Hx_end)+"Oe"+str(_pulse_amp)+\
        	"dB"+str(_pulse_duration)+"ns", "w")
        file.write("" + str(_sample))
        file.write("Pulse Generator set to: " + str(_pulse_amp)+"(dB)"+str(_pulse_duration)+"(ns)\n")
        file.write("The voltage sensitivity was set to " + str(_volt_sensitivity) + "(mV)\n")
        file.write("Applied in-plane field: "+str(Hx_end)+"(Oe)\n\n")
        file.write("Number"+" "+"Field(Oe)"+" "+"Voltage(mV)"+"\n")

        cnt=1
        #output all data
        for a in range(len(values_y)):

            file.write(str(cnt)+" "+str(values_x[a])+" "+str(values_y[a])+"\n")
            cnt +=1

        file.closed

        listbox_l.insert('end', "The Measurement data is saved.")
        listbox_l.see(END)

    if (Hz/i)<V_max and (Hx_end/ix)<12*V_max:

    	th = threading.Thread(target=event)
    	th.start()

    else:

    	listbox_l.insert('end',"Your output field is TOO LARGE!")
    	listbox_l.see(END)
    	print("Your output field is TOO LARGE!")


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
    ax.set_title("Probability Switching vs Applied Field Plot")
    ax.set_xlabel("Applied Field (Oe)")
    ax.set_ylabel("Probability Switching (HV %)")
    ax.axis([0, 1, 0, 1])

    canvas.draw()
    listbox_l.delete(0, END)

    print("clear all")

def quitMethod():

    amp = lockinAmp(func, sense, signal, freq)
    amp.dacOutput(0, 1)
    amp.dacOutput(0, 2)
    amp.dacOutput(0, 3)
    amp.dacOutput(0, 4)

    keith=Keithley2400()
    keith.setVoltage(0)
    keith.outputOff()

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
    ax.set_title("Probability Switching vs Applied Field Plot")
    ax.set_xlabel("Applied Field (Oe)")
    ax.set_ylabel("Probability Switching (HV %)")
    ax.axis([0, 1, 0, 1])


    content = ttk.Frame(root, padding=(3,3,12,12))

    #plotting area
    frame = ttk.Frame(content, borderwidth=0, relief="sunken",padding=(3,3,12,12))
    frame_setting = ttk.Frame(content)
    frame_information = ttk.Frame(content, padding = (3,3,12,12))
    frame_buttomArea = ttk.Frame(content)

    #save entries
    entry_sample = ttk.Entry(frame_information); entry_sample.insert(0, "sample name")
    entry_pulse_duration = ttk.Entry(frame_information); entry_pulse_duration.insert(0, "100")
    entry_pulse_amp = ttk.Entry(frame_information); entry_pulse_amp.insert(0, "10")

    #value entries
    entry_sensitivity = ttk.Entry(frame_setting); entry_sensitivity.insert(0, "50")
    entry_number = ttk.Entry(frame_setting); entry_number.insert(0,"1")
    entry_interval = ttk.Entry(frame_setting);entry_interval.insert(0,"1022")
    entry_output = ttk.Entry(frame_setting); entry_output.insert(0,"200")
    entry_average = ttk.Entry(frame_setting); entry_average.insert(0,"10")
    entry_signal = ttk.Entry(frame_setting); entry_signal.insert(0,"5")
    entry_frequency = ttk.Entry(frame_setting); entry_frequency.insert(0,"1171")
    entry_volt_sensitivity = ttk.Entry(frame_setting); entry_volt_sensitivity.insert(0,"10")
    entry_step = ttk.Entry(frame_setting); entry_step.insert(0,"0.5")
    entry_pulse_length = ttk.Entry(frame_setting); entry_pulse_length.insert(0,"0.01")
    entry_rest_length = ttk.Entry(frame_setting); entry_rest_length.insert(0,"0.01")
    entry_Hx_init = ttk.Entry(frame_setting); entry_Hx_init.insert(0,"0")
    entry_Hx = ttk.Entry(frame_setting); entry_Hx.insert(0,"100")
    entry_dHx = ttk.Entry(frame_setting); entry_dHx.insert(0,"10")
    entry_intervalx = ttk.Entry(frame_setting);entry_intervalx.insert(0,"396.59")

    value = tkinter.StringVar() #mode
    value2 = tkinter.StringVar() #sensitivity
    value3 = tkinter.IntVar() #dac
    value4 = tkinter.StringVar() #keithOut

    mode = ["1st","1st","2nd"]
    sensitivity = ["10mV","1mV","2mV","5mV","10mV","20mV","50mV","100mV","200mV","10uV","20uV","50uV","100uV"]
    dac = [2,1,2,3,4]
    dacx = [3,1,2,3,4]

    option_mode = ttk.OptionMenu(frame_setting, value, *mode, command = optionMethod)
    option_sensitivity = ttk.OptionMenu(frame_setting, value2, *sensitivity, command = senseMethod)
    option_dac = ttk.OptionMenu(frame_setting, value3, *dac, command = dacMethod)
    option_dacx = ttk.OptionMenu(frame_setting, value4, *dacx, command = dacxMethod)

    listbox_l = Listbox(frame_information,height=5)
    scrollbar_s = ttk.Scrollbar(frame_information, orient=VERTICAL, command=listbox_l.yview)

    #save file variables
    label_sample = ttk.Label(frame_information, text = "Sample Name")
    label_pulse_duration = ttk.Label(frame_information, text = "Pulse Duration (ns)")
    label_pulse_amp = ttk.Label(frame_information, text = "Pulse Amp (dB)")


    label_mode = ttk.Label(frame_setting, text="Harmonic mode:")
    label_sensitivity = ttk.Label(frame_setting, text="Sensitivity:")
    label_interval = ttk.Label(frame_setting, text="Hz(Oe)/DAC(V):") #calibration factor
    label_number = ttk.Label(frame_setting, text="Points per scan:")
    label_output = ttk.Label(frame_setting, text="Hz field (Oe):")
    label_average = ttk.Label(frame_setting, text="Averages:")
    label_signal = ttk.Label(frame_setting, text="Lock-in OSC (V):")
    label_frequency = ttk.Label(frame_setting, text="Lock-in freq (Hz):")
    label_dac = ttk.Label(frame_setting, text="Hz DAC Channel:")
    label_dacx = ttk.Label(frame_setting, text="Hx DAC Channel:")
    label_volt_sensitivity = ttk.Label(frame_setting, text="Voltage Sensitivity (mV):")
    label_step = ttk.Label(frame_setting, text="Current step (mA):")
    label_pulse_length = ttk.Label(frame_setting, text="Pulse Length(s)")
    label_rest_length= ttk.Label(frame_setting, text="Rest Length(s)")
    label_Hx_init = ttk.Label(frame_setting, text="Hx Initial field (Oe):")
    label_Hx = ttk.Label(frame_setting, text="Hx field (Oe):")
    label_dHx = ttk.Label(frame_setting, text="Hx step (Oe):")
    label_intervalx = ttk.Label(frame_setting, text="Hx(Oe)/DAC(V):")
    label_empty = ttk.Label(frame_setting, text="")


    button_measure = ttk.Button(frame_buttomArea, text ="Measure", \
    	command = lambda : measureMethod(entry_interval.get(), entry_number.get(), entry_output.get(), \
    		entry_average.get(), entry_signal.get(), entry_frequency.get(), entry_volt_sensitivity.get(), \
    		entry_step.get(), entry_pulse_length.get(), entry_rest_length.get(), entry_Hx.get(), \
    		entry_dHx.get(), entry_intervalx.get(), entry_pulse_amp.get(), entry_sample.get(), \
    		entry_pulse_duration.get(), entry_Hx_init.get()))

    button_dir  = ttk.Button(frame_buttomArea, text="Change directory", command = dirMethod)
    button_quit = ttk.Button(frame_buttomArea, text="Quit", command = quitMethod)
    button_output = ttk.Button(frame_buttomArea, text="Output", command = lambda : \
    	outputMethod(entry_interval.get(),entry_output.get(),entry_signal.get(),entry_frequency.get()))
    button_clear = ttk.Button(frame_buttomArea, text="Clear", command = clearMethod)

    #Attatch Plot
    canvas = FigureCanvasTkAgg(fig, frame)
    canvas.get_tk_widget().grid(row=0, column =0, pady =0, padx =0,sticky='nsew')
    content.grid(column=0, row=0, sticky=(N, S, E, W))
    frame.grid(column=0, row=0, columnspan=3, rowspan=30, sticky=(N, S, E, W))


    frame_setting.grid(column=3, row=0, columnspan=2, rowspan=30, sticky=(N, S, E, W))

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
    label_dacx.grid(column=0, row=19, columnspan=2, sticky=(N, W), padx=5)
    option_dacx.grid(column=0, row=20, columnspan=2, sticky=(N, W), padx=5)
    label_volt_sensitivity.grid(column=0, row=21, columnspan=2, sticky=(N, W), padx=5)
    entry_volt_sensitivity.grid(column=0, row=22, columnspan=2, sticky=(N, W), padx=5)
    label_pulse_length.grid(column=0, row=25, columnspan=2, sticky=(N, W), padx=5)
    entry_pulse_length.grid(column=0, row=26, columnspan=2, sticky=(N, W), padx=5)
    label_rest_length.grid(column=0, row=27, columnspan=2, sticky=(N, W), padx=5)
    entry_rest_length.grid(column=0, row=28, columnspan=2, sticky=(N, W), padx=5)
    label_Hx_init.grid(column=0, row=29, columnspan=2, sticky=(N, W), padx=5)
    entry_Hx_init.grid(column=0, row=30, columnspan=2, sticky=(N, W), padx=5)
    label_Hx.grid(column=0, row=31, columnspan=2, sticky=(N, W), padx=5)
    entry_Hx.grid(column=0, row=32, columnspan=2, sticky=(N, W), padx=5)
    label_dHx.grid(column=0, row=33, columnspan=2, sticky=(N, W), padx=5)
    entry_dHx.grid(column=0, row=34, columnspan=2, sticky=(N, W), padx=5)
    label_intervalx.grid(column=0, row=35, columnspan=2, sticky=(N, W), padx=5)
    entry_intervalx.grid(column=0, row=36, columnspan=2, sticky=(N, W), padx=5)

    label_empty.grid(column=0, row=37, columnspan=2, sticky=(N, W), padx=5)


    frame_information.grid(column=0, row=25,columnspan=3,sticky=(N,W,E,S))

    listbox_l.grid(column=0, row=0,columnspan=3,sticky=(N,W,E,S))
    scrollbar_s.grid(column=1, row=0, sticky=(N,S))

    listbox_l['yscrollcommand'] = scrollbar_s.set

    #save file variables
    label_sample.grid(column=0, row=2, columnspan=1, sticky=(N,W,E,S), padx=5)
    entry_sample.grid(column=0, row=3, columnspan=1, sticky=(N,W,E,S), padx=5)
    label_pulse_duration.grid(column=0, row=4, columnspan=1, sticky=(N,W,E,S), padx=5)
    entry_pulse_duration.grid(column=0, row=5, columnspan=1, sticky=(N,W,E,S), padx=5)
    label_pulse_amp.grid(column=0, row=6, columnspan=1, sticky=(N,W,E,S), padx=5)
    entry_pulse_amp.grid(column=0, row=7, columnspan=1, sticky=(N,W,E,S), padx=5)

    frame_information.grid_columnconfigure(0, weight=1)
    frame_information.grid_rowconfigure(0, weight=1)


    frame_buttomArea.grid(column =3, row=33,columnspan=2,sticky=(N, S, E, W))

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
