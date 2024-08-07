import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial.tools.list_ports
import serial
import datetime
import os

class SerialDataLogger:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Data Logger")

        # Serial port settings
        self.p_Port = tk.StringVar()
        self.s_Port = tk.StringVar()
        self.baudrate = 9600

        # Default filenames
        self.p_filename = tk.StringVar()
        self.s_filename = tk.StringVar()

        # Create GUI elements
        self.create_gui()

        # Serial port instances
        self.ser1 = None
        self.ser2 = None

        # File handles
        self.file1 = None
        self.file2 = None

        # Folder path
        self.folder_path = ""

        # Populate available COM ports
        self.populate_com_ports()

    def create_gui(self):
        # Frame for serial port selection
        port_frame = ttk.LabelFrame(self.root, text="Serial Ports")
        port_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        # Dropdown menu for selecting COM the primary port
        p_Port_label = ttk.Label(port_frame, text="COM Port Primary:")
        p_Port_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.p_Port_dropdown = ttk.Combobox(port_frame, textvariable=self.p_Port, width=14)
        self.p_Port_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Dropdown menu for selecting COM the secondary port
        s_Port_label = ttk.Label(port_frame, text="COM Port Secondary:")
        s_Port_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.s_Port_dropdown = ttk.Combobox(port_frame, textvariable=self.s_Port, width=14)
        self.s_Port_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Connect button
        connect_btn = ttk.Button(port_frame, text="Connect", command=self.connect_serial)
        connect_btn.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky=tk.W)

        # Frame for displaying incoming data for the primary port
        data1_frame = ttk.LabelFrame(self.root, text="Incoming Data - Primary Cosmic Watch (Last 50 lines)")
        data1_frame.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        # Scrolled text widget for the primary port
        self.data1_text = scrolledtext.ScrolledText(data1_frame, wrap=tk.WORD, width=60, height=25)
        self.data1_text.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # Frame for displaying incoming data for the secondary port
        data2_frame = ttk.LabelFrame(self.root, text="Incoming Data - Secondary Cosmic Watch (Last 50 lines)")
        data2_frame.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        # Scrolled text widget for secondary port
        self.data2_text = scrolledtext.ScrolledText(data2_frame, wrap=tk.WORD, width=60, height=25)
        self.data2_text.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

    def populate_com_ports(self):
        # Clear any existing ports
        self.p_Port_dropdown['values'] = []
        self.s_Port_dropdown['values'] = []

        # Get list of available COM ports
        com_ports = [port.device for port in serial.tools.list_ports.comports()]

        # Update dropdown menus with available COM ports
        if com_ports:
            self.p_Port_dropdown['values'] = com_ports
            self.s_Port_dropdown['values'] = com_ports
            if len(com_ports) > 0:
                self.p_Port.set(com_ports[0])  # Select the first port by default
            if len(com_ports) > 1:
                self.s_Port.set(com_ports[1])  # Select the second port by default

    def get_current_timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def connect_serial(self):
        # Create a new folder with a timestamp
        self.folder_path = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(self.folder_path, exist_ok=True)

        # Update filenames with current timestamp and folder path
        self.p_filename.set(os.path.join(self.folder_path, "primary_data.txt"))
        self.s_filename.set(os.path.join(self.folder_path, "secondary_data.txt"))

        # Close previous connections if any
        if self.ser1 and self.ser1.is_open:
            self.ser1.close()
        if self.ser2 and self.ser2.is_open:
            self.ser2.close()

        # Open serial the primary port
        try:
            self.ser1 = serial.Serial(self.p_Port.get(), self.baudrate)
            self.data1_text.insert(tk.END, 'Connection established at ' + self.get_current_timestamp() + '\n')
            
            # Open file for writing for the primary port
            self.file1 = open(self.p_filename.get(), 'w')
            self.file1.write('Connection established at ' + self.get_current_timestamp() + '\n')

            self.root.after(5, self.connect_serial2)  # Wait 5ms before connecting to the secondary port
            self.root.after(100, self.read_p_serial_data)  # Start reading data from the primary port after 100ms
        except serial.SerialException as e:
            messagebox.showerror("Error", str(e))

    def connect_serial2(self):
        # Open serial the secondary port
        try:
            self.ser2 = serial.Serial(self.s_Port.get(), self.baudrate)
            self.data2_text.insert(tk.END, 'Connection established at ' + self.get_current_timestamp() + '\n')

            # Open file for writing for the secondary port
            self.file2 = open(self.s_filename.get(), 'w')
            self.file2.write('Connection established at ' + self.get_current_timestamp() + '\n')

            self.root.after(100, self.read_s_serial_data)  # Start reading data from the secondary port after 100ms
        except serial.SerialException as e:
            messagebox.showerror("Error", str(e))

    def read_p_serial_data(self):
        if self.ser1 and self.ser1.is_open:
            try:
                line = self.ser1.readline().decode().strip()
                self.data1_text.insert(tk.END, line + '\n')
                self.data1_text.see(tk.END)  # Scroll to the end

                # Write to file for the primary port if file is open
                if self.file1:
                    self.file1.write(line + '\n')

            except UnicodeDecodeError:
                pass  # Ignore decoding errors

        # Call itself again to read the next line
        self.root.after(10, self.read_p_serial_data)  # Schedule the next read after 10ms

    def read_s_serial_data(self):
        if self.ser2 and self.ser2.is_open:
            if self.ser2.in_waiting > 0:
                try:
                    line = self.ser2.readline().decode().strip()
                    self.data2_text.insert(tk.END, line + '\n')
                    self.data2_text.see(tk.END)  # Scroll to the end

                    # Write to file for the secondary port if file is open
                    if self.file2:
                        self.file2.write(line + '\n')

                except UnicodeDecodeError:
                    pass  # Ignore decoding errors

        # Schedule the next read for the secondary port after 10ms
        self.root.after(50, self.read_s_serial_data)

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
