# Freeze application
# pyinstaller --add-data=G:\CureQ\py_to_exe\sv_ttk\*:sv_ttk --add-data=G:\CureQ\py_to_exe\sv_ttk\theme\*:sv_ttk\theme --icon=cureq_icon.ico --add-data=cureq_icon.ico:. --onefile CureQ_MEA-analysis_tool.py

if __name__=="__main__":
    import multiprocessing
    multiprocessing.freeze_support()
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import sv_ttk
import threading
import time
from functools import partial
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
import json
import copy
import pandas as pd
import seaborn as sns
from scipy import stats
import numpy as np
import math
import webbrowser
import sys
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import warnings 

# Setting the warnings to be ignored 
warnings.filterwarnings('ignore') 

# Import the MEA library
from CureQ import *
from bandpass import *
from burst_detection import *
from features import *
from network_burst_detection import *
from mea import *
from open_file import *
from plotting import *
from spike_validation import *
from threshold import *


# Initialize tkinter GUI
root = Tk()

"""Visual settings"""
# Set the theme
theme='dark'
sv_ttk.set_theme(theme)

# Define font and styles
font="Arial"
def define_styles():
    # Define different styles
    labelframestyle = ttk.Style()
    labelframestyle.configure("Custom.TLabelframe.Label", font=(font, 20))

    subframestyle = ttk.Style()
    subframestyle.configure("Sublabel.TLabelframe.Label", font=(font, 12))

    bigbuttonstyle=ttk.Style()
    bigbuttonstyle.configure("bigbutton.TButton", font=(font, 30), anchor="center", justify="center", wraplength=400)

    mediumbuttonstyle=ttk.Style()
    mediumbuttonstyle.configure("mediumbutton.TButton", font=(font, 15))

    wellbuttonstyle=ttk.Style()
    wellbuttonstyle.configure("wellbutton.TButton", font=(font, 15))

define_styles()

# Add function for changing theme    
def toggle_theme():
    sv_ttk.toggle_theme()
    global theme
    theme=sv_ttk.get_theme()
    # For some reason you have to redefine the styles everytime you switch themes
    define_styles()

# Set correct icons
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
application_path=resource_path("cureq_icon.ico")

try:
    root.iconbitmap(os.path.join(application_path))
except Exception as error:
    print("Could not load in icon")
    print(error)


root.title("CureQ_MEA-analysis_tool")

# Define global variables and default values
global filename
global validation_method
filename=""
validation_method='DMP_noisebased'

def go_to_parameterframe():
    parameterframe.pack(fill='both', expand=True)
    main_frame.pack_forget()

def openfiles():
    global filename
    selectedfile = filedialog.askopenfilename(filetypes=[("MEA data", "*.h5")])
    if len(selectedfile)!=0:
        filename=selectedfile
        selectedfile=os.path.split(filename)[1]
        btn_selectfile.configure(text=selectedfile)
        # selectedfilelabel.config(text=selectedfile)

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        
    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip if not exists
        if not self.tooltip:
            self.tooltip = tk.Toplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = ttk.Label(self.tooltip, text=self.text, borderwidth=3, relief='sunken')
            label.pack()
            
    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


main_frame=ttk.Frame(root)
main_frame.pack(fill='both', expand=True)

# Scrollable frame
class VerticalScrolledFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

# Frame for the sidebar buttons
sidebarframe=ttk.Frame(master=main_frame)
sidebarframe.grid(row=0, column=2, rowspan=10, sticky='nesw')

# Switch between light and dark mode
theme_switch = ttk.Checkbutton(sidebarframe, text="Light theme", style="Switch.TCheckbutton", command=toggle_theme)
theme_switch.grid(row=0, column=0, sticky='nesw', pady=10, padx=10)

def link_to_cureq():
    webbrowser.open_new("https://cureq.nl/")
cureq_button=ttk.Button(master=sidebarframe, text="CureQ", command=link_to_cureq)
cureq_button.grid(row=1, column=0, sticky='nesw', pady=10, padx=10)

def link_to_pypi():
    webbrowser.open_new("https://pypi.org/project/CureQ/")
pypi_button=ttk.Button(master=sidebarframe, text="Library", command=link_to_pypi)
pypi_button.grid(row=2, column=0, sticky='nesw', pady=10, padx=10)

def link_to_github():
    webbrowser.open_new("https://github.com/CureQ")
github_button=ttk.Button(master=sidebarframe, text="Github", command=link_to_github)
github_button.grid(row=3, column=0, sticky='nesw', pady=10, padx=10)

# Set up the frame where te user selects different parameters
parameterframe=VerticalScrolledFrame(root)
parameterframe.pack(fill='both', expand=True)
parameterframe.pack_forget()

btn_parameter=ttk.Button(master=main_frame, text="Set\nParameters", compound=LEFT, style="bigbutton.TButton", command=go_to_parameterframe)
btn_parameter.grid(row=0, column=0, padx=10, pady=10, sticky='nsew', ipadx=25, ipady=25)

# Set up the required parameters
requiredparameters=ttk.LabelFrame(parameterframe.interior, text='Required Parameters', style="Custom.TLabelframe")
requiredparameters.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

# filelabel=ttk.Label(master=requiredparameters, text="File:", font=(font,10))
# filelabel.grid(row=0, column=0, padx=10, pady=10, sticky='w')
btn_selectfile=ttk.Button(master=requiredparameters, text="Choose a file", command=openfiles)
btn_selectfile.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='nesw')
# selectedfilelabel=ttk.Label(master=requiredparameters, text=filename, borderwidth=3, relief="sunken")
# selectedfilelabel.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='w')

# Setup the sampling frequency
hertzlabel=ttk.Label(master=requiredparameters, text="Sampling rate:", font=(font,10))
hertzlabel.grid(row=2, column=0, padx=10, pady=10, sticky='w')
hertzinput=ttk.Entry(master=requiredparameters)
hertzinput.grid(row=2, column=1, padx=10, pady=10, sticky='w')

# Setup up the amount of electrodes
electrodeamntlabel=ttk.Label(master=requiredparameters, text="Electrode amount:", font=(font,10))
electrodeamntlabel.grid(row=3, column=0, padx=10, pady=10, sticky='w')
electrodeamnttooltip = Tooltip(electrodeamntlabel, 'How many electrodes does each well contain?')
electrodeamntlabel.bind("<Enter>", electrodeamnttooltip.show_tooltip)
electrodeamntlabel.bind("<Leave>", electrodeamnttooltip.hide_tooltip)
electrodeamntinput=ttk.Entry(master=requiredparameters)
electrodeamntinput.grid(row=3, column=1, padx=10, pady=10, sticky='w')

# Set up all the filter parameters
filterparameters=ttk.LabelFrame(parameterframe.interior, text='Filter', style="Custom.TLabelframe")
filterparameters.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

# Low cutoff
lowcutofflabel=ttk.Label(master=filterparameters, text="Low cutoff:", font=(font,10))
lowcutofflabel.grid(row=1, column=0, padx=10, pady=10, sticky='w')
lowcutofftooltip = Tooltip(lowcutofflabel, 'Define the low cutoff value for the butterworth bandpass filter. Values should be given in hertz')
lowcutofflabel.bind("<Enter>", lowcutofftooltip.show_tooltip)
lowcutofflabel.bind("<Leave>", lowcutofftooltip.hide_tooltip)
lowcutoffinput=ttk.Entry(master=filterparameters)
lowcutoffinput.grid(row=1, column=1, padx=10, pady=10, sticky='w')

# High cutoff
highcutofflabel=ttk.Label(master=filterparameters, text="High cutoff:", font=(font,10))
highcutofflabel.grid(row=2, column=0, padx=10, pady=10, sticky='w')
highcutofftooltip = Tooltip(highcutofflabel, 'Define the high cutoff value for the butterworth bandpass filter. Values should be given in hertz')
highcutofflabel.bind("<Enter>", highcutofftooltip.show_tooltip)
highcutofflabel.bind("<Leave>", highcutofftooltip.hide_tooltip)
highcutoffinput=ttk.Entry(master=filterparameters)
highcutoffinput.grid(row=2, column=1, padx=10, pady=10, sticky='w')

# Filter order
orderlabel=ttk.Label(master=filterparameters, text="Filter order:", font=(font,10))
orderlabel.grid(row=3, column=0, padx=10, pady=10, sticky='w')
ordertooltip = Tooltip(orderlabel, 'The filter order for the butterworth filter')
orderlabel.bind("<Enter>", ordertooltip.show_tooltip)
orderlabel.bind("<Leave>", ordertooltip.hide_tooltip)
orderinput=ttk.Entry(master=filterparameters)
orderinput.grid(row=3, column=1, padx=10, pady=10, sticky='w')

# Set up all the spike detection parameters
spikedetectionparameters=ttk.LabelFrame(parameterframe.interior, text='Spike Detection', style="Custom.TLabelframe")
spikedetectionparameters.grid(row=0, column=2, padx=10, pady=10, sticky='nsew', rowspan=2)

# Threshold parameters
thresholdparameters=ttk.LabelFrame(spikedetectionparameters, text='Threshold parameters', style="Sublabel.TLabelframe")
thresholdparameters.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

# Threshold portion
thresholdportionlabel=ttk.Label(master=thresholdparameters, text="Threshold portion:", font=(font,10))
thresholdportionlabel.grid(row=1, column=0, padx=10, pady=10, sticky='w')
thresholdportiontooltip = Tooltip(thresholdportionlabel, 'Define the portion of the electrode data that is used for determining the threshold.\nA higher values will give a better estimate of the background noise,\nbut will take longer to compute\nRanges from 0 to 1.')
thresholdportionlabel.bind("<Enter>", thresholdportiontooltip.show_tooltip)
thresholdportionlabel.bind("<Leave>", thresholdportiontooltip.hide_tooltip)
thresholdportioninput=ttk.Entry(master=thresholdparameters)
thresholdportioninput.grid(row=1, column=1, padx=10, pady=10, sticky='w')

# stdevmultiplier
stdevmultiplierlabel=ttk.Label(master=thresholdparameters, text="Standard Deviation Multiplier:", font=(font,10))
stdevmultiplierlabel.grid(row=2, column=0, padx=10, pady=10, sticky='w')
stdevmultipliertooltip = Tooltip(stdevmultiplierlabel, 'Define when beyond which point values are seen as\noutliers (spikes) when identifying spike-free noise\nA higher value will identify more data as noise')
stdevmultiplierlabel.bind("<Enter>", stdevmultipliertooltip.show_tooltip)
stdevmultiplierlabel.bind("<Leave>", stdevmultipliertooltip.hide_tooltip)
stdevmultiplierinput=ttk.Entry(master=thresholdparameters)
stdevmultiplierinput.grid(row=2, column=1, padx=10, pady=10, sticky='w')

# RMSmultiplier
RMSmultiplierlabel=ttk.Label(master=thresholdparameters, text="RMS Multiplier:", font=(font,10))
RMSmultiplierlabel.grid(row=3, column=0, padx=10, pady=10, sticky='w')
RMSmultipliertooltip = Tooltip(RMSmultiplierlabel, 'Define the multiplication factor of the root mean square (RMS) of the background noise\nA higher number will lead to a higher threshold')
RMSmultiplierlabel.bind("<Enter>", RMSmultipliertooltip.show_tooltip)
RMSmultiplierlabel.bind("<Leave>", RMSmultipliertooltip.hide_tooltip)
RMSmultiplierinput=ttk.Entry(master=thresholdparameters)
RMSmultiplierinput.grid(row=3, column=1, padx=10, pady=10, sticky='w')

# Spike validation parameters
validationparameters=ttk.LabelFrame(spikedetectionparameters, text='Spike Validation Parameters', style="Sublabel.TLabelframe")
validationparameters.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

# Refractory period
refractoryperiodlabel=ttk.Label(master=validationparameters, text="Refractory Period:", font=(font,10))
refractoryperiodlabel.grid(row=0, column=0, padx=10, pady=10, sticky='w')
refractoryperiodtooltip = Tooltip(refractoryperiodlabel, 'Define the refractory period in the spike detection\nIn this period after a spike, no other spike can be detected\nValue should be given in seconds, so 2 ms = 0.002 s')
refractoryperiodlabel.bind("<Enter>", refractoryperiodtooltip.show_tooltip)
refractoryperiodlabel.bind("<Leave>", refractoryperiodtooltip.hide_tooltip)
refractoryperiodinput=ttk.Entry(master=validationparameters)
refractoryperiodinput.grid(row=0, column=1, padx=10, pady=10, sticky='w')

# Dropdown menu where the user selects the validation method
def option_selected(event):
    global validation_method
    validation_method = dropdown_var.get()
    if validation_method=='DMP_noisebased':
        exittimeinput.configure(state="enabled")
        heightexceptioninput.configure(state="enabled")
        maxheightinput.configure(state="enabled")
        amplitudedropinput.configure(state="enabled")
    else:
        exittimeinput.configure(state="disabled")
        heightexceptioninput.configure(state="disabled")
        maxheightinput.configure(state="disabled")
        amplitudedropinput.configure(state="disabled")
    
    
dropdown_var = tk.StringVar(validationparameters)
options = ['DMP_noisebased', 'none']
dropdownlabel = ttk.Label(master=validationparameters, text="Spike validation method:", font=(font,10))
dropdownlabel.grid(row=1, column=0, padx=10, pady=10, sticky='w')
dropdown_menu = ttk.OptionMenu(validationparameters, dropdown_var, options[0], *options, command=option_selected)
dropdown_menu.grid(row=1, column=1, padx=10, pady=10, sticky='nesw')

exittimelabel=ttk.Label(master=validationparameters, text="Exit time:", font=(font,10))
exittimelabel.grid(row=2, column=0, padx=10, pady=10, sticky='w')
exittimetooltip = Tooltip(exittimelabel, 'Define the time a spike gets to drop a certain value.\nStarts from the peak of the spike.\nValue should be given in seconds, so 0.24 ms is 0.00024s')
exittimelabel.bind("<Enter>", exittimetooltip.show_tooltip)
exittimelabel.bind("<Leave>", exittimetooltip.hide_tooltip)
exittimeinput=ttk.Entry(master=validationparameters)
exittimeinput.grid(row=2, column=1, padx=10, pady=10, sticky='w')

amplitudedroplabel=ttk.Label(master=validationparameters, text="Drop amplitude:", font=(font,10))
amplitudedroplabel.grid(row=3, column=0, padx=10, pady=10, sticky='w')
amplitudedroptooltip = Tooltip(amplitudedroplabel, 'Multiplied with the standard deviation of the surrounding noise.\nThis is the height the spike will have to drop in\na certain amount of time to be registered')
amplitudedroplabel.bind("<Enter>", amplitudedroptooltip.show_tooltip)
amplitudedroplabel.bind("<Leave>", amplitudedroptooltip.hide_tooltip)
amplitudedropinput=ttk.Entry(master=validationparameters)
amplitudedropinput.grid(row=3, column=1, padx=10, pady=10, sticky='w')

heightexceptionlabel=ttk.Label(master=validationparameters, text="Height exception:", font=(font,10))
heightexceptionlabel.grid(row=4, column=0, padx=10, pady=10, sticky='w')
heightexceptiontooltip = Tooltip(heightexceptionlabel, 'If a spike reaches an amplitude that is a more than the height exception * the threshold,\nthe spike will always be registered')
heightexceptionlabel.bind("<Enter>", heightexceptiontooltip.show_tooltip)
heightexceptionlabel.bind("<Leave>", heightexceptiontooltip.hide_tooltip)
heightexceptioninput=ttk.Entry(master=validationparameters)
heightexceptioninput.grid(row=4, column=1, padx=10, pady=10, sticky='w')

maxheightlabel=ttk.Label(master=validationparameters, text="Max drop amount:", font=(font,10))
maxheightlabel.grid(row=5, column=0, padx=10, pady=10, sticky='w')
maxheighttooltip = Tooltip(maxheightlabel, 'Multiplied with the threshold.\nThe maximum height a spike can be required to drop in amplitude in the set timeframe')
maxheightlabel.bind("<Enter>", maxheighttooltip.show_tooltip)
maxheightlabel.bind("<Leave>", maxheighttooltip.hide_tooltip)
maxheightinput=ttk.Entry(master=validationparameters)
maxheightinput.grid(row=5, column=1, padx=10, pady=10, sticky='w')

