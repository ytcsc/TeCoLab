'''
Copyright 2025 Leonardo Cabral

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import os
import sys
import time
import glob
import math
import threading
import subprocess
import numpy as np
import pandas as pd
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import filedialog
from Modules.tecolab_enums import CSVColumns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def run_tecolab():
	global tecolab_process
	arg = [sys.executable, "tecolab.py", selected_experiment_file.get(), selected_controller_file.get()]
	try:
		tecolab_process = subprocess.Popen(arg)
	except Exception as e:
		print(f"Error running TeCoLab: {e}")

def start_experiment():
	if not selected_experiment_file.get():
		print("No experiment file selected.")
	elif not selected_controller_file.get():
		print("No controller file selected.")
	else:
		thread = threading.Thread(target = run_tecolab)
		thread.daemon = True
		thread.start()
		root.after(5000, update_plot_from_log)

def scale_y(ax):
	max_y = 0
	min_y = 0
	for line in ax.get_lines():
		if line.get_visible():
			ydata = line.get_data()[1]
			if ydata is not None and len(ydata) > 0:
				ydata_clean = ydata[~np.isnan(ydata)]
				if len(ydata_clean) > 0 and np.max(ydata_clean) > max_y:
					max_y = np.max(ydata_clean)
				if len(ydata_clean) > 0 and np.min(ydata_clean) < min_y:
					min_y = np.min(ydata_clean)
	max_y = math.ceil((max_y + 0.1)/5)*5
	min_y = math.floor((min_y - 0.1)/5)*5
	return min_y, max_y

def load_plots(file_path):
	try:
		df = pd.read_csv(file_path)
		time = df[CSVColumns.Time.value].values/60000
		end_time = time[-1]
		relative_setpoint1 = df[CSVColumns.SetPoint1Relative.value].values
		relative_setpoint2 = df[CSVColumns.SetPoint2Relative.value].values
		absolute_setpoint1 = df[CSVColumns.SetPoint1Absolute.value].values
		absolute_setpoint2 = df[CSVColumns.SetPoint2Absolute.value].values
		relative_temperature1_setpoint.set_data(time, relative_setpoint1)
		relative_temperature2_setpoint.set_data(time, relative_setpoint2)
		absolute_temperature1_setpoint.set_data(time, absolute_setpoint1)
		absolute_temperature2_setpoint.set_data(time, absolute_setpoint2)
		ax1.set_xlim(0, end_time)
		ax1.set_ylim(scale_y(ax1))
		ax2.set_xlim(0, end_time)
		ax2.set_ylim(scale_y(ax2))

		canvas.draw()
	except Exception as e:
		print(f"Failed to update time scale: {e}")
		print("Verify that your experiment file contains data in the time column.")

def update_plot_from_log():
	global already_existing_logs
	log_path = set(glob.glob("Logs/*.csv")) - already_existing_logs
	if log_path:
		try:
			df = pd.read_csv(log_path.pop())
			time = df[CSVColumns.Time.value].values / 60000
			room_temperature.set_data(time, df[CSVColumns.TemperatureAMB.value].values)
			absolute_heater1_temperature.set_data(time, df[CSVColumns.TemperatureH1.value].values)
			absolute_heater2_temperature.set_data(time, df[CSVColumns.TemperatureH2.value].values)
			relative_heater1_temperature.set_data(time, df[CSVColumns.TemperatureH1.value].values - df[CSVColumns.TemperatureAMB.value].values)
			relative_heater2_temperature.set_data(time, df[CSVColumns.TemperatureH2.value].values - df[CSVColumns.TemperatureAMB.value].values)
			computed_power1.set_data(time, df[CSVColumns.ComputedPWMH1.value])
			computed_power2.set_data(time, df[CSVColumns.ComputedPWMH2.value])
			applied_power1.set_data(time, df[CSVColumns.DisturbedPWMH1.value])
			applied_power2.set_data(time, df[CSVColumns.DisturbedPWMH2.value])
			ax1.set_ylim(scale_y(ax1))
			ax2.set_ylim(scale_y(ax2))
			canvas.draw()
		except Exception as e:
			print(f"Error updating plot from log:{e}")

	root.after(5000, update_plot_from_log)

def on_closing():
	global tecolab_process
	if tecolab_process is not None:
		tecolab_process.terminate()
		tecolab_process.wait()
	plt.close("all")
	root.quit()
	root.destroy()

def select_experiment_file():
	file_path = filedialog.askopenfilename(title = "Select an experiment file.", filetypes = [("CSV files", "*.csv")])
	if file_path:
		load_plots(file_path)
		file_name = os.path.splitext(os.path.basename(file_path))[0]
		selected_experiment_file.set(file_name)

def select_controller_file():
	file_path = filedialog.askopenfilename(title = "Select a controller file.", filetypes = [("Python files", "*.py")])
	if file_path:
		file_name = os.path.splitext(os.path.basename(file_path))[0]
		selected_controller_file.set(file_name)

def toggle_lines():
	absolute_temperature1_setpoint.set_visible(show_absolute_setpoint1.get())
	absolute_temperature2_setpoint.set_visible(show_absolute_setpoint2.get())
	relative_temperature1_setpoint.set_visible(show_relative_setpoint1.get())
	relative_temperature2_setpoint.set_visible(show_relative_setpoint2.get())
	room_temperature.set_visible(show_room_temperature.get())
	absolute_heater1_temperature.set_visible(show_absolute_temperature1.get())
	absolute_heater2_temperature.set_visible(show_absolute_temperature2.get())
	relative_heater1_temperature.set_visible(show_relative_temperature1.get())
	relative_heater2_temperature.set_visible(show_relative_temperature2.get())
	computed_power1.set_visible(show_computed_power1.get())
	computed_power2.set_visible(show_computed_power2.get())
	applied_power1.set_visible(show_applied_power1.get())
	applied_power2.set_visible(show_applied_power2.get())
	ax1.set_ylim(scale_y(ax1))
	ax2.set_ylim(scale_y(ax2))
	canvas.draw()

########## Colors ##########
background_color = "#D9D9D9"
setpoint1_color = "#FFA0A0"
setpoint2_color = "#A0A0FF"
roomtemperature_color = "#00FF00"
heater1_color = "#FF0000"
heater2_color = "#0000FF"

########## Root ##########
root = tk.Tk()
root.title("Temperature Control Laboratory (TeCoLab)")
root.geometry()
root.configure(bg = background_color)
root.protocol("WM_DELETE_WINDOW", on_closing)

########## GUI Variables ##########
selected_experiment_file = tk.StringVar()
selected_controller_file = tk.StringVar()
show_absolute_temperature1 = tk.BooleanVar(value = True)
show_absolute_temperature2 = tk.BooleanVar(value = True)
show_relative_temperature1 = tk.BooleanVar(value = True)
show_relative_temperature2 = tk.BooleanVar(value = True)
show_room_temperature = tk.BooleanVar(value = True)
show_absolute_setpoint1 = tk.BooleanVar(value = True)
show_absolute_setpoint2 = tk.BooleanVar(value = True)
show_relative_setpoint1 = tk.BooleanVar(value = True)
show_relative_setpoint2 = tk.BooleanVar(value = True)
show_computed_power1 = tk.BooleanVar(value = True)
show_computed_power2 = tk.BooleanVar(value = True)
show_applied_power1 = tk.BooleanVar(value = True)
show_applied_power2 = tk.BooleanVar(value = True)

########## Other Variables ##########
tecolab_process = None
already_existing_logs = set(glob.glob("Logs/*.csv"))

########## Buttons ##########
select_experiment_button = tk.Button(root, text = "Select experiment", width = 15, height = 1, command = select_experiment_file)
select_experiment_button.grid(row = 1, column = 1, padx = 20, pady = 5, sticky = "w")

select_controller_button = tk.Button(root, text = "Select controller", width = 15, height = 1, command = select_controller_file)
select_controller_button.grid(row = 3, column = 1, padx = 20, pady = 5, sticky = "w")

start_experiment_button = tk.Button(root, text = "START", width = 15, height = 1, command = start_experiment)
start_experiment_button.grid(row = 6, column = 1, padx= 20, pady = 5,  sticky = "w")

########## Labels ##########
experiment_file_label = tk.Entry(root, textvariable = selected_experiment_file, width = 25, state = 'readonly')
experiment_file_label.grid(row = 2, column = 1, padx = 20, pady = 5, sticky = "w")

controller_file_label = tk.Entry(root, textvariable = selected_controller_file, width = 25, state = 'readonly')
controller_file_label.grid(row = 4, column = 1, padx = 20, pady = 5, sticky = "w")

########## Checkboxes ##########
checkbox_frame = tk.LabelFrame(root, text = "Displayed Signals", padx = 10, pady = 5)
checkbox_frame.grid(row = 5, column = 1, padx = 20, pady = 20, sticky = "w")

tk.Checkbutton(checkbox_frame, text = "Abs. temp. 1", variable = show_absolute_temperature1, command = toggle_lines).pack(anchor = "w")
tk.Checkbutton(checkbox_frame, text = "Abs. temp. 2", variable = show_absolute_temperature2, command = toggle_lines).pack(anchor = "w")
tk.Checkbutton(checkbox_frame, text = "Rel. temp. 1", variable = show_relative_temperature1, command = toggle_lines).pack(anchor = "w")
tk.Checkbutton(checkbox_frame, text = "Rel. temp. 2", variable = show_relative_temperature2, command = toggle_lines).pack(anchor = "w")
tk.Checkbutton(checkbox_frame, text = "Room temp.", variable = show_room_temperature, command = toggle_lines).pack(anchor = "w")
tk.Checkbutton(checkbox_frame, text = "Abs. setpoint 1", variable = show_absolute_setpoint1, command = toggle_lines).pack(anchor = "w")
tk.Checkbutton(checkbox_frame, text = "Abs. setpoint 2", variable = show_absolute_setpoint2, command = toggle_lines).pack(anchor = "w")
tk.Checkbutton(checkbox_frame, text = "Rel. setpoint 1", variable = show_relative_setpoint1, command = toggle_lines).pack(anchor = "w")
tk.Checkbutton(checkbox_frame, text = "Rel. setpoint 2", variable = show_relative_setpoint2, command = toggle_lines).pack(anchor = "w")
tk.Checkbutton(checkbox_frame, text = "Computed power 1", variable = show_computed_power1, command = toggle_lines).pack(anchor = "w")
tk.Checkbutton(checkbox_frame, text = "Computed power 2", variable = show_computed_power2, command = toggle_lines).pack(anchor = "w")
tk.Checkbutton(checkbox_frame, text = "Applied power 1", variable = show_applied_power1, command = toggle_lines).pack(anchor = "w")
tk.Checkbutton(checkbox_frame, text = "Applied power 2", variable = show_applied_power2, command = toggle_lines).pack(anchor = "w")

########## Plots ##########
plot_frame = tk.Frame(root)
plot_frame.grid(row = 1, column = 2, rowspan = 6, padx = 20, pady = 5)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (6, 5), dpi = 100)
fig.tight_layout(pad = 4)
fig.patch.set_facecolor(background_color)  # Outside plot area

# Temperature plot figure
ax1.set_title("Temperature")
ax1.set_xlabel("Time (min.)")
ax1.set_ylabel("°C")
ax1.set_xlim(0,1)
ax1.set_ylim(-10,85)
ax1.grid(True)
ax1.set_facecolor(background_color)

# Power plot figure
ax2.set_title("Applied Power")
ax2.set_xlabel("Time (min.)")
ax2.set_ylabel("%Pmax")
ax2.set_xlim(0,1)
ax2.set_ylim(-10,110)
ax2.grid(True)
ax2.set_facecolor(background_color)

# Temperature plots
absolute_temperature1_setpoint = ax1.step([], [], label = "Abs. Temp. 1 Ref.", color = setpoint1_color, where = "post")[0]
absolute_temperature2_setpoint = ax1.step([], [], label = "Abs. Temp. 2 Ref.", color = setpoint2_color, where = "post")[0]
relative_temperature1_setpoint = ax1.step([], [], label = "Rel. Temp. 1 Ref.", color = setpoint1_color, where = "post")[0]
relative_temperature2_setpoint = ax1.step([], [], label = "Rel. Temp. 2 Ref.", color = setpoint2_color, where = "post")[0]
room_temperature = ax1.plot([], [], label = "Room Temp.", color = roomtemperature_color)[0]
absolute_heater1_temperature = ax1.plot([], [], label = "H1 Abs. Temp.", color = heater1_color)[0]
absolute_heater2_temperature = ax1.plot([], [], label = "H2 Abs. Temp.", color = heater2_color)[0]
relative_heater1_temperature = ax1.plot([], [], label = "H1 Rel. Temp.", color = heater1_color)[0]
relative_heater2_temperature = ax1.plot([], [], label = "H2 Rel. Temp.", color = heater2_color)[0]

# Power plots
computed_power1 = ax2.step([], [], label = "Computed Power 1.", color = setpoint1_color, where = "post")[0]
computed_power2 = ax2.step([], [], label = "Computed Power 2.", color = setpoint2_color, where = "post")[0]
applied_power1 = ax2.step([], [], label = "Applied Power 1.", color = heater1_color, where = "post")[0]
applied_power2 = ax2.step([], [], label = "Applied Power 2.", color = heater2_color, where = "post")[0]

# Embed the figure in Tkinter
canvas = FigureCanvasTkAgg(fig, master = plot_frame)
canvas.draw()
canvas.get_tk_widget().pack()

# Start the GUI event loop
root.mainloop()