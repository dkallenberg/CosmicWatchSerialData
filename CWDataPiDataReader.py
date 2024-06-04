import serial
import tkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Serial port configuration
port = '/dev/ttyUSB0'  # Replace with your USB device port
baud_rate = 9600  # Replace with your baud rate

# Initialize serial connection
ser = serial.Serial(port, baud_rate)

# Lists to store data
time_data = []
sensor_data = []
data_lines = []

# Function to update the graph
def update_graph():
    # Clear the existing graph
    plot.clear()
    
    # Plot new data
    plot.plot(time_data, sensor_data)
    plot.set_xlabel('Time')
    plot.set_ylabel('Sensor Data')
    plot.set_title('Serial Data Graph')
    
    # Redraw the graph
    canvas.draw()

# Function to update the data display box
def update_data_display():
    # Get the last 50 lines of data
    last_50_lines = '\n'.join(data_lines[-50:])
    
    # Clear the existing content in the text box
    data_text.delete('1.0', tk.END)
    
    # Insert the new data into the text box
    data_text.insert(tk.END, last_50_lines)

# Function to save data to a file
def save_data():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write('\n'.join(data_lines))

# Main loop
def read_serial():
    # Read serial data
    data = ser.readline().decode().strip()
    if data:
        # Split data into time and sensor value
        time, sensor_value = data.split(',')
        
        # Append data to lists
        time_data.append(time)
        sensor_data.append(float(sensor_value))
        
        # Write data to file
        data_lines.append(data)
        
        # Update the graph
        update_graph()
        
        # Update the data display box
        update_data_display()
    
    # Schedule the next read after 100 milliseconds
    root.after(100, read_serial)

# Create the main window
root = tk.Tk()
root.title('Serial Data Graph')

# Create the graph figure and canvas
fig = Figure(figsize=(8, 6), dpi=80)
plot = fig.add_subplot(1, 1, 1)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Create a frame for the text box and save button
frame = tk.Frame(root)
frame.pack()

# Create the data display box
data_text = tk.Text(frame, height=10, width=50)
data_text.pack(side=tk.LEFT, padx=10, pady=10)

# Create the save button
save_button = tk.Button(frame, text="Save Data", command=save_data)
save_button.pack(side=tk.RIGHT, padx=10, pady=10)

# Start reading serial data
read_serial()

# Start the Tkinter event loop
root.mainloop()
