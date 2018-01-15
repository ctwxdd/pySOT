
#********************** 2017/01/30 Version ********************#
# Note: Threading added in the measureMethod()
# Note: The listbox will now always show the latest measured data
# Note: Threading can avoid non-responsive problem, but will also cause
#       the intereference by clicking other buttons during measurement.
# Note: Keithley2400 current option added.
# Note: All output will be shut down by clicking quit
# Note: Create the K2400 current stepping function

#********************** 2017/03/27 Version ********************#
# Note: Modification on data plots (dots and lines)
# Note: Keithley2000 for photovoltage read-out, using measureMulti(average)
# Note: Saving files with date and time

#********************** 2017/04/11 Version ********************#
# Note: Saving image file at the same time

#********************** 2018/01/12 Version ********************#
# Note: Voltage Protection added 2017/12/19
# Note: Cleaned up code for easier reading
# Note: Unnecessary variables removed
# Note: Save function updated to include sample name and initial resistance 
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
from keithley2400_I import Keithley2400
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
    DAC=1 #Set a default DAC output channel for Hz
    DACx=3 #Set a default DAC output channel for Hx
    signal=1 #Set a default OSC signal voltage (V)
    freq=1171 #Set a default OSC frequency (Hz)

    read_me = 'This program uses Keithley2400 to provide a current to the device. Keithley2000 provides 2 wire voltage measurements \
    and the Lock-In Amp provides Hx and Hz fields of varying strength.'

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