def parameter_to_main_func():
    # Check if the user has selected a file
    if filename == "":
        tk.messagebox.showerror(title='Error', message='No file has been selected yet, please select a file')

    # save parameters in global values
    global wells
    wells='all'
    global hertz
    global low_cutoff
    global high_cutoff
    global order
    global spikeduration
    global exit_time_s
    global plot_electrodes
    plot_electrodes = False
    global electrode_amnt
    global kde_bandwidth
    global smallerneighbours
    global minspikes_burst
    global max_threshold
    global default_threshold
    global heightexception
    global max_drop_amount
    global amplitude_drop_sd
    global stdevmultiplier
    global RMSmultiplier
    global min_channels
    global threshold_method
    global activity_threshold
    global threshold_portion
    global remove_inactive_electrodes
    global cut_data_bool
    global parts
    # Save parameters
    try:
        hertz=int(hertzinput.get())
        low_cutoff=int(lowcutoffinput.get())
        high_cutoff=int(highcutoffinput.get())
        order=int(orderinput.get())
        spikeduration=float(refractoryperiodinput.get())
        exit_time_s=float(exittimeinput.get())
        electrode_amnt=int(electrodeamntinput.get())
        kde_bandwidth=float(isikdebwinput.get())
        smallerneighbours=int(smallernbinput.get())
        minspikes_burst=int(minspikesinput.get())
        max_threshold=float(maxisiinput.get())
        default_threshold=float(defaultthinput.get())
        heightexception=float(heightexceptioninput.get())
        max_drop_amount=float(maxheightinput.get())
        amplitude_drop_sd=float(amplitudedropinput.get())
        stdevmultiplier=float(stdevmultiplierinput.get())
        RMSmultiplier=float(RMSmultiplierinput.get())
        min_channels=float(minchannelsinput.get())
        threshold_method=networkth_var.get()
        remove_inactive_electrodes=bool(removeinactivevar.get())
        activity_threshold=float(activitythinput.get())
        threshold_portion=float(thresholdportioninput.get())
        cut_data_bool=bool(splitdatavar.get())
        parts=int(splitdatapartsinput.get())
        main_frame.pack(fill='both', expand=True)
        parameterframe.pack_forget()
    except Exception as error:
        print(error)
        tk.messagebox.showerror(title='Error', message='Certain parameters could not be converted to the correct datatype (e.g. int or float). Please check if every parameter has the correct values')

parameter_to_main=ttk.Button(master=parameterframe.interior, text="Save parameters and return", command=parameter_to_main_func)
parameter_to_main.grid(row=3, column=0, padx=10, pady=(10,20), sticky='nsew')


# Set up all the burst detection parameters
burstdetectionparameters=ttk.LabelFrame(parameterframe.interior, text='Burst Detection', style="Custom.TLabelframe")
burstdetectionparameters.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

# Setup up the minimal amount of spikes for a burst
minspikeslabel=ttk.Label(master=burstdetectionparameters, text="Minimal amount of spikes:", font=(font,10))
minspikeslabel.grid(row=0, column=0, padx=10, pady=10, sticky='w')
minspikestooltip = Tooltip(minspikeslabel, 'Define the minimal amount of spikes a burst should have before being considered as one')
minspikeslabel.bind("<Enter>", minspikestooltip.show_tooltip)
minspikeslabel.bind("<Leave>", minspikestooltip.hide_tooltip)
minspikesinput=ttk.Entry(master=burstdetectionparameters)
minspikesinput.grid(row=0, column=1, padx=10, pady=10, sticky='w')

# Setup up the default threshold
defaultthlabel=ttk.Label(master=burstdetectionparameters, text="Default interval threshold:", font=(font,10))
defaultthlabel.grid(row=1, column=0, padx=10, pady=10, sticky='w')
defaultthtooltip = Tooltip(defaultthlabel, 'Define the default inter-spike interval threshold\nthat is used for burst detection\nValue should be given in miliseconds')
defaultthlabel.bind("<Enter>", defaultthtooltip.show_tooltip)
defaultthlabel.bind("<Leave>", defaultthtooltip.hide_tooltip)
defaultthinput=ttk.Entry(master=burstdetectionparameters)
defaultthinput.grid(row=1, column=1, padx=10, pady=10, sticky='w')

# Setup up the max threshold
maxisilabel=ttk.Label(master=burstdetectionparameters, text="Max interval threshold:", font=(font,10))
maxisilabel.grid(row=2, column=0, padx=10, pady=10, sticky='w')
maxisitooltip = Tooltip(maxisilabel, 'Define the maximum value the inter-spike interval threshold\ncan be when 2 peaks have been detected in the ISI graph\nValue should be given in miliseconds')
maxisilabel.bind("<Enter>", maxisitooltip.show_tooltip)
maxisilabel.bind("<Leave>", maxisitooltip.hide_tooltip)
maxisiinput=ttk.Entry(master=burstdetectionparameters)
maxisiinput.grid(row=2, column=1, padx=10, pady=10, sticky='w')

# Setup the KDE bandwidth
isikdebwlabel=ttk.Label(master=burstdetectionparameters, text="KDE bandwidth:", font=(font,10))
isikdebwlabel.grid(row=3, column=0, padx=10, pady=10, sticky='w')
isikdebwtooltip = Tooltip(isikdebwlabel, 'Define the bandwidth that is used when calculating the\nkernel density estimate of the inter-spike intervals')
isikdebwlabel.bind("<Enter>", isikdebwtooltip.show_tooltip)
isikdebwlabel.bind("<Leave>", isikdebwtooltip.hide_tooltip)
isikdebwinput=ttk.Entry(master=burstdetectionparameters)
isikdebwinput.grid(row=3, column=1, padx=10, pady=10, sticky='w')

# Setup the amount of smaller neighbours
smallernblabel=ttk.Label(master=burstdetectionparameters, text="Smaller neighbours:", font=(font,10))
smallernblabel.grid(row=4, column=0, padx=10, pady=10, sticky='w')
smallernbtooltip = Tooltip(smallernblabel, 'Define the amount of values next to the peak, that should be lower than the peak\nin order for it to be considered a peak in the distribution')
smallernblabel.bind("<Enter>", smallernbtooltip.show_tooltip)
smallernblabel.bind("<Leave>", smallernbtooltip.hide_tooltip)
smallernbinput=ttk.Entry(master=burstdetectionparameters)
smallernbinput.grid(row=4, column=1, padx=10, pady=10, sticky='w')

# Set up all the network burst detection parameters
networkburstdetectionparameters=ttk.LabelFrame(parameterframe.interior, text='Network Burst Detection', style="Custom.TLabelframe")
networkburstdetectionparameters.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

# Setup the minimum amount of channels participating
minchannelslabel=ttk.Label(master=networkburstdetectionparameters, text="Min channels:", font=(font,10))
minchannelslabel.grid(row=0, column=0, padx=10, pady=10, sticky='w')
minchannelstooltip = Tooltip(minchannelslabel, 'Define the minimal percentage of channels that should be active in a network burst, values ranges from 0 to 1')
minchannelslabel.bind("<Enter>", minchannelstooltip.show_tooltip)
minchannelslabel.bind("<Leave>", minchannelstooltip.hide_tooltip)
minchannelsinput=ttk.Entry(master=networkburstdetectionparameters)
minchannelsinput.grid(row=0, column=1, padx=10, pady=10, sticky='w')

# Setup the thresholding method
networkth_var = tk.StringVar(networkburstdetectionparameters)
nwthoptions = ['Yen', 'Otsu']
dropdownlabel = ttk.Label(master=networkburstdetectionparameters, text="Thresholding method:", font=(font,10))
dropdownlabel.grid(row=1, column=0, padx=10, pady=10, sticky='w')
dropdown_menu = ttk.OptionMenu(networkburstdetectionparameters, networkth_var, nwthoptions[0], *nwthoptions)
dropdown_menu.grid(row=1, column=1, padx=10, pady=10, sticky='nesw')

# Set up all the output parameters
outputparameters=ttk.LabelFrame(parameterframe.interior, text='Output/data manipulation', style="Custom.TLabelframe")
outputparameters.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

def removeinactivefunc():
    if removeinactivevar.get():
        activitythinput.configure(state='enabled')
    else:
        activitythinput.configure(state='disabled')

# Remove inactive electrodes
removeinactivelabel=ttk.Label(master=outputparameters, text="Remove inactive electrodes:", font=(font,10))
removeinactivelabel.grid(row=0, column=0, padx=10, pady=10, sticky='w')
removeinactivetooltip = Tooltip(removeinactivelabel, 'Should inactive electrodes be used when calculating well features?')
removeinactivelabel.bind("<Enter>", removeinactivetooltip.show_tooltip)
removeinactivelabel.bind("<Leave>", removeinactivetooltip.hide_tooltip)
removeinactivevar=IntVar()
removeinactiveinput=ttk.Checkbutton(outputparameters, onvalue=True, offvalue=False, variable=removeinactivevar, command=removeinactivefunc)
removeinactiveinput.grid(row=0, column=1, padx=10, pady=10, sticky='w')

# Setup the activity threshold
activitythlabel=ttk.Label(master=outputparameters, text="Activity threshold:", font=(font,10))
activitythlabel.grid(row=1, column=0, padx=10, pady=10, sticky='w')
activitythtooltip = Tooltip(activitythlabel, 'Define the minimal activity a channel has to have, to be used in calculating well features.\nValue should be given in hertz, so a value of 0.1 would mean\nany channel with less that 1 spike per 10 seconds will be removed')
activitythlabel.bind("<Enter>", activitythtooltip.show_tooltip)
activitythlabel.bind("<Leave>", activitythtooltip.hide_tooltip)
activitythinput=ttk.Entry(master=outputparameters)
activitythinput.grid(row=1, column=1, padx=10, pady=10, sticky='w')

def splitdatafunc():
    if splitdatavar.get():
        splitdatapartsinput.configure(state='enabled')
    else:
        splitdatapartsinput.configure(state='disabled')

# Split data
splitdatalabel=ttk.Label(master=outputparameters, text="Split data:", font=(font,10))
splitdatalabel.grid(row=2, column=0, padx=10, pady=10, sticky='w')
splitdatatooltip = Tooltip(splitdatalabel, 'Should the data be split up in shorter parts?\nSplitting data might be useful to turn one long measurement into several smaller measurements')
splitdatalabel.bind("<Enter>", splitdatatooltip.show_tooltip)
splitdatalabel.bind("<Leave>", splitdatatooltip.hide_tooltip)
splitdatavar=IntVar()
splitdatainput=ttk.Checkbutton(outputparameters, onvalue=True, offvalue=False, variable=splitdatavar, command=splitdatafunc)
splitdatainput.grid(row=2, column=1, padx=10, pady=10, sticky='w')

# Setup the activity threshold
splitdatapartslabel=ttk.Label(master=outputparameters, text="Parts:", font=(font,10))
splitdatapartslabel.grid(row=3, column=0, padx=10, pady=10, sticky='w')
splitdatapartstooltip = Tooltip(splitdatapartslabel, 'In how many smaller parts should the data be split?')
splitdatapartslabel.bind("<Enter>", splitdatapartstooltip.show_tooltip)
splitdatapartslabel.bind("<Leave>", splitdatapartstooltip.hide_tooltip)
splitdatapartsinput=ttk.Entry(master=outputparameters)
splitdatapartsinput.grid(row=3, column=1, padx=10, pady=10, sticky='w')

# Use multiprocessing
multiprocessingframe=ttk.Labelframe(master=parameterframe.interior, text="Other", style="Custom.TLabelframe")
multiprocessingframe.grid(row=2, column=1, padx=10, pady=10, sticky='nesw')
multiprocessinglabel=ttk.Label(master=multiprocessingframe, text="Use multiprocessing:", font=(font,10))
multiprocessinglabel.grid(row=0, column=0, padx=10, pady=10, sticky='e')
multiprocessingtooltip = Tooltip(multiprocessinglabel, 'Using multiprocessing means the electrodes will be analyzed in parallel, generally speeding up\nthe analysis. Multiprocessing might not work properly if the device\n you\'re using does not have sufficient RAM/CPU-cores')
multiprocessinglabel.bind("<Enter>", multiprocessingtooltip.show_tooltip)
multiprocessinglabel.bind("<Leave>", multiprocessingtooltip.hide_tooltip)
multiprocessingvar=IntVar()
multiprocessinginput=ttk.Checkbutton(multiprocessingframe, onvalue=True, offvalue=False, variable=multiprocessingvar)
multiprocessinginput.grid(row=0, column=1, padx=10, pady=10, sticky='w')

def set_default_parameters():
    # reset dropdown parameters
    dropdown_var.set("DMP_noisebased")
    networkth_var.set('Yen')
    # reset checkboxes
    removeinactivevar.set(True)
    splitdatavar.set(False)
    multiprocessingvar.set(False)
    splitdatapartsinput.configure(state='enabled')
    # Update other parameter availability
    if removeinactivevar.get():
        activitythinput.configure(state='enabled')
    else:
        activitythinput.configure(state='disabled')

    validation_method = dropdown_var.get()
    if validation_method=='DMP_noisebased':
        exittimeinput.configure(state="enabled")
        heightexceptioninput.configure(state="enabled")
        maxheightinput.configure(state="enabled")
        amplitudedropinput.configure(state="enabled")
    else:
        exittimeinput.configure(state="disabled")
        heightexceptioninput.configure(state="disabled")
        maxheightinput.configure(state="disabled")
        amplitudedropinput.configure(state="disabled")

    # reset the entry labels
    list=[lowcutoffinput, highcutoffinput, orderinput, thresholdportioninput, stdevmultiplierinput, RMSmultiplierinput, refractoryperiodinput, exittimeinput,
          amplitudedropinput, heightexceptioninput, maxheightinput, electrodeamntinput, minspikesinput, defaultthinput, maxisiinput, isikdebwinput, smallernbinput,
          minchannelsinput, activitythinput, splitdatapartsinput]
    defaults=[200, 3500, 2, 0.1, 5, 5, 0.001, 0.00024, 5, 1.5, 2, 12, 5, 100, 1000, 1, 10, 0.5, 0.1, 10]
    counter=0
    for parameter in list:
        parameter.delete(0, END)
        parameter.insert(0, defaults[counter])
        counter+=1
    hertzinput.delete(0, END)
    if splitdatavar.get():
        splitdatapartsinput.configure(state='enabled')
    else:
        splitdatapartsinput.configure(state='disabled')
    
set_default_parameters()

default_parameters=ttk.Button(master=parameterframe.interior, text="Restore default parameters", command=set_default_parameters)
default_parameters.grid(row=3, column=1, padx=10, pady=(10,20), sticky='nsew')
parameterframe.interior.rowconfigure(3, minsize=125)

def import_parameters():
    parametersfile = filedialog.askopenfilename(filetypes=[("Parameter file", "*.json")])
    parameters=json.load(open(parametersfile))
    # Enable all the entries so we can set the correct values
    entries=[activitythinput, exittimeinput, heightexceptioninput, maxheightinput, amplitudedropinput, splitdatapartsinput]
    for entry in entries:
        entry.configure(state="enabled")        
    # Set all the parameters to the values of the imported file
    hertzinput.delete(0, END)
    hertzinput.insert(0, parameters["sampling rate"])
    electrodeamntinput.delete(0, END)
    electrodeamntinput.insert(0, parameters["electrode amount"])
    lowcutoffinput.delete(0, END)
    lowcutoffinput.insert(0, parameters["low cutoff"])
    highcutoffinput.delete(0, END)
    highcutoffinput.insert(0, parameters["high cutoff"])
    orderinput.delete(0, END)
    orderinput.insert(0, parameters["order"])
    thresholdportioninput.delete(0, END)
    thresholdportioninput.insert(0, parameters["threshold portion"])
    stdevmultiplierinput.delete(0, END)
    stdevmultiplierinput.insert(0, parameters["standard deviation multiplier"])
    RMSmultiplierinput.delete(0, END)
    RMSmultiplierinput.insert(0, parameters["rms multiplier"])
    refractoryperiodinput.delete(0, END)
    refractoryperiodinput.insert(0, parameters["refractory period"])
    dropdown_var.set(parameters["spike validation method"])
    exittimeinput.delete(0, END)
    exittimeinput.insert(0, parameters["exit time"])
    amplitudedropinput.delete(0, END)
    amplitudedropinput.insert(0, parameters["drop amplitude"])
    heightexceptioninput.delete(0, END)
    heightexceptioninput.insert(0, parameters["height exception"])
    maxheightinput.delete(0, END)
    maxheightinput.insert(0, parameters["max drop amount"])
    minspikesinput.delete(0, END)
    minspikesinput.insert(0, parameters["minimal amount of spikes"])
    defaultthinput.delete(0, END)
    defaultthinput.insert(0, parameters["default interval threshold"])
    maxisiinput.delete(0, END)
    maxisiinput.insert(0, parameters["max interval threshold"])
    isikdebwinput.delete(0, END)
    isikdebwinput.insert(0, parameters["KDE bandwidth"])
    smallernbinput.delete(0, END)
    smallernbinput.insert(0, parameters["smaller neighbours"])
    minchannelsinput.delete(0, END)
    minchannelsinput.insert(0, parameters["min channels"])
    networkth_var.set(parameters["thresholding method"])
    removeinactivevar.set(bool(parameters["remove inactive electrodes"]))
    activitythinput.delete(0, END)
    activitythinput.insert(0, parameters["activity threshold"])
    splitdatavar.set(bool(parameters["split data"]))
    splitdatapartsinput.delete(0, END)
    splitdatapartsinput.insert(0, parameters["parts"])
    multiprocessingvar.set(bool(parameters["use multiprocessing"]))
        
    # Update other parameter availability
    if removeinactivevar.get():
        activitythinput.configure(state='enabled')
    else:
        activitythinput.configure(state='disabled')

    validation_method = dropdown_var.get()
    if validation_method=='DMP_noisebased':
        exittimeinput.configure(state="enabled")
        heightexceptioninput.configure(state="enabled")
        maxheightinput.configure(state="enabled")
        amplitudedropinput.configure(state="enabled")
    else:
        exittimeinput.configure(state="disabled")
        heightexceptioninput.configure(state="disabled")
        maxheightinput.configure(state="disabled")
        amplitudedropinput.configure(state="disabled")

    if splitdatavar.get():
        splitdatapartsinput.configure(state='enabled')
    else:
        splitdatapartsinput.configure(state='disabled')

