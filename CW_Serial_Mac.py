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
        self.p_Port = tk.StringVar()
        self.s_Port = tk.StringVar()
        self.baudrate = 9600

        # Default filenames based on current date and time
        self.default_filename1 = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_primary_data.txt"
        self.default_filename2 = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_secondary_data.txt"

        # File settings for the primary port
        self.filename1 = tk.StringVar()
        self.filename1.set(self.default_filename1)

        # File settings for the secondary port
        self.filename2 = tk.StringVar()
        self.filename2.set(self.default_filename2)

        # Create GUI elements
        self.create_gui()

        # Serial port instances
        self.primaryCW = None
        self.secondaryCW = None

        # File handles
        self.pFile = None
        self.sFile = None

        # Populate available COM ports
        self.populate_com_ports()

    def create_gui(self):
        # Frame for serial port selection
        port_frame = ttk.LabelFrame(self.root, text="Serial Ports")
        port_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        # Dropdown menu for selecting COM the primary port
        p_Port_label = ttk.Label(port_frame, text="COM Port Primary:")
        p_Port_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.p_Port_dropdown = ttk.Combobox(port_frame, textvariable=self.p_Port, width=30)
        self.p_Port_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Dropdown menu for selecting COM the secondary port
        s_Port_label = ttk.Label(port_frame, text="COM Port Secondary:")
        s_Port_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.s_Port_dropdown = ttk.Combobox(port_frame, textvariable=self.s_Port, width=30)
        self.s_Port_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Connect button
        connect_btn = ttk.Button(port_frame, text="Connect", command=self.connect_serial)
        connect_btn.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky=tk.W)

        # Frame for file settings
        file_frame = ttk.LabelFrame(self.root, text="File Settings")
        file_frame.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        # File name entry for the primary port
        pFile_label = ttk.Label(file_frame, text="File Name (Primary):")
        pFile_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.pFile_entry = ttk.Entry(file_frame, textvariable=self.filename1, width=30)
        self.pFile_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # File name entry for the secondary port
        sFile_label = ttk.Label(file_frame, text="File Name (Secondary):")
        sFile_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.sFile_entry = ttk.Entry(file_frame, textvariable=self.filename2, width=30)
        self.sFile_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Save button for both ports
        save_btn = ttk.Button(file_frame, text="Save Data", command=self.save_data)
        save_btn.grid(row=0, column=3, rowspan=2, padx=5, pady=5, sticky=tk.W)

        # Frame for displaying incoming data for the primary port
        data1_frame = ttk.LabelFrame(self.root, text="Incoming Data - Primary Cosmic Watch (Last 50 lines)")
        data1_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        # Scrolled text widget for the primary port
        self.data1_text = scrolledtext.ScrolledText(data1_frame, wrap=tk.WORD, width=60, height=15)
        self.data1_text.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # Frame for displaying incoming data for the secondary port
        data2_frame = ttk.LabelFrame(self.root, text="Incoming Data - Secondary Cosmic Watch (Last 50 lines)")
        data2_frame.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

        # Scrolled text widget for the secondary port
        self.data2_text = scrolledtext.ScrolledText(data2_frame, wrap=tk.WORD, width=60, height=15)
        self.data2_text.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

    def populate_com_ports(self):
        # Clear any existing ports
        self.p_Port_dropdown['values'] = []
        self.s_Port_dropdown['values'] = []

        # Get list of available COM ports
        com_ports = [port.device for port in serial.tools.list_ports.comports() if port.device.startswith('/dev/tty.') or port.device.startswith('/dev/cu.')]

        # Update dropdown menus with available COM ports
        if com_ports:
            self.p_Port_dropdown['values'] = com_ports
            self.s_Port_dropdown['values'] = com_ports
            if len(com_ports) > 0:
                self.p_Port.set(com_ports[0])  # Select the first port by default
            if len(com_ports) > 1:
                self.s_Port.set(com_ports[1])  # Select the second port by default

    def connect_serial(self):
        # Close previous connections if any
        if self.primaryCW and self.primaryCW.is_open:
            self.primaryCW.close()
        if self.secondaryCW and self.secondaryCW.is_open:
            self.secondaryCW.close()

        # Open serial the primary port
        try:
            self.primaryCW = serial.Serial(self.p_Port.get(), self.baudrate)
            self.root.after(5, self.connect_serial2)  # Wait 500ms before connecting to the secondary port
            self.root.after(100, self.read_p_serial_data)  # Start reading data from the primary port after 100ms
        except serial.SerialException as e:
            messagebox.showerror("Error", str(e))

    def connect_serial2(self):
        # Open serial the secondary port
        try:
            self.secondaryCW = serial.Serial(self.s_Port.get(), self.baudrate)
            self.root.after(100, self.read_s_serial_data)  # Start reading data from the secondary port after 100ms
        except serial.SerialException as e:
            messagebox.showerror("Error", str(e))

    def read_p_serial_data(self):
        if self.primaryCW and self.primaryCW.is_open:
            try:
                line = self.primaryCW.readline().decode().strip()
                self.data1_text.insert(tk.END, line + '\n')
                self.data1_text.see(tk.END)  # Scroll to the end

                # Write to file for the primary port if file is open
                if self.pFile:
                    self.pFile.write(line + '\n')

            except UnicodeDecodeError:
                pass  # Ignore decoding errors

        # Call itself again to read the next line
        self.root.after(10, self.read_p_serial_data)  # Schedule the next read after 10ms

    def read_s_serial_data(self):
        if self.secondaryCW and self.secondaryCW.is_open:
            if self.secondaryCW.in_waiting > 0:
                try:
                    line = self.secondaryCW.readline().decode().strip()
                    self.data2_text.insert(tk.END, line + '\n')
                    self.data2_text.see(tk.END)  # Scroll to the end

                    # Write to file for the secondary port if file is open
                    if self.sFile:
                        self.sFile.write(line + '\n')

                except UnicodeDecodeError:
                    pass  # Ignore decoding errors

        # Schedule the next read for the secondary port after 10ms
        self.root.after(50, self.read_s_serial_data)

    def save_data(self):
        # Open file dialog to choose file location for the primary port
        file_path1 = filedialog.asksaveasfilename(initialfile=self.filename1.get(),
                                                  filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path1:
            try:
                # Close existing file for the primary port if any
                if self.pFile:
                    self.pFile.close()

                # Open new file for the primary port for writing
                self.pFile = open(file_path1, 'w')
                self.filename1.set(file_path1)

                # Write existing data in scrolled text widget for the primary port to file
                data1 = self.data1_text.get('1.0', tk.END)
                self.pFile.write(data1)

            except IOError as e:
                messagebox.showerror("Error", f"Failed to save file for Primary Cosmic Watch: {e}")

        # Open file dialog to choose file location for the secondary port
        file_path2 = filedialog.asksaveasfilename(initialfile=self.filename2.get(),
                                                  filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path2:
            try:
                # Close existing file for the secondary port if any
                if self.sFile:
                    self.sFile.close()

                # Open new file for the secondary port for writing
                self.sFile = open(file_path2, 'w')
                self.filename2.set(file_path2)

                # Write existing data in scrolled text widget for the secondary port to file
                data2 = self.data2_text.get('1.0', tk.END)
                self.sFile.write(data2)

                messagebox.showinfo("File Saved", f"Data saved to {file_path1} and {file_path2}")

            except IOError as e:
                messagebox.showerror("Error", f"Failed to save file for Secondary Cosmic Watch: {e}")

    def cleanup(self):
        # Cleanup resources
        if self.primaryCW and self.primaryCW.is_open:
            self.primaryCW.close()
        if self.secondaryCW and self.secondaryCW.is_open:
            self.secondaryCW.close()
        if self.pFile:
            self.pFile.close()
        if self.sFile:
            self.sFile.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialDataLogger(root)
    root.protocol("WM_DELETE_WINDOW", app.cleanup)  # Handle window close event
    root.mainloop()

    # Cleanup
    app.cleanup()