# Uses Keithley2000 for voltage measurements, Keithley2400 for applying current, Lock-In Amp for Hx and Hz
def measureMethod(_interval, _number, _output, _average, _signal, _frequency, _current, _step, _Hx, _dHx, _intervalx, _sample):
    

    i=float(_interval) # Hz calibration factor
    ix=float(_intervalx) # Hx calibration factor
    n=int(_number) # number of points measured per Hz field sweep
    average=int(_average) # number of averaged measurements for Keithley2000
    signal=float(_signal) # Lock-in Amp OSC signal voltage (MAX 5 V)
    freq=int(_frequency) # Lock-in Amp OSC frequency (Hz)

    def event():

        Hx_start=float(_Hx) # Max Hx field strength
        Hx_end=float(_Hx)*(-1)
        Hx_step=float(_dHx)

        keith1=Keithley('voltage') #Initiate K2000 to voltage measurement
        keith=Keithley2400(f) #Initiate K2400
        amp = lockinAmp(func, sense, signal, freq) #Initiate Lock-in

        while Hx_start>=Hx_end:

            amp.dacOutput((Hx_start/ix), DACx)

            current_start=float(_current) 
            current_end=float(_current)*(-1)
            current_step=float(_step)
    
            while current_start>=current_end:

                ax.clear()
                ax.grid(True)
                ax.set_title("Realtime photo-voltage vs H Plot")
                ax.set_xlabel("Applied Field (Oe)")
                ax.set_ylabel("Photo-voltage (V)")

                listbox_l.insert('end',"Now measuring with Hx = %f (Oe) and Idc = %f (mA) " %(Hx_start,current_start))
                listbox_l.see(END)
                
                #Prepare data entries
                global values_x, values_y, result

                values_y=[]
                values_x=[]
                result=[]
                
                #Setup K2400 for current output and resistance measurement
                keith.setCurrent(current_start)
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

                #Setup lock-in for dac (Hz field) output
                t=0
                a=0.0
                step = (double(_output)/i)/n
        
                while t < n :

                    amp.dacOutput(a, DAC)
                    tmp=keith1.measureMulti(average) #Keithley2000 2-wire voltage
                    result.append(tmp)
                    values_y.append(tmp)
                    values_x.append(a*i)
                    #ax.scatter(values_x[-1], values_y[-1], s=dot_size, c='red', alpha=0.5)
                    ax.plot(values_x, values_y,'r-o', ms=dot_size, mew=dot_edge, alpha=0.5)
                    canvas.draw()
                    listbox_l.insert('end', tmp)
                    t+=1
                    a+=step
                    listbox_l.see(END)

                while t < 3*n :

                    amp.dacOutput(a, DAC)
                    tmp=keith1.measureMulti(average) #Keithley2000 2-wire voltage
                    result.append(tmp)
                    values_y.append(tmp)
                    values_x.append(a*i)
                    #ax.scatter(values_x[-1], values_y[-1], s=dot_size, c='red', alpha=0.5)
                    ax.plot(values_x, values_y,'r-o', ms=dot_size, mew=dot_edge, alpha=0.5)
                    canvas.draw()
                    listbox_l.insert('end', tmp)
                    t+=1
                    a-=step
                    listbox_l.see(END)

                while t <= 4*n :

                    amp.dacOutput(a, DAC)
                    tmp=keith1.measureMulti(average) #Keithley2000 2-wire voltage
                    result.append(tmp)
                    values_y.append(tmp)
                    values_x.append(a*i)
                    #ax.scatter(values_x[-1], values_y[-1], s=dot_size, c='red', alpha=0.5)
                    ax.plot(values_x, values_y,'r-o', ms=dot_size, mew=dot_edge, alpha=0.5)
                    canvas.draw()
                    listbox_l.insert('end', tmp)
                    t+=1
                    a+=step
                    listbox_l.see(END)


                #Setup timestamp
                stamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
                listbox_l.insert('end', str(stamp))

                file = open(str(directory)+"/LaserMOKE_"+str(_sample)+"_"+str(Hx_start)+"Oe_"+str(current_start)+"mA_"+str(stamp), "w")
                file.write(str(_sample)+"\n")
                file.write("Initial resistance: " + str(save) + "(Ohm)\n")
                file.write("Applied in-plane field: "+str(Hx_start)+"(Oe)\n")
                file.write("Applied current: "+str(current_start)+"(mA)\n\n")
                file.write("Number"+" "+"Field(Oe)"+" "+"Voltage(V)"+"\n")

                cnt=1
                #output all data 
                for a in range(len(values_y)):

                    file.write(str(cnt)+" "+str(values_x[a])+" "+str(values_y[a])+"\n")
                    cnt +=1

                file.closed

                #Save image file
                fig.savefig(str(directory)+"/LaserMOKE_"+str(_sample)+"_"+str(Hx_start)+"Oe_"+str(current_start)+"mA_"+str(stamp)+".JPG")

                listbox_l.insert('end', "The Measurement data is saved.")
                listbox_l.see(END)

                keith.outputOff()
                current_start=current_start-current_step

                time.sleep(1) #Sleep between each scan


            Hx_start=Hx_start-Hx_step

        amp.dacOutput(0, DACx)
        amp.dacOutput(0, DAC)
        listbox_l.insert('end',"Measurement finished")
        listbox_l.see(END)

    if (double(_output)/i)< 1 and (float(_Hx)/ix)<12:
        
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
    ax.set_title("Realtime photo-voltage vs H Plot")
    ax.set_xlabel("Applied Field (Oe)")
    ax.set_ylabel("Photo-voltage (V)")
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

    keith=Keithley2400(f)
    keith.setCurrent(0)
    keith.outputOff()

    listbox_l.insert('end', "All fields set to zero.")
    listbox_l.see(END)
    time.sleep(1)
    
    global root

    root.quit()