default_parameters=ttk.Button(master=parameterframe.interior, text="Import parameters", command=import_parameters)
default_parameters.grid(row=3, column=2, padx=10, pady=(10,20), sticky='nsew')


def data_analysis():
    def close_progressbar():
        # Communicate to the progressbar that the analysis has crashed
        progressfile=f'{os.path.split(filename)[0]}/progress.npy'
        np.save(progressfile, ['crashed'])
    if multiprocessingvar.get():
        try:
            analyse_well(fileadress=filename, wells=wells, hertz=hertz, validation_method=validation_method, low_cutoff=low_cutoff, high_cutoff=high_cutoff, order=order, spikeduration=spikeduration,
                    exit_time_s=exit_time_s, electrode_amnt=electrode_amnt, kde_bandwidth=kde_bandwidth, smallerneighbours=smallerneighbours, minspikes_burst=minspikes_burst,
                    max_threshold=max_threshold, default_threshold=default_threshold, heightexception=heightexception, max_drop_amount=max_drop_amount, amplitude_drop_sd=amplitude_drop_sd,
                    stdevmultiplier=stdevmultiplier, RMSmultiplier=RMSmultiplier, min_channels=min_channels, threshold_method=threshold_method, activity_threshold=activity_threshold,
                    threshold_portion=threshold_portion, remove_inactive_electrodes=remove_inactive_electrodes, cut_data_bool=cut_data_bool, parts=parts, use_multiprocessing=True)
        except Exception as error:
            print(error)
            tk.messagebox.showerror(title='Error', message='Something went wrong with analyzing the data, please check if all the parameters are set correctly\nAlternatively, try analyzing the data with multiprocessing turned off')
            close_progressbar()
    else:
        try:
            analyse_well(fileadress=filename, wells=wells, hertz=hertz, validation_method=validation_method, low_cutoff=low_cutoff, high_cutoff=high_cutoff, order=order, spikeduration=spikeduration,
                        exit_time_s=exit_time_s, electrode_amnt=electrode_amnt, kde_bandwidth=kde_bandwidth, smallerneighbours=smallerneighbours, minspikes_burst=minspikes_burst,
                        max_threshold=max_threshold, default_threshold=default_threshold, heightexception=heightexception, max_drop_amount=max_drop_amount, amplitude_drop_sd=amplitude_drop_sd,
                        stdevmultiplier=stdevmultiplier, RMSmultiplier=RMSmultiplier, min_channels=min_channels, threshold_method=threshold_method, activity_threshold=activity_threshold,
                        threshold_portion=threshold_portion, remove_inactive_electrodes=remove_inactive_electrodes, cut_data_bool=cut_data_bool, parts=parts, use_multiprocessing=False)
        except Exception as error:
            print(error)
            tk.messagebox.showerror(title='Error', message='Something went wrong with analyzing the data, please check if all the parameters are set correctly')
            close_progressbar()

def progress():
    # Read out the progressbar from the file
    start=time.time()
    path=os.path.split(filename)[0]
    progressfile=f"{path}/progress.npy"
    popup=tk.Toplevel(root)
    popup.title('Progress')
    try:
        popup.iconbitmap(os.path.join(application_path))
    except Exception as error:
        print(error)
    progressinfo=ttk.Label(master=popup, text='The MEA data is being analyzed, please wait for the program to finish')
    progressinfo.grid(row=0, column=0, pady=10, padx=20)
    progressbarlength=1000
    progressbar=ttk.Progressbar(master=popup, length=progressbarlength, mode='determinate', maximum=progressbarlength)
    progressbar.grid(row=1, column=0, pady=10, padx=20)
    progressbar.step(0)
    info=ttk.Label(master=popup, text='')
    info.grid(row=2, column=0, pady=10, padx=20)
    while True:
        currenttime=time.time()
        elapsed=round(currenttime-start,1)
        try:
            progress=np.load(progressfile)
        except:
            progress=['starting']
        if progress[0]=='crashed':
            popup.destroy()
            os.remove(progressfile)
            return
        if progress[0]=='done':
            break
        elif progress[0]=='starting':
            info.configure(text=f'Loading raw data, time elapsed: {elapsed} seconds')
        else:
            currentprogress=(progress[0]/progress[1])*progressbarlength
            progressbar.configure(value=currentprogress)
            info.configure(text=f"Analyzing data, channel: {progress[0]}/{progress[1]}, time elapsed: {elapsed} seconds")
        time.sleep(0.01)
    popup.destroy()
    os.remove(progressfile)
    currenttime=time.time()
    elapsed=round(currenttime-start,2)
    finishedpopup=tk.Toplevel(root)
    finishedpopup.title('Finished')
    try:
        finishedpopup.iconbitmap(os.path.join(application_path))
    except Exception as error:
        print(error)
    finishedtext=ttk.Label(master=finishedpopup, text=f'The data has been analyzed. It took {elapsed} seconds')
    finishedtext.grid(column=0, row=0, padx=10, pady=10)
    
# Start the analysis
def go_to_analysisframe():
    # Check if the user has selected a file
    if filename == "":
        tk.messagebox.showerror(title='Error', message='No file has been selected yet, please select a file and set parameters')
        return
    # Start two seperate threads for analyzing the data and reading out the progress. This makes sure the main gui stays responsive
    data_thread=threading.Thread(target=data_analysis)
    data_thread.start()
    progress_thread=threading.Thread(target=progress)
    progress_thread.start()

def go_to_resultfileframe():
    resultfileframe.pack(fill='both', expand=True)
    main_frame.pack_forget()
    

analysisframe=ttk.Frame(root)
analysisframe.pack(fill='both', expand=True)
analysisframe.pack_forget()

btn_parameter=ttk.Button(master=main_frame, text="Start\nAnalysis", style="bigbutton.TButton", command=go_to_analysisframe)
btn_parameter.grid(row=0, column=1, padx=10, pady=10, sticky='nesw', ipadx=25, ipady=25)

# Select files to view results
resultfileframe=ttk.Frame(root)
resultfileframe.pack(fill='both', expand=True)
resultfileframe.pack_forget()

results_btn=ttk.Button(master=main_frame, text="View\nResults", style="bigbutton.TButton", command=go_to_resultfileframe)
results_btn.grid(row=1, column=0, padx=10, pady=10, sticky='nesw', ipadx=25, ipady=25)

def results_file_to_main_func():
    main_frame.pack(fill='both', expand=True)
    resultfileframe.pack_forget()

# Results file selection
datalocation=ttk.LabelFrame(resultfileframe, text='Data location', style="Custom.TLabelframe")
datalocation.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

resultsfolder=''    # default value
def openfolder():
    global resultsfolder
    resultsfolder = filedialog.askdirectory()
    if resultsfolder != '':
        btn_selectfolder.configure(text=resultsfolder)

# Open location of results
folderlabel=ttk.Label(master=datalocation, text="Folder:", font=(font,10))
folderlabel.grid(row=0, column=0, padx=10, pady=10)
btn_selectfolder=ttk.Button(master=datalocation, text="Select a folder", command=openfolder)
btn_selectfolder.grid(row=0, column=1, padx=10, pady=10)

def openrawfile():
    global filename
    selectedfile = filedialog.askopenfilename(filetypes=[("MEA data", "*.h5")])
    if len(selectedfile)!=0:
        filename=selectedfile
        btn_selectrawfile.configure(text=os.path.split(filename)[1])

# Open location of raw data
rawfilelabel=ttk.Label(master=datalocation, text="File:", font=(font,10))
rawfilelabel.grid(row=1, column=0, padx=10, pady=10)
btn_selectrawfile=ttk.Button(master=datalocation, text="Choose a file", command=openrawfile)
btn_selectrawfile.grid(row=1, column=1, padx=10, pady=10)

# View the results
resultsframe=ttk.Frame(root)
resultsframe.pack(fill='both', expand=True)
resultsframe.pack_forget()

# Results notebook
results_nb=ttk.Notebook(master=resultsframe)
results_nb.pack(fill='both', expand=True)

electrode_frame=ttk.Frame(master=results_nb)#, width=1920, height=800)
electrode_frame.pack(fill='both', expand=True)

well_frame=ttk.Frame(master=results_nb)#, width=1920, height=800)
well_frame.pack(fill='both', expand=True)

output_frame=ttk.Frame(master=results_nb)
output_frame.pack(fill='both', expand=True)

results_nb.add(electrode_frame, text='Single electrode view')
results_nb.add(well_frame, text='Whole well view')
results_nb.add(output_frame, text="Results")

'''Build the output_frame tab'''
table_frame=ttk.Frame(master=output_frame)
table_frame.grid(row=0, column=0, sticky='nesw', padx=25, pady=25)
output_frame.grid_columnconfigure(0, weight=1)
output_frame.grid_rowconfigure(0, weight=1)

output_frame.grid_rowconfigure(1, weight=1)

global raw_data

