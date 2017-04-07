
# 01/25/2017 Selection of sensitivity (mVs and uVs) now added.
# 01/25/2017 Number of averages added.
# 01/26/2017 Lock-in OSC signal options (amplitude, frequency) added.
# 01/26/2017 Lock-in DAC channel (DAC1 to DAC4) option added.
# 03/31/2017 Lock-in '0.0E+00\x00\r\n' error avoided.

import visa
import time

class lockinAmp():
    
    v_max = +12
    v_min = -12
    

    def __init__(self, func, sense, signal, freq):

        self.rm = visa.ResourceManager()
        #Depending on instrument GPIB address
        self.sr = self.rm.open_resource('GPIB::10') #SR7265 GPIB address 10
        #Execute something with SR7265
        #print(self.sr.query("ID"))

        #Set output AC voltage amplitude
        self.amplitude = signal     #output voltage amplitude (V)
        self.frequency = freq  #output frequency (Hz)

        #Initialize display
        self.sr.write("DISPOUT0 9")
        self.sr.write("DISPOUT1 3")
        self.sr.write("DISPOUT2 4")
        self.sr.write("DISPOUT3 10")

        #Set signal channel to
        #self.sr.write("VMODE 1") #A
        self.sr.write("VMODE 3") #A-B

        #Setting up AC Gain and Time Constant
        #self.sr.write("AUTOMATIC 1")
        self.sr.write("ACGAIN 2")
        self.sr.write("TC10")

        #Reset DAC1 to DAC4 output to zero
        self.sr.write("DAC1 0")
        self.sr.write("DAC2 0")
        self.sr.write("DAC3 0")
        self.sr.write("DAC4 0")
        

        self.amp_set = self.amplitude*1000000 #conversion based on original setting
        self.freq_set = self.frequency*1000 #conversion based on original setting

        self.sr.write("OA %d" %self.amp_set)
        self.sr.write("OF %d" %self.freq_set)

        #Choosing sensitivity range

        
        if sense == '5uV':
            self.sr.write("SEN11") #5uV
        elif sense == '10uV':
            self.sr.write("SEN12") #10uV
        elif sense == '20uV':
            self.sr.write("SEN13") #20uV
        elif sense == '50uV':
            self.sr.write("SEN14") #50uV
        elif sense == '100uV':
            self.sr.write("SEN15") #100uV
        elif sense == '200uV':
            self.sr.write("SEN16") #200uV
        elif sense == '500uV':
            self.sr.write("SEN17") #500uV
        elif sense == '1mV':
             self.sr.write("SEN18") #1mV
        elif sense == '2mV':
            self.sr.write("SEN19") #2mV
        elif sense == '5mV':
            self.sr.write("SEN20") #5mV
        elif sense == '10mV':
            self.sr.write("SEN21") #10mV
        elif sense == '20mV':
            self.sr.write("SEN22") #20mV
        elif sense == '50mV':
            self.sr.write("SEN23") #50mV
        elif sense == '100mV':
            self.sr.write("SEN24") #100mV
        elif sense == '200mV':
            self.sr.write("SEN25") #200mV
        else:
            self.sr.write("SEN26") #500mV

        #Choosing first or second harmonic
        if func == '1st':
                
            self.sr.write("REFN1") #1st harmonic
            self.sr.write("REFP0") #phase 0deg

        else:
            
            self.sr.write("REFN2") #2nd harmonic
            self.sr.write("REFP90000") #phase 9deg


    def __str__(self):
        return "initialized"


    def ouputSignal(self, amp, freq):
    #Output signal
        self.amplitude = amp #Oscillator output Vrms from 0 to 5V
        self.frequency = freq #Oscillator output frequency from 0 to 250kHz
        self.amp_set = self.amplitude*1000000 #conversion based on original setting
        self.freq_set = self.frequency*1000 #conversion based on original setting
        self.sr.write("OA %d" %self.amp_set)
        self.sr.write("OF %d" %self.freq_set)
    #Sensing setting
    def sensitivity(self, mode):
        #Sensing range
        self.sr.write("SEN%d" %mode)
        print("SEN%d" %mode)

    def timeConst(self, mode):
    #Time constant
        self.sr.write("TC%d" %mode)
        print("TC%d" %mode)
    def acGain(self, mode):
    #AC Gain
    #   self.sr.write("ACGAIN1")
        print("ACGAIN1")


    def dacOutput(self, vol, dac):
        dac_amp_set = vol*1000
        t0=time.time()*1000
        self.sr.write("DAC%d %d" %(dac,dac_amp_set))
        print("DAC%d: %fV" %(dac,vol))


    #DAC output (Digital to Analog Converter)
    def dacRampTo(self, vol):

        #print(type(vol))
        if (vol <=12 and vol >= -12) :

            H_e=vol*float(56.953)
            H_c=vol*float(23.833)
            dac_amplitude = vol #DAC output DC voltage from -12V to 12V
            dac_step = 0.1 * vol/abs(vol) #DAC output step in volts
            dac_step_set = dac_step*1000
            dac_amp_set = dac_amplitude*1000 #conversion based on original setting
            dac_i = 0 #sweep from zero

            t0=time.time()*1000

            while abs(dac_i) <= abs(dac_amp_set):

                self.sr.write("DAC1 %d" %dac_i)
                dac_i+=dac_step_set

            print ("%.2f" %float(time.time()*1000-t0))
            #print("The magnetic fild at Edge is %.2lf (Oe)." %H_e)
            #print("The magnetic fild at cenber is %.2lf (Oe)" %H_c)
            msg = "DAC output has been set to "+str(vol)+"(V)."
            return msg
        else:
            return "Out of limit."


    #Signal Readout
    def readX(self, average):

        i=1
        data=0
        N=average #Number of averages

        while i<=N:

            tmp=self.sr.query("X.")

            if tmp=='0.0E+00\x00\r\n':
                tmp=0
            else:
                tmp=float(tmp)

            data=data+tmp
            i+=1
            
        return float(data/average)