def createWidgit():

    global ax, canvas, listbox_l, result, func, frame, sense, fig

    fig = pylab.figure(1)

    ax = fig.add_subplot(111)
    ax.grid(True)
    ax.set_title("Realtime photo-voltage vs H Plot")
    ax.set_xlabel("Applied Field (Oe)")
    ax.set_ylabel("Photo-voltage (V)")
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
    entry_number = ttk.Entry(frame_setting); entry_number.insert(0,"25")
    entry_interval = ttk.Entry(frame_setting);entry_interval.insert(0,"1022")
    entry_output = ttk.Entry(frame_setting); entry_output.insert(0,"50")
    entry_average = ttk.Entry(frame_setting); entry_average.insert(0,"3")
    entry_signal = ttk.Entry(frame_setting); entry_signal.insert(0,"1")
    entry_frequency = ttk.Entry(frame_setting); entry_frequency.insert(0,"1171")
    entry_current = ttk.Entry(frame_setting); entry_current.insert(0,"0")
    entry_step = ttk.Entry(frame_setting); entry_step.insert(0,"0.5")
    entry_Hx = ttk.Entry(frame_setting); entry_Hx.insert(0,"0")
    entry_dHx = ttk.Entry(frame_setting); entry_dHx.insert(0,"100")
    entry_intervalx = ttk.Entry(frame_setting);entry_intervalx.insert(0,"396.59")

    value = tkinter.StringVar() #mode
    value2 = tkinter.StringVar() #sensitivity
    value3 = tkinter.IntVar() #dac
    value4 = tkinter.StringVar() #keithOut

    mode = ["1st","1st","2nd"]
    sensitivity = ["10mV","1mV","2mV","5mV","10mV","20mV","50mV","100mV","200mV","10uV","20uV","50uV","100uV"]
    dac = [1,1,2,3,4]
    dacx = [3,1,2,3,4]

    option_mode = ttk.OptionMenu(frame_setting, value, *mode, command = optionMethod)
    option_sensitivity = ttk.OptionMenu(frame_setting, value2, *sensitivity, command = senseMethod)
    option_dac = ttk.OptionMenu(frame_setting, value3, *dac, command = dacMethod)
    option_dacx = ttk.OptionMenu(frame_setting, value4, *dacx, command = dacxMethod)

    listbox_l = Listbox(frame_information,height=5)
    scrollbar_s = ttk.Scrollbar(frame_information, orient=VERTICAL, command=listbox_l.yview)

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
    label_current = ttk.Label(frame_setting, text="Current (mA):")
    label_step = ttk.Label(frame_setting, text="Current step (mA):")
    label_Hx = ttk.Label(frame_setting, text="Hx field (Oe):")
    label_dHx = ttk.Label(frame_setting, text="Hx step (Oe):")
    label_intervalx = ttk.Label(frame_setting, text="Hx(Oe)/DAC(V):")
    label_empty = ttk.Label(frame_setting, text="")
    
    
    button_measure = ttk.Button(frame_buttomArea, text ="Measure", \
        command = lambda : measureMethod(entry_interval.get(),entry_number.get(),entry_output.get(),\
            entry_average.get(),entry_signal.get(),entry_frequency.get(),entry_current.get(),\
            entry_step.get(),entry_Hx.get(),entry_dHx.get(),entry_intervalx.get(),entry_sample.get()))

    button_dir  = ttk.Button(frame_buttomArea, text="Change directory", command = dirMethod)
    button_quit = ttk.Button(frame_buttomArea, text="Quit", command = quitMethod)
    button_output = ttk.Button(frame_buttomArea, text="Output", \
        command = lambda : outputMethod(entry_interval.get(),entry_output.get(),entry_signal.get(),entry_frequency.get()))
    button_clear = ttk.Button(frame_buttomArea, text="Clear", command = clearMethod)

    #Attatch Plot 
    canvas = FigureCanvasTkAgg(fig, frame)
    canvas.get_tk_widget().grid(row=0, column =0, pady =0, padx =0,sticky='nsew')
    content.grid(column=0, row=0, sticky=(N, S, E, W))
    frame.grid(column=0, row=0, columnspan=3, rowspan=30, sticky=(N, S, E, W))


    frame_setting.grid(column=3, row=0, columnspan=2, rowspan=30, sticky=(N, S, E, W))

    #Save setings
    label_sample = ttk.Label(frame_information, text = "Sample Name")

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
    label_current.grid(column=0, row=21, columnspan=2, sticky=(N, W), padx=5)
    entry_current.grid(column=0, row=22, columnspan=2, sticky=(N, W), padx=5)
    label_step.grid(column=0, row=23, columnspan=2, sticky=(N, W), padx=5)
    entry_step.grid(column=0, row=24, columnspan=2, sticky=(N, W), padx=5)
    label_Hx.grid(column=0, row=25, columnspan=2, sticky=(N, W), padx=5)
    entry_Hx.grid(column=0, row=26, columnspan=2, sticky=(N, W), padx=5)
    label_dHx.grid(column=0, row=27, columnspan=2, sticky=(N, W), padx=5)
    entry_dHx.grid(column=0, row=28, columnspan=2, sticky=(N, W), padx=5)
    label_intervalx.grid(column=0, row=29, columnspan=2, sticky=(N, W), padx=5)
    entry_intervalx.grid(column=0, row=30, columnspan=2, sticky=(N, W), padx=5)

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