class treeview_table(ttk.Frame):
    def __init__(self, master, file_path):
        super().__init__(master)  # Initialize the parent class
        self.tableframe=ttk.Frame(self)
        self.tableframe.grid(row=0, column=0, sticky='nesw')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.tableframe.rowconfigure(0, weight=1)
        self.tableframe.columnconfigure(0, weight=1)

        self.button_frame=ttk.Frame(self)
        self.button_frame.grid(row=1, column=0, sticky='ew', pady=5)
        self.groupmanager=ttk.Frame(self.button_frame)
        self.groupmanager.grid(row=0, column=1, sticky='ew')
        self.group_frame=ttk.Frame(self)
        self.group_frame.grid(row=3, column=0, sticky='ew')

        self.file_path = file_path
        df = pd.read_csv(file_path)
        self.columns=list(df.columns)

        vert_scrollbar = ttk.Scrollbar(self.tableframe, orient="vertical")
        vert_scrollbar.grid(row=0, column=1, sticky='nesw')

        hor_scrollbar = ttk.Scrollbar(self.tableframe, orient="horizontal")
        hor_scrollbar.grid(row=1, column=0, sticky='nesw')

        self.tree = ttk.Treeview(self.tableframe, yscrollcommand=vert_scrollbar.set, xscrollcommand=hor_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nesw')

        vert_scrollbar.config(command=self.tree.yview)
        hor_scrollbar.config(command=self.tree.xview)
        # Define the columns
        self.tree["columns"] = self.columns
        width=100
        # Format the columns
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.heading("#0", text="")
        for feature in self.columns:
            self.tree.column(feature, anchor=tk.W, width=width)
            self.tree.heading(feature, text=feature)

        # Add data
        data = df.values.tolist()

        for item in data:
            self.tree.insert(parent='', index=tk.END, values=list(np.round(item,2)))
        self.currenttag=''
        def item_selected(event):
            for selected_item in self.tree.selection():
                # If the user tries to set the same tag again, deselect the row
                if len(self.tree.item(selected_item)['tags'])!=0 and self.tree.item(selected_item)['tags'][0]==self.currenttag:
                    self.tree.item(selected_item, tags=())
                else:
                    self.tree.item(selected_item, tags=self.currenttag)
            self.deselect_all()
        self.tree.bind('<<TreeviewSelect>>', item_selected)

        clearbutton=ttk.Button(self.button_frame, text='Clear all groups', command=self.clear_selection)
        clearbutton.grid(row=0, column=0, sticky='w')

        self.groups=[]
        self.buttons=[]

        add_group_button=ttk.Button(self.groupmanager, text='Add group:', command=self.add_group)
        add_group_button.grid(row=0, column=1, sticky='w')

        self.add_group_entry=ttk.Entry(self.groupmanager)
        self.add_group_entry.grid(row=0, column=2, sticky='w', padx=(0,10))

        self.colors= [
            "#FF5733",  # Vivid Red
            "#3357FF",  # Vivid Blue
            "#FF33A6",  # Vivid Pink
            "#33FFF0",  # Vivid Cyan
            "#FFD700",  # Vivid Yellow
            "#8A2BE2",  # Blue Violet
            "#FF4500",  # Orange Red
            "#32CD32",  # Lime Green
            "#9400D3",  # Dark Violet
            "#33FF57",  # Vivid Green
        ]

        # Create styles
        self.style = ttk.Style()
        for i, color in enumerate(self.colors):
            style_name = f"Custom{i}.TButton"
            self.style.configure(style_name, foreground=color)
            self.style.map(style_name, foreground=[('active', color)])

    def get_selection(self):
        dict={}
        for group in self.groups:
            temp=[]
            for item in self.tree.get_children():
                if len(self.tree.item(item)['tags'])!=0:
                    if str(self.tree.item(item)['tags'][0])==group:
                        temp.append(self.tree.item(item)['values'])
            dict[group]=temp
        return dict, self.columns, self.colors

    def set_tag(self, tag):
        self.currenttag=str(tag)

    def clear_selection(self):
        for item in self.tree.get_children():
            self.tree.item(item, tags=())

    def add_group(self):
        new_group=str(self.add_group_entry.get())
        if new_group != '' and new_group not in self.groups and len(self.groups)<10:
            self.groups.append(new_group)
        self.update_buttons()

    def update_buttons(self):
        # Remove buttons
        for button in self.buttons:
            button.destroy()
        for group in range(len(self.groups)):
            # Create tag
            self.tree.tag_configure(str(self.groups[group]), background=self.colors[group])
            # Create buttons
            button=ttk.Button(self.group_frame, text=self.groups[group], command=partial(self.set_tag, str(self.groups[group])), style=f"Custom{group}.TButton")
            button.grid(row=0, column=group, sticky='w')
            self.buttons.append(button)
    
    def deselect_all(self):
        for item in self.tree.selection():
            self.tree.selection_remove(item)

class graphs(ttk.Frame):
    def __init__(self, master, table):
        super().__init__(master)  # Initialize the parent class
        self.table=table
        self.buttonframe=ttk.Frame(self)
        self.buttonframe.grid(row=0, column=0, sticky='nesw')
        self.treeframe=ttk.Frame(self)
        self.treeframe.grid(row=1, column=0, sticky='nesw')
        
        self.update_graph_button=ttk.Button(self.buttonframe, text='Update table', command=self.update_table)
        self.update_graph_button.grid(row=0, column=0, sticky='new', pady=10)
        self.update_plot_button=ttk.Button(self.buttonframe, text='Create graph', command=self.update_plot)
        self.update_plot_button.grid(row=0, column=1, sticky='new', pady=10)
        self.disclaimer_label=ttk.Label(self.buttonframe, text="\nThe calculated p-value is merely to indicate where significant differences might be located\nIt should not be used to draw conclusions as it does not take into account the origin/source or distribution of the data")
        self.disclaimer_label.grid(row=0, column=2, pady=10, padx=10, sticky='new')

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.plot_values={}

        # Configure the treeview
        vert_scrollbar = ttk.Scrollbar(self.treeframe, orient="vertical")
        vert_scrollbar.grid(row=0, column=1, sticky='nesw')
        self.tree = ttk.Treeview(self.treeframe, yscrollcommand=vert_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nesw')
        vert_scrollbar.config(command=self.tree.yview)
        # Define the columns
        headers=["Feature", "p-value"]
        self.tree["columns"] = headers
        width=200
        # # Format the columns
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.heading("#0", text="")
        for header in headers:
            self.tree.column(header, anchor=tk.W, width=width)
            self.tree.heading(header, text=header)

        # colors for the boxplots
        self.palette=[]       
        # Create the fig and canvas
        self.figure = Figure()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.treeframe)
        self.canvas.get_tk_widget().grid(row=0, column=2, sticky='nesw')
        self.canvas.draw()

        self.treeframe.columnconfigure(2, weight=1) 
        self.treeframe.rowconfigure(0, weight=1)

        self.groups=[]

        if theme=='dark':
            self.bgcolor='#1c1c1c'
            self.axiscolour='#ecf3fa'
        else:
            self.bgcolor='#fafafa'
            self.axiscolour='#221c1c'
        self.figure.set_facecolor(self.bgcolor)


    def update_table(self):
        data, columns, colors=self.table.get_selection()
        # Retrieve the colors of the groups that are not empty
        temp_colors=[]
        temp_groups=[]
        keys=list(data.keys())
        for i in range(len(keys)):
            if len(data[keys[i]])!=0:
                temp_colors.append(colors[i])
                temp_groups.append(keys[i])
        self.palette=temp_colors
        self.groups=temp_groups
        # Remove entries where the list is empty
        data = {key: value for key, value in data.items() if value}
        if len(data)==0:
            tk.messagebox.showerror(title='Error', message='No rows selected')
            return
        if len(data)==1:
            tk.messagebox.showerror(title='Error', message='Not enough groups to compare, select at least 2 groups')
            return
        p_values=[]
        keys=list(data.keys())
        test_title="P_value"
        # If we have 2 groups, do t-tests for all features to make a ranking
        if len(data)==2:
            test_title="P_value (t-test)"
            group1=np.array(data[keys[0]]).astype(float)
            group2=np.array(data[keys[1]]).astype(float)
            # Skip the first column because this is the well number
            for i in range(1,len(columns)):
                t_stat, p_value = stats.ttest_ind(group1[:,i], group2[:,i])
                p_values.append(p_value)
                self.plot_values[columns[i]]=[group1[:,i], group2[:,i]]
        # If we have more than 2 groups, perform an anova
        if len(data)>2:
            test_title="P_value (ANOVA)"
            for i in range(1,len(columns)):
                anova_data=[]
                for key in keys:
                    anova_data.append(np.array(data[key]).astype(float)[:,i])
                t_stat, p_value=stats.f_oneway(*anova_data)
                p_values.append(p_value)
                self.plot_values[columns[i]]=anova_data
        self.update_graph_button.configure(text="Update table")
        
        headers=["Feature", test_title]
        self.tree["columns"] = headers
        for header in headers:
            self.tree.heading(header, text=header)

        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Insert the new values
        for i in range(len(p_values)):
            self.tree.insert(parent='', index=tk.END, values=[columns[i+1], p_values[i]])

        self.tree.tag_configure('selected', background="#bb86fc")

        def item_selected(event):
            # Either select or deselect the items
            for selected_item in self.tree.selection():
                if len(self.tree.item(selected_item)['tags'])!=0:
                    self.tree.item(selected_item, tags=())
                else:
                    self.tree.item(selected_item, tags='selected')
            for item in self.tree.selection():
                self.tree.selection_remove(item)
        self.tree.bind('<<TreeviewSelect>>', item_selected)

    def update_plot(self):
        labels=[]
        for item in self.tree.get_children():
            if len(self.tree.item(item)['tags'])!=0:
                labels.append(self.tree.item(item)['values'][0])
        if len(labels)>0:
            self.update_plot_button.configure(text='Update graph')

            # First remove all previous axes
            while self.figure.axes:
                self.figure.delaxes(self.figure.axes[0])
            # Create multiple different plots
            self.axes = self.figure.subplots(1, len(labels))
            for i in range(len(labels)):
                if len(labels)==1:
                    ax=self.axes
                else:
                    ax=self.axes.flatten()[i]
                data_df=[]
                for array in range(len(self.plot_values[labels[i]])):
                    df = pd.DataFrame({'Group': self.groups[array], 'Value': self.plot_values[labels[i]][array]})
                    data_df.append(df)
                data_df = pd.concat(data_df, ignore_index=True)
                sns.boxplot(x='Group', y='Value', data=data_df, palette=self.palette, ax=ax)
                sns.stripplot(x='Group', y='Value', data=data_df, jitter=True, palette=[self.axiscolour]*len(self.palette), ax=ax)
                #ax.set_xticks(ticks=range(len(self.groups)), labels=self.groups)
                ax.set_title(f"{labels[i]}")

            # Set the correct colours
            for ax in self.figure.axes:
                ax.set_facecolor(self.bgcolor)
                # Change the other colours
                ax.xaxis.label.set_color(self.axiscolour)
                ax.yaxis.label.set_color(self.axiscolour)
                for side in ['top', 'bottom', 'left', 'right']:
                    ax.spines[side].set_color(self.axiscolour)
                ax.tick_params(axis='x', colors=self.axiscolour)
                ax.tick_params(axis='y', colors=self.axiscolour)
                ax.set_title(label=ax.get_title(),color=self.axiscolour)
            self.canvas.draw()

def load_table(file_path):
    results_window=tk.Toplevel(master=output_frame)
    try:
        results_window.iconbitmap(os.path.join(application_path))
    except Exception as error:
        print(error)
    results_window.title("Results")
    results_window.geometry("500x500") # Set dimensions in pixels 
    table=treeview_table(results_window, file_path)
    table.grid(row=0,column=0, sticky='nesw')
    graph=graphs(results_window, table)
    graph.grid(row=1, column=0, sticky='nesw')
    results_window.columnconfigure(0, weight=1)
    results_window.rowconfigure(0, weight=2)
    results_window.rowconfigure(1, weight=1)

# Add buttons for selecting which results to load
feature_filepath=''
def get_feature_filepath():
    global feature_filepath
    temp=filedialog.askopenfilename(filetypes=[("Feature file", "*.csv")])
    if temp != '':
        feature_filepath=temp
    choose_featurefile_button.configure(text=feature_filepath)

choose_featurefile_button=ttk.Button(master=output_frame, text="Choose a Features.csv file to analyse", command=get_feature_filepath)
choose_featurefile_button.grid(row=0, column=0, pady=10, padx=10, sticky='n')
load_table_button=ttk.Button(master=output_frame, text='Load table', command=lambda: load_table(feature_filepath))
load_table_button.grid(row=1, column=0, pady=10, padx=10, sticky='n')

selected_well = 1
selected_electrode = 1

view_results=ttk.Button(master=resultfileframe, text="View results", compound=LEFT, command=lambda: threading.Thread(target=view_results_func).start())
view_results.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

results_file_to_main=ttk.Button(master=resultfileframe, text="Back", command=results_file_to_main_func)
results_file_to_main.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

# Single electrode frame
choose_well=ttk.LabelFrame(master=electrode_frame, text='Select a well', style="Custom.TLabelframe")
choose_well.grid(column=0, row=0, sticky='nw', padx=10)

# Choose electrode
choose_electrode=ttk.LabelFrame(master=electrode_frame, text='Select an electrode', style="Custom.TLabelframe")
choose_electrode.grid(column=1, row=0, sticky='nw', padx=10)

def well_button_pressed(well):
    global selected_well
    selected_well=well

# Function to calculate the initial grid
def calculate_optimal_grid(num_wells):
    min_difference = num_wells
    optimal_width = num_wells
    optimal_height = 1
    
    for width in range(1, int(math.sqrt(num_wells)) + 1):
        if num_wells % width == 0:
            height = num_wells // width
            difference = abs(width - height)
            if difference < min_difference:
                min_difference = difference
                optimal_width = width
                optimal_height = height
    
    return int(optimal_width), int(optimal_height)

def create_wellbuttons(master, wells, button_command):
    ywells, xwells=calculate_optimal_grid(wells)
    wellbuttons=[]
    i=1

    for y in range(ywells):
        for x in range(xwells):
            well_btn=ttk.Button(master=master, text=i, command=partial(button_command, i), style="wellbutton.TButton")
            well_btn.grid(row=y, column=x, sticky='nesw', ipadx=25, ipady=25)
            wellbuttons.append(well_btn)
            i+=1
    return wellbuttons

'''This function takes the amount of electrodes the MEA has, and creates a correctly
sized grid with buttons for it'''
def create_electrodebuttons(master, electrode_amnt, button_command):
    # Two presets for a 12 and 16 electrode MEA
    if electrode_amnt==12:
        electrode_layout=np.array([ [False, True, True, False],
                                    [True, True, True, True],
                                    [True, True, True, True],
                                    [False, True, True, False]])
    elif electrode_amnt==16:    
        electrode_layout=np.array([ [True, True, True, True],
                                    [True, True, True, True],
                                    [True, True, True, True],
                                    [True, True, True, True]])
    # If the MEA has a different amount of electrodes than 12 or 16, we calculate the grid with the following function
    else:
        height, width = calculate_optimal_grid(electrode_amnt)
        electrode_layout = np.ones((height, width), dtype=bool)
    i = 1
    electrodebuttons=[]

    # Loop over the grid
    for x in range(electrode_layout.shape[0]):
        for y in range(electrode_layout.shape[1]):
            if electrode_layout[x,y]:
                # And create a button for each of the electrodes
                electrode_btn=ttk.Button(master=master, text=i, command=partial(button_command, i), style="mediumbutton.TButton")
                electrode_btn.grid(row=x, column=y, sticky='nesw', ipadx=25, ipady=25)
                electrodebuttons.append(electrode_btn)
                i+=1
    return electrodebuttons

def plot_network_bursts(master, parameters, well):
    fig=network_burst_detection(outputpath=resultsfolder, wells=[well], electrode_amnt=parameters["electrode amount"], measurements=parameters["measurements"], hertz=parameters["sampling rate"], min_channels=parameters["min channels"], threshold_method=parameters["thresholding method"], plot_electrodes=True, savedata=False, save_figures=False)
    if theme=='dark':
        bgcolor='#1c1c1c'
        axiscolour='#ecf3fa'
    else:
        bgcolor='#fafafa'
        axiscolour='#221c1c'
    fig.set_facecolor(bgcolor)
    for ax in fig.axes:
        ax.set_facecolor(bgcolor)
        # Change the other colours
        ax.xaxis.label.set_color(axiscolour)
        ax.yaxis.label.set_color(axiscolour)
        for side in ['top', 'bottom', 'left', 'right']:
            ax.spines[side].set_color(axiscolour)
        ax.tick_params(axis='x', colors=axiscolour)
        ax.tick_params(axis='y', colors=axiscolour)
        ax.set_title(label=ax.get_title(),color=axiscolour)

    plot_canvas = FigureCanvasTkAgg(fig, master=master)  
    plot_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
    toolbarframe=ttk.Frame(master=master)
    toolbarframe.grid(row=1, column=0, sticky='s')
    toolbar = NavigationToolbar2Tk(plot_canvas, toolbarframe)
    toolbar.update()
    plot_canvas.draw()

def plot_electrode_activity(master, parameters, well, bandwidth):
    fig=well_electrodes_kde(outputpath=resultsfolder, well=well, electrode_amnt=parameters["electrode amount"], measurements=parameters["measurements"], hertz=parameters["sampling rate"], bandwidth=bandwidth)
    if theme=='dark':
        bgcolor='#1c1c1c'
        axiscolour='#ecf3fa'
    else:
        bgcolor='#fafafa'
        axiscolour='#221c1c'
    fig.set_facecolor(bgcolor)
    for ax in fig.axes:
        ax.set_facecolor(bgcolor)
        # Change the other colours
        ax.xaxis.label.set_color(axiscolour)
        ax.yaxis.label.set_color(axiscolour)
        for side in ['top', 'bottom', 'left', 'right']:
            ax.spines[side].set_color(axiscolour)
        ax.tick_params(axis='x', colors=axiscolour)
        ax.tick_params(axis='y', colors=axiscolour)
        ax.set_title(label=ax.get_title(),color=axiscolour)

    plot_canvas = FigureCanvasTkAgg(fig, master=master)  
    plot_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
    toolbarframe=ttk.Frame(master=master)
    toolbarframe.grid(row=1, column=0)
    toolbar = NavigationToolbar2Tk(plot_canvas, toolbarframe)
    toolbar.update()
    plot_canvas.draw()

def network_visualization(well):
    # Open a new window and setup the notebook
    main_well_window=tk.Toplevel(master=well_frame)
    main_well_window.title(f'Well: {well}')
    try:
        main_well_window.iconbitmap(os.path.join(application_path))
    except Exception as error:
        print(error)

    well_nb=ttk.Notebook(master=main_well_window)
    well_nb.pack(fill='both', expand=True)
    
    network_burst_detection=ttk.Frame(master=well_nb)
    network_burst_detection.pack(expand=True, fill='both')

    electrode_activity=ttk.Frame(master=well_nb)
    electrode_activity.pack(expand=True, fill='both')

    well_nb.add(network_burst_detection, text='Network burst detection')
    well_nb.add(electrode_activity, text='Electrode activity')

    '''Network burst detection'''
    network_burst_plot_frame=ttk.Frame(master=network_burst_detection)
    network_burst_plot_frame.grid(row=0, column=0, sticky='nesw')
    network_burst_plot_frame.grid_columnconfigure(0, weight=1)
    network_burst_plot_frame.grid_rowconfigure(0, weight=1)

    # Load the parameters
    parameters=open(f"{resultsfolder}/parameters.json")
    parameters=json.load(parameters)

    # Initial plot
    plot_network_bursts(master=network_burst_plot_frame, parameters=parameters, well=well)

    network_burst_detection.grid_columnconfigure(0, weight=1)
    network_burst_detection.grid_rowconfigure(0, weight=3)

    # Frame for the NB settings
    nb_settings_frame=ttk.Labelframe(master=network_burst_detection, text="Network burst detection settings", style="Custom.TLabelframe")
    nb_settings_frame.grid(row=1, column=0, padx=10, pady=10)

    # NB settings disclaimer
    nbd_disclaimer_label=ttk.Label(master=nb_settings_frame, text="Warning: altering these settings will have no effect on the output of the application\nor further analysis steps such as feature calculation.\nThese settings are here purely to visualize how these parameters could alter the analysis pipeline")
    nbd_disclaimer_label.grid(row=0, column=2, rowspan=2, pady=10, padx=10, sticky='w')

    # NB settings
    min_channels_nb_label=ttk.Label(master=nb_settings_frame, text="Min channels (%)").grid(row=0, column=0, sticky='w', padx=10, pady=10)
    min_channels_nb_entry=ttk.Entry(master=nb_settings_frame)
    min_channels_nb_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)
    
    th_method_nb_var = tk.StringVar(nb_settings_frame)
    nwthoptions_nb = ['Yen', 'Otsu']
    th_method_nb = ttk.Label(master=nb_settings_frame, text="Thresholding method:")
    th_method_nb.grid(row=1, column=0, padx=10, pady=10, sticky='w')
    th_method_dropdown_nb = ttk.OptionMenu(nb_settings_frame, th_method_nb_var, nwthoptions_nb[0], *nwthoptions_nb)
    th_method_dropdown_nb.grid(row=1, column=1, padx=10, pady=10, sticky='w')

    def nb_default_values():
        th_method_nb_var.set(parameters["thresholding method"])
        min_channels_nb_entry.delete(0,END)
        min_channels_nb_entry.insert(0,parameters["min channels"])

    nb_default_values()

    def nb_update_plot():
        temp_parameters=copy.deepcopy(parameters)
        temp_parameters["min channels"]=float(min_channels_nb_entry.get())
        temp_parameters["thresholding method"]=str(th_method_nb_var.get())

        plot_network_bursts(master=network_burst_plot_frame, parameters=temp_parameters, well=well)

    def nb_reset():
        nb_default_values()
        nb_update_plot()

    nb_update_plot_button=ttk.Button(master=nb_settings_frame, text="Update plot", command=nb_update_plot)
    nb_update_plot_button.grid(row=2, column=0, sticky='nesw', padx=10, pady=10)

    nb_reset_button=ttk.Button(master=nb_settings_frame, text="Reset", command=nb_reset)
    nb_reset_button.grid(row=2, column=1, sticky='nesw', padx=10, pady=10)

    '''Electrode activity'''
    electrode_activity_plot_frame=ttk.Frame(master=electrode_activity)
    electrode_activity_plot_frame.grid(row=0, column=0, sticky='nsew')
    electrode_activity_plot_frame.grid_columnconfigure(0, weight=1)
    electrode_activity_plot_frame.grid_rowconfigure(0, weight=1)
    electrode_activity.grid_columnconfigure(0, weight=1)
    electrode_activity.grid_rowconfigure(0, weight=1)

    def_bw_value=0.1
    plot_electrode_activity(master=electrode_activity_plot_frame, parameters=parameters, well=well, bandwidth=def_bw_value)

    electrode_activity_settings=ttk.Frame(master=electrode_activity)
    electrode_activity_settings.grid(row=1, column=0)

    el_act_bw_label=ttk.Label(master=electrode_activity_settings, text="KDE bandwidth")
    el_act_bw_label.grid(row=0, column=0, sticky='nesw', padx=10, pady=10)
    el_act_bw_entry=ttk.Entry(master=electrode_activity_settings)
    el_act_bw_entry.grid(row=0, column=1, sticky='nesw', pady=10, padx=10)
    el_act_bw_entry.insert(0, def_bw_value)

    def update_electrode_activity():
        plot_electrode_activity(master=electrode_activity_plot_frame, parameters=parameters, well=well, bandwidth=float(el_act_bw_entry.get()))
    
    el_act_update_plot=ttk.Button(master=electrode_activity_settings, text='Update plot', command=update_electrode_activity)
    el_act_update_plot.grid(row=1, column=0, sticky='nesw', padx=10, pady=10)

    def reset_electrode_activity():
        el_act_bw_entry.delete(0, END)
        el_act_bw_entry.insert(0, def_bw_value)
        update_electrode_activity()

    el_act_reset=ttk.Button(master=electrode_activity_settings, text='Reset', command=reset_electrode_activity)
    el_act_reset.grid(row=1, column=1, sticky='nesw', padx=10, pady=10)


