import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import serial.tools.list_ports
import serial
import datetime

class SerialDataLogger:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Data Logger")

        # Serial port settings
        self.port1 = tk.StringVar()
        self.port2 = tk.StringVar()
        self.baudrate = 9600

        # Default filenames based on current date and time
        self.default_filename1 = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_serial_data1.txt"
        self.default_filename2 = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_serial_data2.txt"

        # File settings for port 1
        self.filename1 = tk.StringVar()
        self.filename1.set(self.default_filename1)

        # File settings for port 2
        self.filename2 = tk.StringVar()
        self.filename2.set(self.default_filename2)

        # Create GUI elements
        self.create_gui()

        # Serial port instances
        self.ser1 = None
        self.ser2 = None

        # File handles
        self.file1 = None
        self.file2 = None

        # Populate available COM ports
        self.populate_com_ports()

    def create_gui(self):
        # Frame for serial port selection
        port_frame = ttk.LabelFrame(self.root, text="Serial Ports")
        port_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        # Dropdown menu for selecting COM port 1
        port1_label = ttk.Label(port_frame, text="COM Port Primary:")
        port1_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.port1_dropdown = ttk.Combobox(port_frame, textvariable=self.port1, width=30)
        self.port1_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Dropdown menu for selecting COM port 2
        port2_label = ttk.Label(port_frame, text="COM Port Secondary:")
        port2_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.port2_dropdown = ttk.Combobox(port_frame, textvariable=self.port2, width=30)
        self.port2_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Connect button
        connect_btn = ttk.Button(port_frame, text="Connect", command=self.connect_serial)
        connect_btn.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky=tk.W)

        # Frame for file settings
        file_frame = ttk.LabelFrame(self.root, text="File Settings")
        file_frame.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        # File name entry for port 1
        file1_label = ttk.Label(file_frame, text="File Name (Port 1):")
        file1_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.file1_entry = ttk.Entry(file_frame, textvariable=self.filename1, width=30)
        self.file1_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # File name entry for port 2
        file2_label = ttk.Label(file_frame, text="File Name (Port 2):")
        file2_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.file2_entry = ttk.Entry(file_frame, textvariable=self.filename2, width=30)
        self.file2_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Save button for both ports
        save_btn = ttk.Button(file_frame, text="Save Data", command=self.save_data)
        save_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # Frame for displaying incoming data for port 1
        data1_frame = ttk.LabelFrame(self.root, text="Incoming Data - Primary Cosmic Watch (Last 50 lines)")
        data1_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        # Scrolled text widget for port 1
        self.data1_text = scrolledtext.ScrolledText(data1_frame, wrap=tk.WORD, width=60, height=15)
        self.data1_text.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # Frame for displaying incoming data for port 2
        data2_frame = ttk.LabelFrame(self.root, text="Incoming Data - Secondary Cosmic Watch (Last 50 lines)")
        data2_frame.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

        # Scrolled text widget for port 2
        self.data2_text = scrolledtext.ScrolledText(data2_frame, wrap=tk.WORD, width=60, height=15)
        self.data2_text.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

    def populate_com_ports(self):
        # Clear any existing ports
        self.port1_dropdown['values'] = []
        self.port2_dropdown['values'] = []

        # Get list of available COM ports
        com_ports = [port.device for port in serial.tools.list_ports.comports() if port.device.startswith('/dev/tty.') or port.device.startswith('/dev/cu.')]

        # Update dropdown menus with available COM ports
        if com_ports:
            self.port1_dropdown['values'] = com_ports
            self.port2_dropdown['values'] = com_ports
            if len(com_ports) > 0:
                self.port1.set(com_ports[0])  # Select the first port by default
            if len(com_ports) > 1:
                self.port2.set(com_ports[1])  # Select the second port by default

    def connect_serial(self):
        # Close previous connections if any
        if self.ser1 and self.ser1.is_open:
            self.ser1.close()
        if self.ser2 and self.ser2.is_open:
            self.ser2.close()

        # Open serial port 1
        try:
            self.ser1 = serial.Serial(self.port1.get(), self.baudrate)
            self.root.after(5, self.connect_serial2)  # Wait 500ms before connecting to port 2
            self.root.after(100, self.read_serial_data1)  # Start reading data from port 1 after 100ms
        except serial.SerialException as e:
            messagebox.showerror("Error", str(e))

    def connect_serial2(self):
        # Open serial port 2
        try:
            self.ser2 = serial.Serial(self.port2.get(), self.baudrate)
            self.root.after(100, self.read_serial_data2)  # Start reading data from port 2 after 100ms
        except serial.SerialException as e:
            messagebox.showerror("Error", str(e))

    def read_serial_data1(self):
        if self.ser1 and self.ser1.is_open:
            try:
                line = self.ser1.readline().decode().strip()
                self.data1_text.insert(tk.END, line + '\n')
                self.data1_text.see(tk.END)  # Scroll to the end

                # Write to file for port 1 if file is open
                if self.file1:
                    self.file1.write(line + '\n')

            except UnicodeDecodeError:
                pass  # Ignore decoding errors

        # Call itself again to read the next line
        self.root.after(10, self.read_serial_data1)  # Schedule the next read after 10ms

    def read_serial_data2(self):
        if self.ser2 and self.ser2.is_open:
            if self.ser2.in_waiting > 0:
                try:
                    line = self.ser2.readline().decode().strip()
                    self.data2_text.insert(tk.END, line + '\n')
                    self.data2_text.see(tk.END)  # Scroll to the end

                    # Write to file for port 2 if file is open
                    if self.file2:
                        self.file2.write(line + '\n')

                except UnicodeDecodeError:
                    pass  # Ignore decoding errors

        # Schedule the next read for port 2 after 10ms
        self.root.after(50, self.read_serial_data2)

    def save_data(self):
        # Open file dialog to choose file location for port 1
        file_path1 = filedialog.asksaveasfilename(initialfile=self.filename1.get(),
                                                  filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path1:
            try:
                # Close existing file for port 1 if any
                if self.file1:
                    self.file1.close()

                # Open new file for port 1 for writing
                self.file1 = open(file_path1, 'w')
                self.filename1.set(file_path1)

                # Write existing data in scrolled text widget for port 1 to file
                data1 = self.data1_text.get('1.0', tk.END)
                self.file1.write(data1)

            except IOError as e:
                messagebox.showerror("Error", f"Failed to save file for Primary Cosmic Watch: {e}")

        # Open file dialog to choose file location for port 2
        file_path2 = filedialog.asksaveasfilename(initialfile=self.filename2.get(),
                                                  filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path2:
            try:
                # Close existing file for port 2 if any
                if self.file2:
                    self.file2.close()

                # Open new file for port 2 for writing
                self.file2 = open(file_path2, 'w')
                self.filename2.set(file_path2)

                # Write existing data in scrolled text widget for port 2 to file
                data2 = self.data2_text.get('1.0', tk.END)
                self.file2.write(data2)

                messagebox.showinfo("File Saved", f"Data saved to {file_path1} and {file_path2}")

            except IOError as e:
                messagebox.showerror("Error", f"Failed to save file for Secondary Cosmic Watch: {e}")

    def cleanup(self):
        # Cleanup resources
        if self.ser1 and self.ser1.is_open:
            self.ser1.close()
        if self.ser2 and self.ser2.is_open:
            self.ser2.close()
        if self.file1:
            self.file1.close()
        if self.file2:
            self.file2.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialDataLogger(root)
    root.protocol("WM_DELETE_WINDOW", app.cleanup)  # Handle window close event
    root.mainloop()

    # Cleanup
    app.cleanup()
