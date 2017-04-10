A simple implementation of tkinter GUI for magnetic, spintronic and electronic devices measurements.

Controlling Keithley 2400, Signal Recovery 7265 Lock-In amplifier thorugh National Instrument's NI GPIB-USB-HS GPIB control device.

Containing:

1. 1st and 2nd harmonic measurement (Ref [1]): GUI_HarmonicMeasurement_thread.py
2. Spin-orbit torque (SOT) switching (Ref [2]): GUI_HarmonicMeasurement_thread_SOT_switching.py
3. Spin-orbit torque (SOT) switching with pulse (Ref [3]): GUI_HarmonicMeasurement_thread_SOT_switching_pulse.py
4. Hysteresis loop shift measurement (Ref [4]): GUI_HarmonicMeasurement_thread_Iscan_Hx.py
5. Widefield MOKE (capture the screen of CCD software package): GUI_WideFieldMOKE.py

Environment:

Windows 10, python 3.4, 

python modules: Visa, matplotlib, numpy, pylab

References: <br />
[1] Kim et. al., Nature Materials  12, 240–245 (2013) https://doi.org/10.1038/nmat3522 <br />
[2] Liu et. al., Physical Review Letters 109, 096602 (2012) https://doi.org/10.1103/PhysRevLett.109.096602 <br />
[3] Garello et. al., Applied Physics Letters 105, 212402 (2014) http://dx.doi.org/10.1063/1.4902443 <br />
[4] Pai et. al., Physical Review B 93, 144409 (2016) https://doi.org/10.1103/PhysRevB.93.144409 <br />


![alt tag](http://140.112.32.1/~cfpai/wfMOKE.png)