choose_well_nw=ttk.LabelFrame(master=well_frame, text='Select a well', style="Custom.TLabelframe")
choose_well_nw.grid(column=0, row=0, sticky='nesw', padx=10)

'''This function handles all the preparation necessary for properly viewing the analysed data'''
def view_results_func():
    global resultsfolder

    # Load in the correct files
    global raw_data
    # Check if the correct files have been selected
    if os.path.exists(f"{resultsfolder}/burst_values") and os.path.exists(f"{resultsfolder}/spike_values") and os.path.exists(f"{resultsfolder}/network_data"):
        try:
            loaddatapopup=tk.Toplevel(resultfileframe)
            loaddatapopup.title('Progress')
            try:
                loaddatapopup.iconbitmap(os.path.join(application_path))
            except Exception as error:
                print(error)
            progressinfo=ttk.Label(master=loaddatapopup, text='Loading in the raw data...')
            progressinfo.grid(row=0, column=0, pady=10, padx=20)
            raw_data=openHDF5(filename)
        except Exception as error:
            print(error)
            tk.messagebox.showerror(title='Error', message='Could not load in the raw data, please make sure you have selected the correct file')
            loaddatapopup.destroy()
            return
    else:
        tk.messagebox.showerror(title='Error', message='Could not load in the results, please make sure you have selected the correct folder')
        return
    global feature_filepath
    feature_filepath=f"{resultsfolder}/Features.csv"
    choose_featurefile_button.configure(text=feature_filepath)
    # Load the parameters
    parameters=open(f"{resultsfolder}/parameters.json")
    parameters=json.load(parameters)
    electrode_wellbuttons=create_wellbuttons(choose_well, raw_data.shape[0]/parameters["electrode amount"], well_button_pressed)
    whole_wellbuttons=create_wellbuttons(choose_well_nw, raw_data.shape[0]/parameters["electrode amount"], network_visualization)
    electrode_buttons=create_electrodebuttons(choose_electrode, parameters["electrode amount"], electrode_button_pressed)
    loaddatapopup.destroy()
    resultsframe.pack(fill='both', expand=True)
    resultfileframe.pack_forget()


def plot_single_electrode(master, parameters, electrode_nr, plot_rectangle):
    electrode_data=butter_bandpass_filter(raw_data[electrode_nr], lowcut=parameters["low cutoff"], highcut=parameters["high cutoff"], fs=parameters["sampling rate"], order=parameters["order"])
    threshold=fast_threshold(electrode_data, hertz=parameters["sampling rate"], stdevmultiplier=parameters["standard deviation multiplier"], RMSmultiplier=parameters["rms multiplier"], threshold_portion=parameters["threshold portion"])
    fig=spike_validation(data=electrode_data, electrode=electrode_nr, threshold=threshold, hertz=parameters["sampling rate"], spikeduration=parameters["refractory period"], exit_time_s=parameters["exit time"], amplitude_drop=parameters["drop amplitude"], plot_electrodes=True, electrode_amnt=parameters["electrode amount"], heightexception=parameters["height exception"], max_drop_amount=parameters["max drop amount"], outputpath='', savedata=False, plot_rectangles=plot_rectangle)
    # Check which colorscheme we have to use
    if theme=='dark':
        bgcolor='#1c1c1c'
        axiscolour='#ecf3fa'
    else:
        bgcolor='#fafafa'
        axiscolour='#221c1c'
    # Set the plot background
    fig.set_facecolor(bgcolor)
    ax=fig.axes[0]
    ax.set_facecolor(bgcolor)

    # Change the other colours
    ax.xaxis.label.set_color(axiscolour)
    ax.yaxis.label.set_color(axiscolour)
    for side in ['top', 'bottom', 'left', 'right']:
        ax.spines[side].set_color(axiscolour)
    ax.tick_params(axis='x', colors=axiscolour)
    ax.tick_params(axis='y', colors=axiscolour)
    ax.set_title(label=ax.get_title(),color=axiscolour)

    plot_canvas = FigureCanvasTkAgg(fig, master=master)  
    plot_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
    toolbarframe=ttk.Frame(master=master)
    toolbarframe.grid(row=1, column=0, sticky='s')
    toolbar = NavigationToolbar2Tk(plot_canvas, toolbarframe)
    toolbar.update()
    plot_canvas.draw()

def plot_burst_detection(master, parameters, electrode_nr):
    electrode_data=butter_bandpass_filter(raw_data[electrode_nr], lowcut=parameters["low cutoff"], highcut=parameters["high cutoff"], fs=parameters["sampling rate"], order=parameters["order"])
    KDE_fig, burst_fig = burst_detection(data=electrode_data, electrode=electrode_nr, electrode_amnt=parameters["electrode amount"], hertz=parameters["sampling rate"], kde_bandwidth=parameters["KDE bandwidth"], smallerneighbours=parameters["smaller neighbours"], minspikes_burst=parameters["minimal amount of spikes"], max_threshold=parameters["max interval threshold"], default_threshold=parameters["default interval threshold"], outputpath=resultsfolder, plot_electrodes=True, savedata=False)
    
    # Change the colours of the graph
    if theme=='dark':
        bgcolor='#1c1c1c'
        axiscolour='#ecf3fa'
    else:
        bgcolor='#fafafa'
        axiscolour='#221c1c'
    for fig in [KDE_fig, burst_fig]:
        fig.set_facecolor(bgcolor)
        ax=fig.axes[0]
        ax.set_facecolor(bgcolor)
        # Change the other colours
        ax.xaxis.label.set_color(axiscolour)
        ax.yaxis.label.set_color(axiscolour)
        for side in ['top', 'bottom', 'left', 'right']:
            ax.spines[side].set_color(axiscolour)
        ax.tick_params(axis='x', colors=axiscolour)
        ax.tick_params(axis='y', colors=axiscolour)
        ax.set_title(label=ax.get_title(),color=axiscolour)
    # Plot the raw burst plot
    burst_canvas = FigureCanvasTkAgg(burst_fig, master=master)  
    burst_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
    bursttoolbarframe=ttk.Frame(master=master)
    bursttoolbarframe.grid(row=1, column=0, sticky='s', columnspan=2)
    bursttoolbar = NavigationToolbar2Tk(burst_canvas, bursttoolbarframe)
    bursttoolbar.update()
    burst_canvas.draw()

    # Plot the KDE plot
    KDE_canvas = FigureCanvasTkAgg(KDE_fig, master=master)  
    KDE_canvas.get_tk_widget().grid(row=0, column=1, sticky='nsew')
    # KDEtoolbarframe=ttk.Frame(master=master)
    # KDEtoolbarframe.grid(row=1, column=1, sticky='s')
    # KDEtoolbar = NavigationToolbar2Tk(KDE_canvas, KDEtoolbarframe)
    # KDEtoolbar.update()

    master.grid_columnconfigure(0, weight=3)
    master.grid_columnconfigure(1, weight=1)
    master.grid_rowconfigure(0, weight=1)
    KDE_canvas.draw()

