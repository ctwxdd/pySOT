import visa

class Keithley2400:
    
    def __init__(self,func):
        self.rm = visa.ResourceManager()
        #Depending on instrument GPIB address
        self.keithley2400 = self.rm.open_resource('GPIB::20')
        #For K2400, GPIB address is 20
        #Reset K2400
        self.keithley2400.write("*rst; status:preset; *cls") #Reset K2400
        #set mode
        
        #self.keithley2400.write("configure:%s" % func) 

        #self.keithley2400.write("status:measurement:enable 512; *sre 1")
        #self.keithley2400.write("trigger:source bus")
        #self.keithley2400.write("trace:feed sense1; feed:control next")
        #Prepare K2400 for trigger
        self.keithley2400.write(":SYST:RSEN OFF") #2-wire:OFF / 4-wire:ON


        print("initialized")
    def __str__(self):
        return "initialized"

    def outputOn(self):
        self.keithley2400.write(":OUTPUT ON")
        print("Keithley2400 output: ON")

    def outputOff(self):
        self.keithley2400.write(":OUTPUT OFF")
        print("Keithley2400 output: OFF")

    def setCurrent(self, current):

        #Note that above 20mA will kill the extended film device!
        self.keithley2400.write(":SOUR:FUNC CURR")
        self.keithley2400.write(":SOUR:CURR:MODE FIX")
        self.keithley2400.write(":SOUR:CURR:RANG 1e-1") #set range to 100mA
        
        I = current/1000 #convert to mA
        self.keithley2400.write(":SOUR:CURR:LEV %f" %I)
        print("Keithley2400 current set to: %f mA" %current)


    def measureOnce(self):
        self.keithley2400.write("initiate")
        #Sensing with voltage, protected by default compliance ~ 21V
        self.keithley2400.write(":SENS:FUNC 'VOLT'")
        self.keithley2400.write(":SENS:VOLT:PROT 10")
        #self.keithley2400.write(":SENS:VOLT:RANG 100") 
        self.keithley2400.write(":SENS:VOLT:RANG:AUTO ON") #default is 21V
        
        #self.keithley.assert_trigger()
        #self.keithley.wait_for_srq()
        #Request data from K2400
        result=[0.0]
        #raw= self.keithley.query_ascii_values("trace:data?")
        raw= self.keithley2400.query_ascii_values("READ?")
        #Reset Keithley
        #self.keithley2400.query("status:measurement?")
        #self.keithley2400.write("trace:clear; feed:control next")
        for i in raw:
            result.append(float(i))
        return result
 
    def measurement(self):
        
        #Setup measurement
    
        self.keithley2400.write("configure:%s" % self.func) 
        self.keithley2400.write("status:measurement:enable 512; *sre 1")
        self.keithley2400.write("sample:count %d" % self.number_of_readings)
        #self.keithley2400.write("sample:count 1")
        self.keithley2400.write("trigger:source bus")
        #self.keithley2400.write("trigger:delay %f" % (self.interval_in_ms / 1000.0))
        #self.keithley2400.write("trigger:delay 10")
        #self.keithley2400.write("trace:points %d" % self.number_of_readings)
        self.keithley2400y.write("trace:feed sense1; feed:control next")
        #Prepare K2400 for trigger
        self.keithley2400.write("initiate")
        self.keithley2400.assert_trigger()
        self.keithley2400.wait_for_srq()
        #Request data from K2400
        self.result = self.keithley2400.query_ascii_values("trace:data?")
        #self.result = self.keithley2400.query(":READ?")
        #average = 0;
        #for i in self.result:
           # self.average += int(i)
        #self.average /= len(self.result)
        #Reset Keithley
        self.keithley2400.query("status:measurement?")
        self.keithley2400.write("trace:clear; feed:control next")
             


    def save(self, s):
        result = ""
        for i in s:
            if i in self.code:
                j = self.alph.index(i)
                result += self.code[j]
            else:
                result += i
     
        return result
     
    def toDecode(self, s):
        result = ""
        for i in s:
            if i in self.code:
                j = self.code.index(i)
                result += self.alph[j]
            else:
                result += i
     
        return result


    def pulse(self,current, current_max,trigger_delay,source_delay):

      

        #self.keithley2400.write(":*RST")
        #self.keithley2400.write(":TRAC:CLE")
        #self.keithley2400.write(":TRAC:POIN 1")   #cler buffer and set for 10 reading
        #self.keithley2400.write(":STAT:MEAS:ENAB 512") #generate an SRQ upon buffer full (GPIB only!)
        #self.keithley2400.write(":*SRE 1")
        #self.keithley2400.write(":TRIG:COUN 1") #trigger count
        #self.keithley2400.write(":SYST:AZER:STAT OFF")  #auto zero off
        self.keithley2400.write(":SOUR:FUNC CURR")  #source current
        #self.keithley2400.write(":SENS:FUNC:CONC OFF") #concurrent reading off
        #self.keithley2400.write(":SENS:FUNC \"VOLT\"") #measure voltage
        #self.keithley2400.write(":SENS:VOLT:NPLC 0.08")
        #self.keithley2400.write(":SENS:VOLT:RANG 20")
        #self.keithley2400.write(":SENS:VOLT:PROT:LEV 21") #voltage compliance
        #self.keithley2400.write(":FORM:ELEM VOLT") #read back voltage only
        self.keithley2400.write(":SOUR:CURR %f"%(current*0.001)) #source current level in A
        self.keithley2400.write(":TRIG:DEL %d"%trigger_delay)

        self.keithley2400.write(":SOUR:DEL %g"%source_delay)
        self.keithley2400.write(":TRAC:FEED:CONT NEXT")
        self.keithley2400.write(":SOUR:CLE:AUTO ON")  #source auto clear
        #self.keithley2400.write(":DISP:ENAB OFF") #display set up
        self.keithley2400.write(":INIT")
                    #on recieving SR
        #print (self.keithley2400.query(":TRAC:DATA?"))
                    #Enter 10K bytes of data from 2400 & process data
                    #clean up registers
        #self.keithley2400.write("*RST;")
        #self.keithley2400.write("*CLS;")
        #self.keithley2400.write("*SRE 0;")
        #self.keithley2400.write(":STAT:MEAS:ENAB 0")
 
if __name__ == '__main__':
    
    print()
    new = Keithley2400()
    new.pulse( current_max= 10, trigger_delay=0.1, source_delay=0.1)
 