def electrode_button_pressed(electrode):
    global selected_electrode
    selected_electrode=electrode

    # Open a new window
    main_electrode_window=tk.Toplevel(master=electrode_frame)
    main_electrode_window.title(f'Well: {selected_well}, electrode: {selected_electrode}')
    try:
        main_electrode_window.iconbitmap(os.path.join(application_path))
    except Exception as error:
        print(error)

    electrode_nb=ttk.Notebook(master=main_electrode_window)
    electrode_nb.pack(fill='both', expand=True)
    
    electrode_window=ttk.Frame(master=electrode_nb)
    electrode_window.pack(expand=True, fill='both')

    burst_frame=ttk.Frame(master=electrode_nb)
    burst_frame.pack(fill='both', expand=True)

    electrode_nb.add(electrode_window, text='Spike detection')
    electrode_nb.add(burst_frame, text='Burst detection')

    # Load the parameters
    parameters=open(f"{resultsfolder}/parameters.json")
    parameters=json.load(parameters)
    electrode_nr=(selected_well-1)*parameters["electrode amount"]+selected_electrode-1

    # Button to create/update the plot
    def update_plot():
        # Get the new parameters from the entry widgets
        # Create a temporary dict we will give to the plot electrode function
        temp_parameters=copy.deepcopy(parameters)
        temp_parameters['low cutoff']=int(lowcut_ew_entry.get())
        temp_parameters['high cutoff']=int(highcut_ew_entry.get())
        temp_parameters['order']=int(order_ew_entry.get())
        temp_parameters['standard deviation multiplier']=float(stdevmultiplier_ew_entry.get())
        temp_parameters['rms multiplier']=float(RMSmultiplier_ew_entry.get())
        temp_parameters['threshold portion']=float(thpn_ew_entry.get())
        temp_parameters['refractory period']=float(rfpd_ew_entry.get())
        if str(validation_method_var.get())=='none':
            temp_parameters['drop amplitude']=0
        else:
            temp_parameters['exit time']=float(exittime_ew_entry.get())
            temp_parameters['drop amplitude']=float(dropamplitude_ew_entry.get())
            temp_parameters['height exception']=float(heightexc_ew_entry.get())
            temp_parameters['max drop amount']=float(maxdrop_ew_entry.get())

        # Plot the electrode with the new parameters
        plot_single_electrode(electrode_window, temp_parameters, electrode_nr, plot_rectangle.get())

    # Set the weights
    electrode_window.grid_columnconfigure(0, weight=1)
    electrode_window.grid_rowconfigure(0, weight=3)
    electrode_window.grid_rowconfigure(2, weight=1)

    # Create a frame for the settings
    electrode_settings_frame=ttk.Frame(master=electrode_window)
    electrode_settings_frame.grid(row=2, column=0)

    # Bandpass options
    bp_options_ew_frame = ttk.LabelFrame(master=electrode_settings_frame, text='Bandpass Filter', style="Custom.TLabelframe")
    bp_options_ew_frame.grid(row=0, column=0, pady=10, padx=10, sticky='nsew')

    lowcut_label=ttk.Label(master=bp_options_ew_frame, text='Low cutoff', font=(font,10)).grid(row=0, column=0, pady=10, padx=10, sticky='w')
    lowcut_ew_entry=ttk.Entry(master=bp_options_ew_frame)
    lowcut_ew_entry.grid(row=0, column=1, pady=10, padx=10, sticky='w')
    highcut_label=ttk.Label(master=bp_options_ew_frame, text='High cutoff', font=(font,10)).grid(row=1, column=0, sticky='w', pady=10, padx=10)
    highcut_ew_entry=ttk.Entry(master=bp_options_ew_frame)
    highcut_ew_entry.grid(row=1, column=1, pady=10, padx=10, sticky='w')
    order_label=ttk.Label(master=bp_options_ew_frame, text='Order', font=(font,10)).grid(row=2, column=0, sticky='w', pady=10, padx=10)
    order_ew_entry=ttk.Entry(master=bp_options_ew_frame)
    order_ew_entry.grid(row=2, column=1, pady=10, padx=10, sticky='w')

    # Threshold options
    th_options_ew_frame = ttk.LabelFrame(master=electrode_settings_frame, text='Threshold', style="Custom.TLabelframe")
    th_options_ew_frame.grid(row=0, column=1, pady=10, padx=10, sticky='nesw')
    
    stdevmultiplier_label=ttk.Label(master=th_options_ew_frame, text='Standard deviation multiplier', font=(font,10)).grid(row=0, column=0, pady=10, padx=10, sticky='w')
    stdevmultiplier_ew_entry=ttk.Entry(master=th_options_ew_frame)
    stdevmultiplier_ew_entry.grid(row=0, column=1, pady=10, padx=10, sticky='w')
    RMSmultiplier_label=ttk.Label(master=th_options_ew_frame, text='RMS multiplier', font=(font,10)).grid(row=1, column=0, sticky='w', pady=10, padx=10)
    RMSmultiplier_ew_entry=ttk.Entry(master=th_options_ew_frame)
    RMSmultiplier_ew_entry.grid(row=1, column=1, pady=10, padx=10, sticky='w')
    thpn_label=ttk.Label(master=th_options_ew_frame, text='Threshold portion', font=(font,10)).grid(row=2, column=0, sticky='w', pady=10, padx=10)
    thpn_ew_entry=ttk.Entry(master=th_options_ew_frame)
    thpn_ew_entry.grid(row=2, column=1, pady=10, padx=10, sticky='w')

    # Spike validation options
    val_options_ew_frame = ttk.LabelFrame(master=electrode_settings_frame, text='Spike validation', style="Custom.TLabelframe")
    val_options_ew_frame.grid(row=0, column=2, pady=10, padx=10)

    def set_states():
        validation_method = validation_method_var.get()
        if validation_method=='DMP_noisebased':
            exittime_ew_entry.configure(state="enabled")
            heightexc_ew_entry.configure(state="enabled")
            maxdrop_ew_entry.configure(state="enabled")
            dropamplitude_ew_entry.configure(state="enabled")
            plot_rectangle_ew_entry.configure(state="enabled")
        else:
            exittime_ew_entry.configure(state="disabled")
            heightexc_ew_entry.configure(state="disabled")
            maxdrop_ew_entry.configure(state="disabled")
            dropamplitude_ew_entry.configure(state="disabled")
            plot_rectangle.set(False)
            plot_rectangle_ew_entry.configure(state="disabled")
    def ew_option_selected(event):
        set_states()
    
    
    validation_method_var = tk.StringVar(validationparameters)
    validation_options = ['DMP_noisebased', 'none']
    validation_method_label = ttk.Label(master=val_options_ew_frame, text="Spike validation method:", font=(font,10))
    validation_method_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
    validation_method_entry = ttk.OptionMenu(val_options_ew_frame, validation_method_var, validation_options[0], *options, command=ew_option_selected)
    validation_method_entry.grid(row=0, column=1, padx=10, pady=10, sticky='nesw')

    rfpd_label=ttk.Label(master=val_options_ew_frame, text='Refractory period', font=(font,10)).grid(row=1, column=0, pady=10, padx=10, sticky='w')
    rfpd_ew_entry=ttk.Entry(master=val_options_ew_frame)
    rfpd_ew_entry.grid(row=1, column=1, pady=10, padx=10, sticky='w')
    exittime_label=ttk.Label(master=val_options_ew_frame, text='Exit time', font=(font,10)).grid(row=2, column=0, pady=10, padx=10, sticky='w')
    exittime_ew_entry=ttk.Entry(master=val_options_ew_frame)
    exittime_ew_entry.grid(row=2, column=1, pady=10, padx=10, sticky='w')
    dropamplitude_label=ttk.Label(master=val_options_ew_frame, text='Drop amplitude', font=(font,10)).grid(row=3, column=0, pady=10, padx=10, sticky='w')
    dropamplitude_ew_entry=ttk.Entry(master=val_options_ew_frame)
    dropamplitude_ew_entry.grid(row=3, column=1, pady=10, padx=10, sticky='w')
    heightexc_label=ttk.Label(master=val_options_ew_frame, text='Height exception', font=(font,10)).grid(row=1, column=2, pady=10, padx=10, sticky='w')
    heightexc_ew_entry=ttk.Entry(master=val_options_ew_frame)
    heightexc_ew_entry.grid(row=1, column=3, pady=10, padx=10, sticky='w')
    maxdrop_label=ttk.Label(master=val_options_ew_frame, text='Max drop amount', font=(font,10)).grid(row=2, column=2, pady=10, padx=10, sticky='w')
    maxdrop_ew_entry=ttk.Entry(master=val_options_ew_frame)
    maxdrop_ew_entry.grid(row=2, column=3, pady=10, padx=10, sticky='w')
    plot_rectangle_label=ttk.Label(master=val_options_ew_frame, text='Plot validation', font=(font,10))
    plot_rectangle_label.grid(row=3, column=2, pady=10, padx=10, sticky='w')
    plot_rectangle_tooltip = Tooltip(plot_rectangle_label, 'Display the rectangles that have been used to validate the spikes\nWarning: Plotting these is computationally expensive and might take a while')
    plot_rectangle_label.bind("<Enter>", plot_rectangle_tooltip.show_tooltip)
    plot_rectangle_label.bind("<Leave>", plot_rectangle_tooltip.hide_tooltip)
    plot_rectangle=BooleanVar()
    plot_rectangle_ew_entry=ttk.Checkbutton(master=val_options_ew_frame, variable=plot_rectangle)
    plot_rectangle_ew_entry.grid(row=3, column=3, pady=10, padx=10, sticky='w')

    # Insert the default values from the json in the entries
    def default_values():
        # Bandpass
        lowcut_ew_entry.delete(0,END)
        lowcut_ew_entry.insert(0,parameters["low cutoff"])
        highcut_ew_entry.delete(0,END)
        highcut_ew_entry.insert(0,parameters["high cutoff"])
        order_ew_entry.delete(0,END)
        order_ew_entry.insert(0,parameters["order"])
        # Threshold
        stdevmultiplier_ew_entry.delete(0,END)
        stdevmultiplier_ew_entry.insert(0,parameters["standard deviation multiplier"])
        RMSmultiplier_ew_entry.delete(0,END)
        RMSmultiplier_ew_entry.insert(0,parameters["rms multiplier"])
        thpn_ew_entry.delete(0,END)
        thpn_ew_entry.insert(0,parameters["threshold portion"])
        # Spike validation
        rfpd_ew_entry.delete(0,END)
        rfpd_ew_entry.insert(0,parameters["refractory period"])
        exittime_ew_entry.delete(0,END)
        exittime_ew_entry.insert(0,parameters["exit time"])
        dropamplitude_ew_entry.delete(0,END)
        dropamplitude_ew_entry.insert(0,parameters["drop amplitude"])
        heightexc_ew_entry.delete(0,END)
        heightexc_ew_entry.insert(0,parameters["height exception"])
        maxdrop_ew_entry.delete(0,END)
        maxdrop_ew_entry.insert(0,parameters["max drop amount"])
        plot_rectangle.set(False)
        validation_method_var.set(parameters['spike validation method'])
        set_states()

    def reset():
        # First, enable all the possibly disabled entries so we can alter the values
        exittime_ew_entry.configure(state="enabled")
        heightexc_ew_entry.configure(state="enabled")
        maxdrop_ew_entry.configure(state="enabled")
        dropamplitude_ew_entry.configure(state="enabled")
        plot_rectangle_ew_entry.configure(state="enabled")
        # Insert the new values
        default_values()
        # Update the availability of certain entries
        set_states()
        # Update the plot
        update_plot()

    # Set default values and create initial plot
    reset()
    
    update_plot_button=ttk.Button(master=electrode_settings_frame, text='Update plot', command=update_plot)
    update_plot_button.grid(row=1, column=0, pady=10, padx=10, sticky='nsew')

    reset_button = ttk.Button(master=electrode_settings_frame, text='Reset', command=reset)
    reset_button.grid(row=1, column=1, pady=10, padx=10, sticky='nsew')

    disclaimerlabel=ttk.Label(master=electrode_settings_frame, text='Warning: altering these settings will have no effect on the output of the application,\nor further analysis steps such as burst detection.\nThese settings are here purely to visualize how these parameters could alter the analysis pipeline', font=(font,10), anchor='e')
    disclaimerlabel.grid(row=1, column=2, pady=10, padx=10, sticky='nsew')

    # Now do the same for the burst window

    # Create the initial burst plot
    burstplotsframe=ttk.Frame(master=burst_frame)
    burstplotsframe.grid(row=0, column=0, sticky='nesw')

    burst_frame.grid_columnconfigure(0, weight=1)
    burst_frame.grid_rowconfigure(0, weight=3)

    burstsettingsframe=ttk.Labelframe(master=burst_frame, text='Burst detection settings', style="Custom.TLabelframe")
    burstsettingsframe.grid(row=1, column=0)
    burst_frame.grid_rowconfigure(1, weight=1)

    # Burst detection settings
    minspikes_bw_label=ttk.Label(master=burstsettingsframe, text='Minimal amount of spikes', font=(font,10)).grid(row=0, column=0, pady=10, padx=10, sticky='w')
    minspikes_bw_entry=ttk.Entry(master=burstsettingsframe)
    minspikes_bw_entry.grid(row=0, column=1, pady=10, padx=10, sticky='w')
    def_iv_bw_label=ttk.Label(master=burstsettingsframe, text='Default interval threshold', font=(font,10)).grid(row=1, column=0, pady=10, padx=10, sticky='w')
    def_iv_bw_entry=ttk.Entry(master=burstsettingsframe)
    def_iv_bw_entry.grid(row=1, column=1, pady=10, padx=10, sticky='w')
    max_iv_bw_label=ttk.Label(master=burstsettingsframe, text='Max interval threshold', font=(font,10)).grid(row=2, column=0, pady=10, padx=10, sticky='w')
    max_iv_bw_entry=ttk.Entry(master=burstsettingsframe)
    max_iv_bw_entry.grid(row=2, column=1, pady=10, padx=10, sticky='w')
    kde_bw_bw_label=ttk.Label(master=burstsettingsframe, text='KDE bandwidth', font=(font,10)).grid(row=0, column=2, pady=10, padx=10, sticky='w')
    kde_bw_bw_entry=ttk.Entry(master=burstsettingsframe)
    kde_bw_bw_entry.grid(row=0, column=3, pady=10, padx=10, sticky='w')
    smaller_nb_bw_label=ttk.Label(master=burstsettingsframe, text='Smaller neighbours', font=(font,10)).grid(row=1, column=2, pady=10, padx=10, sticky='w')
    smaller_nb_bw_entry=ttk.Entry(master=burstsettingsframe)
    smaller_nb_bw_entry.grid(row=1, column=3, pady=10, padx=10, sticky='w')

    def update_burst_plot():
        # Get the new parameters from the entry widgets
        temp_parameters=copy.deepcopy(parameters)
        temp_parameters["minimal amount of spikes"]=int(minspikes_bw_entry.get())
        temp_parameters["default interval threshold"]=float(def_iv_bw_entry.get())
        temp_parameters["max interval threshold"]=float(max_iv_bw_entry.get())
        temp_parameters["KDE bandwidth"]=float(kde_bw_bw_entry.get())
        temp_parameters["smaller neighbours"]=int(smaller_nb_bw_entry.get())

        plot_burst_detection(master=burstplotsframe, parameters=temp_parameters, electrode_nr=electrode_nr)

    def default_values_burst():
        # Reset the values to the ones in the JSON file
        minspikes_bw_entry.delete(0,END)
        minspikes_bw_entry.insert(0,parameters["minimal amount of spikes"])
        def_iv_bw_entry.delete(0,END)
        def_iv_bw_entry.insert(0,parameters["default interval threshold"])
        max_iv_bw_entry.delete(0,END)
        max_iv_bw_entry.insert(0,parameters["max interval threshold"])
        kde_bw_bw_entry.delete(0,END)
        kde_bw_bw_entry.insert(0,parameters["KDE bandwidth"])
        smaller_nb_bw_entry.delete(0,END)
        smaller_nb_bw_entry.insert(0,parameters["smaller neighbours"])

    def burst_reset():
        default_values_burst()
        update_burst_plot()

    # Set default values and create initial plot
    burst_reset()

    # Create update and reset buttons
    update_burst_plot_button=ttk.Button(master=burstsettingsframe, text='Update plot', command=update_burst_plot)
    update_burst_plot_button.grid(row=3, column=0, pady=10, padx=10, sticky='nsew', columnspan=2)

    reset_burst_button = ttk.Button(master=burstsettingsframe, text='Reset', command=burst_reset)
    reset_burst_button.grid(row=3, column=2, pady=10, padx=10, sticky='nsew', columnspan=2)

    burstdisclaimerlabel=ttk.Label(master=burstsettingsframe, text='Warning: altering these settings will have no effect on the output of the application,\nor further analysis steps such as network burst detection.\nThese settings are here purely to visualize how these parameters could alter the analysis pipeline', font=(font,10), anchor='e')
    burstdisclaimerlabel.grid(row=0, column=4, pady=10, padx=10, sticky='nsew')


'''

AI analysis

Front-end Lay-out of the choose feature file frame

'''
# Choose feature file frame - Rectangular window which is used to organize a group of complex widgets
choose_feature_file_frame = ttk.Frame(root)

# Button to go to the AI window frame
# The lambda function in the command parameter, ensures a function can be used before the function is defined
choose_feature_file_frame_button = ttk.Button(master=main_frame, text="ML\nAnalysis", style="bigbutton.TButton", command=lambda: go_to_choose_feature_file_frame())
# Grid puts the widgets in a 2-dimensional table. 
# Grid enables you to specify the exact location (row and column) to place the widget in the table.
choose_feature_file_frame_button.grid(row=1, column=1, padx=10, pady=10, sticky='nesw', ipadx=25, ipady=25)


# Container widget where the user can select the filename with all MEA features
select_feature_file = ttk.LabelFrame(master=choose_feature_file_frame, text='Select file with the MEA features', style="Custom.TLabelframe")
select_feature_file.grid(row=0, column=0, padx=10, pady=10, sticky='nesw')

# Button to select the filename with all MEA features
select_feature_file_button = ttk.Button(master=select_feature_file, text="Choose a file", command=lambda: open_feature_file())
select_feature_file_button.grid(row=0, column=0, padx=10, pady=10, sticky='nesw')

# Button to Load the chosen csv file
load_feature_data_button = ttk.Button(master=select_feature_file, text="Load File", command=lambda: load_feature_data())
load_feature_data_button.grid(row=0, column=1, padx=10, pady=10, sticky='nesw')


# Container widget where the user can select the parameters necessary for the AI analysis
preparation_parameters = ttk.LabelFrame(master=choose_feature_file_frame, text='Select data preparation parameters', style="Custom.TLabelframe")
# preparation_parameters.grid(row=2, column=0, padx=10, pady=10, sticky='nesw')
preparation_parameters.pack()

# Entry for the amount of wells in the dataset 
well_amount_label = ttk.Label(master=preparation_parameters, text="Well amount")
well_amount_label.grid(row=0, column=0, padx=10, pady=10, sticky='nesw')
# TODO: Add Tooltip
well_amount_input = ttk.Entry(master=preparation_parameters)
well_amount_input.grid(row=0, column=1, padx=10, pady=10, sticky='nesw')
well_amount_input.insert(0, 12) # Add default parameter

# Entry for the amount of electrodes in each well 
electrode_amount_label = ttk.Label(master=preparation_parameters, text="Electrode amount")
electrode_amount_label.grid(row=1, column=0, padx=10, pady=10, sticky='nesw')
# TODO: Add Tooltip
electrode_amount_input = ttk.Entry(master=preparation_parameters)
electrode_amount_input.grid(row=1, column=1, padx=10, pady=10, sticky='nesw')
electrode_amount_input.insert(0, 12)

# Split dataset 
# To be deleted later
data_magnification_label = ttk.Label(master=preparation_parameters, text="Dataset magnified by")
data_magnification_label.grid(row=2, column=0, padx=10, pady=10, sticky='nesw')
data_magnification_tooltip = Tooltip(data_magnification_label, 'An Machine Learning model needs a lot of data to make accurate predictions. \nSome datasets are very small and therefore cannot yet be trained into a decent ML model. \nIn these scenarios, the choice is made to split the wells in the feature dataset into multiple data points. \nThis causes the features in the feature dataset to be calculated over a portion of the measurement of a well rather than the entire measurement of a well. \n\nThis Entry asks for the magnification size. \nFor unedited datasets, the magnification size is “1x”')
data_magnification_label.bind("<Enter>", data_magnification_tooltip.show_tooltip)
data_magnification_label.bind("<Leave>", data_magnification_tooltip.hide_tooltip)
data_magnification_input = ttk.Entry(master=preparation_parameters)
data_magnification_input.grid(row=2, column=1, padx=10, pady=10, sticky='nesw')
data_magnification_input.insert(0, 30)

# Button to label all wells in the data
go_to_label_frame_button = ttk.Button(master=choose_feature_file_frame, text="Label data", style="bigbutton.TButton", command=lambda: go_to_label_frame()) 
go_to_label_frame_button.grid(row=4, column=0, padx=10, pady=(30, 10), ipadx=20, ipady=18, sticky='nesw')


# Container widget to navigate back through the GUI
go_back_buttons = tk.LabelFrame(master=choose_feature_file_frame, bd=0) # bd=0 Removes border of container widget
go_back_buttons.grid(row=0, column=1, padx=(40, 10), pady=(26, 10), sticky='nesw')

# Button to go to the main frame window
main_frame_button = ttk.Button(master=go_back_buttons, text="Go to the main menu", command=lambda: go_to_main_frame())
main_frame_button.grid(row=0, column=1, pady=(0, 15), sticky='new')

# Button to show / hide parameter options
parameter_options = ttk.Button(master=go_back_buttons, text="Parameter options", command=lambda: show_parameter_options())
parameter_options.grid(row=1, column=1, sticky='new')


# Show or hide parameter options for the data preperation part
def show_parameter_options():
    preparation_parameters.pack_forget()
    well_amount_label.pack_forget()
    electrode_amount_label.pack_forget()
    data_magnification_label.pack_forget()

'''
Back-end - Functions for all buttons in the choose feature file frame
'''
# Define global empty variable for error checks
global feature_filename
global raw_df
global is_model_trained
feature_filename = ""
raw_df = pd.DataFrame()
is_model_trained = False


# Set up the window frame where the user can analyse the data with AI scripts
def go_to_choose_feature_file_frame():
    # Forget all ML analysis packs
    forget_packs()
    choose_feature_file_frame.pack(fill='both', expand=True) # Pack places block of the choose feature file frame widget

# Forget all frame packs from the ML analysis
def forget_packs():
    choose_feature_file_frame.pack_forget()
    feature_selection_frame.pack_forget()
    model_selection_frame.pack_forget()
    preparation_frame.pack_forget()
    ai_results_frame.pack_forget()
    label_frame.pack_forget()
    main_frame.pack_forget()

# Go back to the main frame window
def go_to_main_frame():
    # Forget all ML analysis packs
    forget_packs()
    parameterframe.pack_forget() # Pack_forget removes block of the main frame widget
    main_frame.pack(fill='both', expand=True) # Pack places block of the choose feature file frame widget


# Choose feature file from the file directory
def open_feature_file():
    # Redefine feature filename variable
    global feature_filename 

    # Open file dialog with text to open features.csv file
    selected_feature_file = filedialog.askopenfilename(filetypes=[("MEA feature data", "*.csv"), ("All file types", "*.*")])
    # Get filename of selected file
    if len(selected_feature_file)!=0:
        feature_filename=selected_feature_file
        selected_feature_file=os.path.split(feature_filename)[1]
        select_feature_file_button.configure(text=selected_feature_file)

# Load the Pandas DataFrame
def load_feature_data():
    # Check if a file is selected
    if feature_filename == "":
        messagebox.showwarning(title="Select a file first", message="No file selected. Please select a MEA features file with the 'Choose a file' button near this button.")
        return None
    else:
        global raw_df
        # Read the selected file as DataFrame
        try:
            csv_filename = r"{}".format(feature_filename)
            raw_df = pd.read_csv(csv_filename, sep=',')
        # Raise an error if the chosen file could not be read
        except ValueError:
            messagebox.showerror(title="Error", message="The file you have chosen is invalid!")
            return None
        # Raise a warning if the selected file could not been found
        except FileNotFoundError:
            messagebox.showwarning(title="Error  (How did you even do this?)", message=f"The following file does not exist on your computer: {feature_filename}")
            return None

# Set up the window where the user can label all wells
def go_to_label_frame():
    # Check if model can be trained
    if raw_df.empty:
        messagebox.showinfo(title="Load a MEA features file", message="Please select a MEA features .csv file first, before training the model.")
        return
    
    # Define global variables for all data preparation parameters
    global well_amount
    global electrode_amount
    global data_magnification
    
    try:
        # Get all data preparation parameters to use them for the CureQ library functions
        well_amount = int(well_amount_input.get())
        electrode_amount = int(electrode_amount_input.get())
        data_magnification = int(data_magnification_input.get())
        
    # Check if all parameters have a correct datatype value
    except Exception as error:
        messagebox.showinfo(title='Please check your data preparation parameters', message='Certain parameters could not be converted to the correct datatype (e.g. int or float). Please check if every parameter has the correct values')
        return

    # Check if the entered well amount is correct
    if len(raw_df) / data_magnification != well_amount:
        messagebox.showwarning(title='Unmatched paramaters', message='Number of wells does not match number of rows in the dataset. \nCheck if all 3 entered data preparation parameters are correct.')
        return

    # Create all well buttons in a lay-out corresponding to the physical MEA plate
    global well_buttons
    well_buttons = create_well_buttons_label_frame(well_layout, well_amount, assign_label_to_well)

    # Forget all ML analysis packs
    forget_packs()
    # Open label frame
    label_frame.pack(fill='both', expand=True) # Pack places block of the choose feature file frame widget
    

'''
Front-end lay-out of the data labelling frame
'''
# Data labelling frame - Rectangular window which is used to organize a group of complex widgets
label_frame = ttk.Frame(root)

# Layout with all well buttons
well_layout = ttk.LabelFrame(master=label_frame, text='Assign labels to wells', style="Custom.TLabelframe")
well_layout.grid(column=0, row=0, sticky='nw', padx=20, pady=10)


'''Frames to assign labels to the wells'''
# Frame for all buttons
button_frame = ttk.Frame(master=label_frame)
button_frame.grid(row=1, column=0, sticky="ew", pady=5, padx=(5, 0))

# Clear button
clear_button = ttk.Button(button_frame, text="Clear all assigned labels", command=lambda: clear_selection())
clear_button.grid(row=0, column=0, sticky="w")

# Frame for group manager (inside the button frame)
group_manager_frame = ttk.Frame(master=button_frame)
group_manager_frame.grid(row=0, column=1, sticky="ew")

# Button to add groups
add_group_button = ttk.Button(group_manager_frame, text="Add label:", command=lambda: add_group())
add_group_button.grid(row=0, column=1, sticky="w", padx=5)

# Enter the labels to assign to the groups
add_group_entry = ttk.Entry(group_manager_frame)
add_group_entry.grid(row=0, column=2, sticky="w", padx=(0, 0))

# Style to color the buttons with the tag
style = ttk.Style()

# Frame for groups
group_frame = ttk.Frame(master=label_frame)
group_frame.grid(row=2, column=0, sticky="ew")


'''Navigate through the GUI'''
# Button to preprocess the dataset in order to give it to a ML model
preprocess_data_button = ttk.Button(master=label_frame, text="Default preprocessing", style="bigbutton.TButton", command=lambda: preprocess_data()) 
preprocess_data_button.grid(row=3, column=0, padx=(10, 0), pady=(25, 10), ipadx=20, ipady=20, sticky='nesw')

# Container widget to navigate back through the GUI
go_back_buttons = tk.LabelFrame(master=label_frame, bd=0) # bd=0 Removes border of container widget
go_back_buttons.grid(row=0, column=1, padx=(40, 10), pady=(26, 10), sticky='nesw')

# Button to go back to the choose feature file frame window
back_to_choose_feature_file_frame_button = ttk.Button(master=go_back_buttons, text="Previous window", command=lambda: go_to_choose_feature_file_frame())
back_to_choose_feature_file_frame_button.grid(row=0, column=0, pady=(0, 15), sticky='new')

# Button to go to the main frame window
main_frame_button_3 = ttk.Button(master=go_back_buttons, text="Main menu", command=lambda: go_to_main_frame())
main_frame_button_3.grid(row=1, column=0, sticky='new')


'''
Back-end - Functions to label the dataset
'''
label_well_dictionary = {}  # Dictionary to store assigned wells
current_label = None        # Variable to store selected well
groups, buttons = [], []    # List of groups with well labels and buttons with label tags

# Background colors for all groups
'''         Vivid Red    Vivid Blue    Vivid Pink    Vivid Cyan    Vivid Yellow    Blue Violet    Orange Red    Lime Green    Dark Violet    Vivid Green'''
colors = [  "#FF5733",   "#3357FF",    "#FF33A6",    "#33FFF0",    "#FFD700",      "#8A2BE2",     "#FF4500",    "#32CD32",    "#9400D3",     "#33FF57"  ]


# Create well buttons for in the label frame
def create_well_buttons_label_frame(master, wells, button_command):
    # Create an optimal grid of wells
    y_wells, x_wells = calculate_optimal_grid(wells)
    well_buttons, well_number = [], 1

    # Loop through all wells
    for y in range(y_wells):
        for x in range(x_wells):
            # Create an empty style for every well button
            style_name = "Custom_well_{0}.TButton".format(well_number)
            style.configure(style_name, font=(font, 15))

            # Create well buttons on a specific grid location
            well_button = ttk.Button(master=master, text=well_number, style=style_name)
            # Assign a label to a well and change the button color when button is pressed
            well_button.config(command=partial(button_command, well_number, well_button))
            well_button.grid(row=y, column=x, sticky='nesw', ipadx=25, ipady=25)
            well_buttons.append(well_button)
            well_number += 1
    return well_buttons


# Set the current label tag of a group wells
def set_label(label):
    # Current label tag is now globally recognized
    global current_label
    current_label = str(label)
    print(f"Current label selected: {current_label}")

# Dynamically create all buttons with label tags 
def update_label_buttons():
    # Remove label buttons
    for button in buttons:
        button.destroy()

    # Create all label buttons
    for label_idx, label in enumerate(groups):

        # Create an unique (color) style for every label button
        style_name = f"Custom{label_idx}.TButton"
        style = ttk.Style()
        style.configure(style_name, foreground=colors[label_idx])

        # Create button with wanted tag and assign a color to the button
        button = ttk.Button(group_frame, text=label, command=partial(set_label, str(label)), style=style_name)
        button.grid(row=0, padx=(5, 0), column=label_idx, sticky="w")
        buttons.append(button)

# Assigns selected label (current_label) to pressed well button
def assign_label_to_well(well, well_button):
    global current_label, label_well_dictionary

    # Checks if a label is selected
    if current_label is not None:
        print("Assigning label '{0}' to well '{1}'".format(current_label, well))

        # Add label name as a key to the label_well_dictionary dictionary
        if current_label not in label_well_dictionary:
            label_well_dictionary[current_label] = []
        # Add well number as a value to the assigned label name key
        if not any(well in sublist for lists in label_well_dictionary.values() for sublist in lists):
            label_well_dictionary[current_label].append([well])

            # Get the label index of the selected label
            label_idx = groups.index(current_label)
            # Change the color for a clicked well button with the right label color
            style_name = "Custom_well_{0}.TButton".format(well)
            style.configure(style_name, foreground=colors[label_idx], font=(font, 15))
            well_button.configure(style=style_name)
        else: 
            # Iterate over each key in the dictionary
            for label in label_well_dictionary:
                # Remove well number from dictionary if clicked well button already is assigned
                label_well_dictionary[label] = [well_number for well_number in label_well_dictionary[label] if well_number != [well]]
            # Change the foreground color of the button back to normal
            well_button.configure(style="wellbutton.TButton")
    else:
        # No label is selected
        messagebox.showinfo(title="Select a label", message="No label selected. Please add and select a label first.")

# Clear all assigned labels
def clear_selection():
    # Iterate over each key in the dictionary
    for label in label_well_dictionary:
        # Remove all assigned wells from dictionary
        label_well_dictionary[label] = []    
    global well_buttons
    # Iterate over all well buttons
    for well_button in well_buttons:
        # Change the foreground color of the button back to normal
        well_button.configure(style="wellbutton.TButton")


# Add a group entered in the Entry field
def add_group():
    # Get the entry text
    new_group = str(add_group_entry.get())
    # Add the group to list of groups
    if new_group != "" and new_group not in groups and len(groups) < 10:
        groups.append(new_group)

    # Update buttons with label tags
    update_label_buttons()


# Set up the window where the user can select the AI parameters and train an AI model
def preprocess_data():
    # Get all well ID's
    global label_well_dictionary
    print("\nDictionary with labels and their assigned wells:")
    print(label_well_dictionary)

    # Count amount of assigned wells
    assigned_label_amount = sum([len(label_well_dictionary[label]) for label in label_well_dictionary if isinstance(label_well_dictionary[label], list)])

    # Check if the user does not have assigned the first label
    if assigned_label_amount == 0:
        messagebox.showinfo(title="Assign labels", message="Please assign the belonging label to each individual well.\n\nIn order to do this, first create the desired labels with the 'Add label:' button, then you can assign a label to each well by clicking at the newly created label and then clicking on the wells belonging to that label.")
        return
    # Check if the user has assigned all wels
    elif assigned_label_amount != well_amount:
        messagebox.showinfo(title="Assign all labels", message="Please assign the belonging label to every well.")
        return
    # Only continue if all wells do have an assigned label

    # Prepare data with the preparation parameters
    data_preparation()

    # TODO Download df

    # Button to go to ML model selection frame
    go_to_choose_model_frame_button = ttk.Button(master=label_frame, text="Choose ML model", style="bigbutton.TButton", command=lambda: go_to_choose_model_frame())
    go_to_choose_model_frame_button.grid(row=4, column=0, padx=(10, 0), pady=(5, 10), ipadx=20, ipady=20, sticky="nesw")
    

# Set up the window where the user can choose a ML model
def go_to_choose_model_frame():
    # Forget all ML analysis packs
    forget_packs()
    # Go to model selection frame
    model_selection_frame.pack(fill='both', expand=True)


'''
Front-end lay-out of the data preparation frame
'''
# Model selection frame - Rectangular window which is used to organize a group of complex widgets
model_selection_frame = ttk.Frame(root)

# Container widget where the user can select the ML model that he wants to train
select_ml_model = ttk.LabelFrame(master=model_selection_frame, text='Select Machine Learning model', style="Custom.TLabelframe")
select_ml_model.grid(row=0, column=0, padx=10, pady=10, sticky='nesw')

# Button to select the Random Forest Classifier
select_rfc = ttk.Button(master=select_ml_model, text="Random Forest Classifier (RFC)", style="wellbutton.TButton", command=lambda: select_rfc_model())
select_rfc.grid(row=0, column=0, padx=10, pady=(25, 5), ipadx=10, ipady=10, sticky='nesw')

# Button to select the Gradient Boosting Classifier
select_gbc = ttk.Button(master=select_ml_model, text="Gradient Boosting Classifier (GBC)", style="wellbutton.TButton", command=lambda: select_gbc_model())
select_gbc.grid(row=1, column=0, padx=10, pady=10, ipadx=10, ipady=10, sticky='nesw')


# Container widget to navigate back through the GUI
go_back_buttons_choose_model = tk.LabelFrame(master=model_selection_frame, bd=0) # bd=0 Removes border of container widget
go_back_buttons_choose_model.grid(row=0, column=1, padx=(40, 10), pady=(26, 10), sticky='nesw')

# Button to go back to the label frame window
back_to_label_frame_button = ttk.Button(master=go_back_buttons_choose_model, text="Previous window", command=lambda: go_to_label_frame())
back_to_label_frame_button.grid(row=0, column=0, pady=(0, 15), sticky='new')

# Button to go to the main frame window
main_frame_button_4 = ttk.Button(master=go_back_buttons_choose_model, text="Main menu", command=lambda: go_to_main_frame())
main_frame_button_4.grid(row=1, column=0, sticky='new')


'''
Back-end - Functions to label the dataset
'''
# Select the Random Forest Classifier as the global ML model
def select_rfc_model():
    from sklearn.ensemble import RandomForestClassifier
    global ml_model
    ml_model = RandomForestClassifier()

    # Go to the preparation frame
    go_to_preparation_frame()

# Select the Gradient Boosting Classifier as the global ML model
def select_gbc_model():
    from sklearn.ensemble import GradientBoostingClassifier
    global ml_model
    ml_model = GradientBoostingClassifier()

    # Go to the preparation frame
    go_to_preparation_frame()

# Set up the window where the user can select the AI parameters and train an AI model
def go_to_preparation_frame():
    # Forget all ML analysis packs
    forget_packs()
    # Go to preparation frame
    preparation_frame.pack(fill='both', expand=True)


'''
Front-end lay-out of the data preparation frame
'''
# Data preparation frame - Rectangular window which is used to organize a group of complex widgets
preparation_frame = ttk.Frame(root)

# # Row and column count widget of prepared treeview
# row_column_count_prepped_df_frame = ttk.Label(master=preparation_frame.interior, text="row x columns")
# row_column_count_prepped_df_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nesw')

''' AI parameters'''

# Container widget where the user can select the parameters necessary for the AI analysis
select_ai_parameters = ttk.LabelFrame(master=preparation_frame, text='Select Machine Learning parameters', style="Custom.TLabelframe")
select_ai_parameters.grid(row=0, column=0, padx=10, pady=10, sticky='nesw')

# Entries for all AI parameters 
# Entry for the train percentage for training the AI model
train_percentage_label = ttk.Label(master=select_ai_parameters, text="Train percentage")
train_percentage_label.grid(row=0, column=0, padx=10, pady=10, sticky='nesw')
train_percentage_tooltip = Tooltip(train_percentage_label, 'Value of the train percentage should be between 1% and 99%\nThe default value for the train size is 70%')
train_percentage_label.bind("<Enter>", train_percentage_tooltip.show_tooltip)
train_percentage_label.bind("<Leave>", train_percentage_tooltip.hide_tooltip)
train_percentage_input = ttk.Entry(master=select_ai_parameters)
train_percentage_input.grid(row=0, column=1, padx=10, pady=10, sticky='nesw')


# Container widget to train the AI model and view the results
train_model_navigation_buttons = ttk.LabelFrame(master=preparation_frame, text="Train Machine Learning model on", style="Custom.TLabelframe")
train_model_navigation_buttons.grid(row=1, column=0, padx=10, pady=10, sticky='nesw')

# Button to train the AI model with the chosen features file and the chosen parameters
train_model_all_features_button = ttk.Button(master=train_model_navigation_buttons, text="all features", style="wellbutton.TButton", command=lambda: train_model_check()) # TODO: Really train the AI model
train_model_all_features_button.grid(row=0, column=0, padx=10, pady=10, ipadx=10, ipady=8, sticky='nesw')

# Button to train the AI model with the chosen features file and the chosen parameters
train_model_independent_features_button = ttk.Button(master=train_model_navigation_buttons, text="independent features", style="wellbutton.TButton", command=lambda: train_model_check()) # TODO: Really train the AI model
train_model_independent_features_button.grid(row=1, column=0, padx=10, pady=2, ipadx=10, ipady=8, sticky='nesw')

# Button to train the AI model with the chosen features file and the chosen parameters
train_model_user_defined_features_button = ttk.Button(master=train_model_navigation_buttons, text="user-defined features", style="wellbutton.TButton", command=lambda: go_to_feature_selection()) # TODO: Really train the AI model
train_model_user_defined_features_button.grid(row=2, column=0, padx=10, pady=10, ipadx=10, ipady=8, sticky='nesw')

# # Button to view the results and all visualtion possibilities of the AI model
# view_ai_results_button = ttk.Button(master=train_model_navigation_buttons, text="View results", style="wellbutton.TButton", command=lambda: go_to_ai_results_frame()) # TODO: Add AI results frame and go to this frame
# view_ai_results_button.grid(row=3, column=1, padx=10, pady=10, ipadx=25, ipady=25, sticky='nesw')

# # Button to compute a correlation matrix and select some features
# cm_button = ttk.Button(master=train_model_navigation_buttons, text="Correlation matrix", style="wellbutton.TButton", command=lambda: go_to_feature_selection()) # TODO: Function to Build Your Own code
# cm_button.grid(row=4, column=0, padx=10, pady=10, ipadx=25, ipady=25, sticky='nesw')

# # Button to download the prepared and cleaned dataframe
# download_df_button = ttk.Button(master=train_model_navigation_buttons, text="Download DataFrame", style="wellbutton.TButton", command=lambda: download_df()) # TODO: Really train the AI model
# download_df_button.grid(row=4, column=1, padx=10, pady=10, ipadx=25, ipady=25, sticky='nesw')

# # Button to build your own script to analyse an AI model
# byo_button = ttk.Button(master=train_model_navigation_buttons, text="Write Your Own code!", style="bigbutton.TButton", command=lambda: write_your_own_code()) # TODO: Function to Build Your Own code
# byo_button.grid(row=1, column=2, padx=10, pady=10, ipadx=25, ipady=25, sticky='nesw')

# Container widget to navigate back through the GUI
go_back_buttons_prep = tk.LabelFrame(master=preparation_frame, bd=0) # bd=0 Removes border of container widget
go_back_buttons_prep.grid(row=0, column=1, padx=(40, 10), pady=(26, 10), sticky='nesw')

# Button to go back to the label frame window
back_to_model_selection_frame_button = ttk.Button(master=go_back_buttons_prep, text="Previous window", command=lambda: go_to_choose_model_frame())
back_to_model_selection_frame_button.grid(row=0, column=0, pady=(0, 15), sticky='new')

# Button to go to the main frame window
main_frame_button_6 = ttk.Button(master=go_back_buttons_prep, text="Main menu", command=lambda: go_to_main_frame())
main_frame_button_6.grid(row=1, column=0, sticky='new')

# Button to go to the main frame window from the parameters frame
main_frame_button_1 = ttk.Button(master=parameterframe.interior, text="Go back to the main menu and don't save parameters", command=lambda: go_to_main_frame())
main_frame_button_1.grid(row=4, column=0, padx=10, pady=(0, 20), ipadx=25, ipady=25, sticky='nesw', columnspan=3)


'''
Back-end - Functions for the Machine Learning training process
'''
# Define global empty variable for error checks
global prepped_df
global delete_axis
prepped_df = pd.DataFrame
delete_axis = 1

# TODO: Function needs to be implemented in the CureQ library
# Prepare the dataset before training an AI model
def data_preparation():
    global selected_x_train_set
    selected_x_train_set = [] # Reset array of selected columns with each update

    # Copy the raw DataFrame as the prepped DataFrame (Changes do not reflect on copied df)
    global prepped_df
    prepped_df = raw_df.copy()

    # Calculate well number
    prepped_df["Index"] = prepped_df["Well"]
    prepped_df["Well"] = prepped_df["Well"]/data_magnification+0.49
    prepped_df["Well"] = prepped_df["Well"].round().astype(int)
    # # All value counts should be equal to the inserted data magnification
    # print(prepped_df["Well"].value_counts())

    # Delete inactive electrodes
    minimum_active_electrodes = 2 / electrode_amount
    prepped_df = prepped_df[prepped_df["Active_electrodes"] > minimum_active_electrodes]

    # Delete incorrect columns if exists
    incorrect_columns = ["Unnamed: 0"]
    prepped_df = prepped_df.drop(columns=incorrect_columns, errors="ignore")

    # Handle NaN and infinte values
    count_nan = prepped_df.isna().any()[lambda x: x].values.sum()
    # print("The dataframe contains " + str(count_nan) + " NaN values")

    count_inf = np.isinf(prepped_df).values.sum()
    # print("The dataframe contains " + str(count_inf) + " infinite values") 

    prepped_df.replace([np.inf, -np.inf], np.nan, inplace=True) # Replace infinte values with NaN values
    prepped_df = prepped_df.dropna(axis=delete_axis) # Delete all NaN values

    # Add the assigned labels to the dataframe
    add_labels()


# Add labels to the dataframe
def add_labels():
    # Declare variables as global in order to use it in other function
    global label_well_dictionary
    global prepped_df

    # Convert dictionary to df
    dictionary_to_df = []
    # Dictionary with individual wells and labels
    for label, wells in label_well_dictionary.items():
        for well in wells:
            dictionary_to_df.append({"Well": well[0], "Label": label})

    # Dictionary of labels to be converted to df
    label_df = pd.DataFrame(dictionary_to_df)

    # Ensure well columns are the same type
    label_df["Well"] = label_df["Well"].astype(int)
    prepped_df["Well"] = prepped_df["Well"].astype(int)
    
    # Append df of labels to features dataframe
    prepped_df = prepped_df.merge(label_df, on="Well", how="left")


# Count the amount of rows and columns in the prepped dataframe
def row_column_count_prepped_df():
    # Count the rows and columns
    prepped_rows = len(prepped_df)
    prepped_columns = len(prepped_df.columns)
    prepped_amount = "{0} rows x {1} columns".format(prepped_rows, prepped_columns)

    # Show the row x column amounts in the widget
    row_column_count_prepped_df_frame["text"] = prepped_amount


# Check if model can be trained and train model
def train_model_check():
    # Define global variables for all data preparation parameters TODO
    global train_percentage
    
    try:
        # Get all parameters to train the ML model
        train_percentage = float(train_percentage_input.get())
        
        # Check if the train percentage has a valid number
        if train_percentage <= 0 or train_percentage >= 100:
            messagebox.showinfo(title='Invalid train percentage', message="The entered train percentage is invalid. Please choose a percentage between the values 0 and 100.")
            return
        # Convert train percentage to acceptable train size in train test split
        train_percentage /= 100
        
    # Check if all parameters have a correct datatype value
    except Exception as error:
        print(error)
        messagebox.showinfo(title='Please check your ML preparation parameters', message='Certain parameters could not be converted to the correct datatype (e.g. int or float). Please check if every parameter has the correct values')
    if train_percentage <= 0 or train_percentage >= 100:
        return

   # Allows to go to the AI results tab
    global is_model_trained
    is_model_trained = True

    # CureQ function to train model
    train_model()

    # Go to the frame with all results
    go_to_ai_results_frame()


# TODO: Function needs to be implemented in the CureQ library
# AI analysis function from CureQ library which analyses the chosen features file.  # TODO: Really train the AI model
def train_model():
    # Declare variables as global in order to use it in other function
    global train_percentage
    global prepped_df
    global selected_x_train_set
    global ml_model
    global X

    # Check whether list is empty
    if not selected_x_train_set:
        # Drop all non-feature columns
        X = prepped_df.drop(["Well", "Label", "Active_electrodes", "Index"], axis=1) # Extracted features
    else:
        # Only use the selected columns as features to train the model on
        X = prepped_df[selected_x_train_set]
    # Labels # control_wells = np.array([1, 2, 4, 7, 8, 10]) kleefstra_wells = np.array([3, 5, 6, 9, 11, 12])
    y = prepped_df["Label"]

    from sklearn.model_selection import train_test_split
    # Split the data in a train and test dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=train_percentage, stratify=y)

    from sklearn import metrics
    # Train chosen Machine Learning model
    ml_model = ml_model.fit(X_train, y_train)
    y_pred = ml_model.predict(X_test)

    # Test ML model and show accuracy
    accuracy = metrics.accuracy_score(y_test, y_pred)*100
    print("Accuracy of {}: {:.2f}% {}".format(ml_model, accuracy, type(ml_model)))
    if ml_model == "RandomForestClassifier()":
        messagebox.showinfo(title='RFC accuracy', message='Accuracy of Random Forest Classifier trained on chosen features: {:.2f}'.format(accuracy))
    else:
        messagebox.showinfo(title='GBC accuracy', message='Accuracy of Gradient Boosting Classifier trained on chosen features: {:.2f}'.format(accuracy))


# Set up the window frame where the user can view all results of the trained AI model
def go_to_ai_results_frame():
    # Check whether a model is already trained
    if is_model_trained == False:
        messagebox.showinfo(title="Information", message="Please train a model first.")
        return

    # Forget all ML analysis packs
    forget_packs()
    # Go to results frame
    ai_results_frame.pack(fill='both', expand=True) # .Pack places block of the AI results frame widget


# Download the prepared and cleaned DataFrame
def download_df():
    # Declare variables as global in order to use it in other function
    global prepped_df
    global feature_filename

    # Get the input directory, and save the cleaned dataframe to this directory
    df_directory = os.path.dirname(feature_filename)
    df_filename = os.path.basename(feature_filename)
    df_filename = os.path.splitext(df_filename)[0]
    save_df = "{0}/{1}_cleaned.csv".format(df_directory, df_filename)

    # Save the prepped dataframe in the input folder
    prepped_df.to_csv(save_df, index=False)


# Function to write your own Python analysis script
def write_your_own_code():
    messagebox.showinfo(title="Coming Soon...", message="This feature is not published yet.")


'''
Front-end layout of the feature selection procedure
'''
# Feature_selection_frame - Rectangular window which is used to organize a group of complex widgets
feature_selection_frame = VerticalScrolledFrame(root)
   

# Button to view the results and all visualtion possibilities of the AI model
back_to_prep_frame_button = ttk.Button(master=feature_selection_frame.interior, text="Previous window", command=lambda: go_to_preparation_frame()) 
back_to_prep_frame_button.grid(row=1, column=0, padx=20, pady=10, ipadx=25, ipady=25, sticky='nesw')

# Button to go to the main frame window from the parameters frame
main_frame_button_5 = ttk.Button(master=feature_selection_frame.interior, text="Go to the main menu", command=lambda: go_to_main_frame())
main_frame_button_5.grid(row=2, column=0, padx=20, pady=10, ipadx=25, ipady=25, sticky='nesw')


'''
Back-end - Functions to select the required features and show the correlation matrix
'''
# Go to feature selection and show correlation matrix
def go_to_feature_selection():
    # Forget all ML analysis packs
    forget_packs()
    # Go to feature selection frame
    feature_selection_frame.pack(fill='both', expand=True) # .Pack places block of the AI results frame widget

    # Embed correlation matrix in GUI
    embed_correlation_matrix()

    # Select all columns for the X train set 
    select_features()


# Embed a correlation matrix in GUI
def embed_correlation_matrix():
    # Declare variables as global in order to use it in other function
    global X

    # Check whether a model is already trained
    if is_model_trained == False:
        # Drop all non-feature columns
        X = prepped_df.drop(["Well", "Label", "Active_electrodes", "Index"], axis=1) # Extracted features
    
    # Round all correlation values on 2 decimals
    correlation_df = round(X.corr(), 2)

    # Figure that will contain the correlation matrix
    correlation_figure = Figure(figsize=(10, 8))
    correlation_subplot = correlation_figure.add_subplot(1, 1, 1)  # Add subplot (nrows, ncols, index)
    # Seaborn heatmap for visualizing the correlation matrix of all features
    correlation_matrix = sns.heatmap(correlation_df, vmin=-1, vmax=1, center=0, cmap=sns.diverging_palette(50, 500, n=500), square=True, ax=correlation_subplot) # Add heatmap to Matplotlib axes
    correlation_matrix.set_title("Correlation matrix of all MEA features") # Set title of subplot figure
    correlation_matrix.figure.tight_layout() # Show all feature columns

    # Creating the TKinter canvas containing the correlation matrix
    correlation_canvas = FigureCanvasTkAgg(correlation_figure, master=feature_selection_frame.interior)
    correlation_canvas.draw()  # Draw the correlation matrix
    correlation_canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)  # Place the canvas on the Tkinter window


# Create buttons to select all features for the X train set
def select_features():
    # Loop through all columns of the Treeview headings
    for idx, column in enumerate(X.columns):  
        # Create a checkbox near each column header
        column_checkbutton = ttk.Checkbutton(master=feature_selection_frame.interior, text=column, command=lambda selected_column=column: toggle_column_selection(selected_column))
        column_checkbutton.grid(sticky="w", row=idx+3)


# Select/deselect column names
def toggle_column_selection(selected_column):
    global selected_x_train_set
    # Delete column name if column already is selected
    if selected_column in selected_x_train_set:
        selected_x_train_set.remove(selected_column)
    # Append column name
    else:
        selected_x_train_set.append(selected_column)

    print("\nFeatures for the X train set:")
    print(selected_x_train_set)


'''
Front-end lay-out of the AI results frame
'''
# Results frame - Rectangular window which is used to organize a group of complex widgets
ai_results_frame = ttk.Frame(root)


# Container widget where the user can view the results of the just trained AI model
visualization_options = ttk.LabelFrame(master=ai_results_frame, text='Visualization options', style="Custom.TLabelframe")
visualization_options.grid(row=0, column=0, padx=10, pady=10, sticky='nesw')

# Button to show a bar plot which shows the feature importance of each feature
feature_importance_button = ttk.Button(master=visualization_options, text="Feature Importances", command=lambda: feature_importances())
feature_importance_button.grid(row=0, column=0, padx=10, pady=10, sticky='nesw')

# Button to show a confusion matrix between with the disease/control ratio
cm_button = ttk.Button(master=visualization_options, text="Confusion Matrix", command=lambda: confusion_matrices())
cm_button.grid(row=1, column=0, padx=10, pady=10, sticky='nesw')

# Button to show a bar plot with the amount of network bursts per well
network_bursts_button = ttk.Button(master=visualization_options, text="Network Bursts", command=lambda: network_bursts())
network_bursts_button.grid(row=2, column=0, padx=10, pady=10, sticky='nesw')

# Button to show a bar plot which shows the accuracy score of each feature
acc_button = ttk.Button(master=visualization_options, text="Performance metrics", command=lambda: performance_metrics())
acc_button.grid(row=3, column=0, padx=10, pady=10, sticky='nesw')

# Button to show the correlation matrix of all MEA features
corr_button = ttk.Button(master=visualization_options, text="Correlation Matrix", command=lambda: get_correlation_matrix())
corr_button.grid(row=4, column=0, padx=10, pady=10, sticky='nesw')
   

# Button to go to the main frame window from the parameters frame
main_frame_button_2 = ttk.Button(master=ai_results_frame, text="Go to the main menu", command=lambda: go_to_main_frame())
main_frame_button_2.grid(row=1, column=0, padx=10, pady=(0, 20), ipadx=25, ipady=25, sticky='nesw')

# Button to view the results and all visualtion possibilities of the AI model
back_to_preparation_frame_button = ttk.Button(master=ai_results_frame, text="Previous window", command=lambda: go_to_preparation_frame()) 
back_to_preparation_frame_button.grid(row=2, column=0, padx=10, pady=10, ipadx=25, ipady=25, sticky='nesw')


'''
Back-end - Functions for all AI results
'''
# Function to write your own Python analysis script
def feature_importances():
    # Calculate feature importances
    feature_importance = ml_model.feature_importances_
    # Calculate Standard deviation
    std = np.std([tree.feature_importances_ for tree in ml_model.estimators_], axis=0)
    # Get feature names
    feature_names = X.columns
    # Get all features and their importances in a nice overview
    forest_importances = pd.Series(feature_importance, index=feature_names)
    
    # Plot all feature importances
    fig, ax = plt.subplots()
    forest_importances.plot.bar(yerr=std, ax=ax)
    ax.set_title("Feature importances using MDI") # Mean Decrease in Impurity
    ax.set_ylabel("Mean Decrease in Impurity")
    fig.tight_layout()
    plt.show()


# Compute a correlation matrix and select features
def get_correlation_matrix():
    # Declare variables as global in order to use it in other function
    global X

    # Round all correlation values on 2 decimals
    correlation_df = round(X.corr(), 2)

    # Seaborn heatmap for visualizing the correlation matrix of all features
    plt.figure(figsize=(12, 8))
    correlation_matrix = sns.heatmap(correlation_df, vmin=-1, vmax=1, center=0, cmap=sns.diverging_palette(50, 500, n=500), square=True)
    correlation_matrix.figure.tight_layout()
    plt.show()


# Function to write your own Python analysis script
def network_bursts():
    messagebox.showinfo(title="Coming Soon...", message="This feature is not published yet.")

# Function to write your own Python analysis script
def confusion_matrices():
    messagebox.showinfo(title="Coming Soon...", message="This feature is not published yet.")

# Function to write your own Python analysis script
def performance_metrics():
    messagebox.showinfo(title="Coming Soon...", message="This feature is not published yet.")


'''
Back-end - AI Code for the data preparation  for in the CureQ library!
'''
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np




# # Load the specified feature file in a DataFrame
# def load_df():
#     df = 


# # Shows a bar plot with the amount of network bursts per well
# def get_network_bursts():
# # Shows a confusion matrix between with the disease/control ratio
# def get_cm():
# # Shows a bar plot which shows the feature importance of each feature
# def get_feature_importance():
# # Shows the DataFrame in a specified format
# def get_df():
# # Shows a bar plot which shows the accuracy score of each feature
# def get acc():
# # Shows the correlation matrix of all MEA features
# def get_corr()
# Button with Write your own code!

'''
'''

# Destroy GUI
def on_closing():
        root.destroy()

# Start GUI
if __name__ == "__main__":
    multiprocessing.freeze_support()
    #root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    #root.destroy()