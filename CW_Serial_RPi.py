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
        self.pPort = tk.StringVar()
        self.sPort = tk.StringVar()
        self.baudrate = 9600

        # Default filenames based on current date and time
        self.default_pFilename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + "_primary_data.txt"
        self.default_sFilename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + "_secondary_data.txt"

        # File settings for the primary port
        self.pFilename = tk.StringVar()
        self.pFilename.set(self.default_pFilename)

        # File settings for the secondary port
        self.sFilename = tk.StringVar()
        self.sFilename.set(self.default_sFilename)

        # Create GUI elements
        self.create_gui()

        # Serial port instances
        self.pSer = None
        self.sSer = None

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
        pPort_label = ttk.Label(port_frame, text="COM Port Primary:")
        pPort_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.pPort_dropdown = ttk.Combobox(port_frame, textvariable=self.pPort, width=30)
        self.pPort_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Dropdown menu for selecting COM the secondary port
        sPort_label = ttk.Label(port_frame, text="COM Port Secondary:")
        sPort_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.sPort_dropdown = ttk.Combobox(port_frame, textvariable=self.sPort, width=30)
        self.sPort_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Connect button
        connect_btn = ttk.Button(port_frame, text="Connect", command=self.connect_serial)
        connect_btn.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky=tk.W)

        # Frame for file settings
        file_frame = ttk.LabelFrame(self.root, text="File Settings")
        file_frame.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        # File name entry for the primary port
        pFile_label = ttk.Label(file_frame, text="File Name (Primary):")
        pFile_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.pFile_entry = ttk.Entry(file_frame, textvariable=self.pFilename, width=30)
        self.pFile_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # File name entry for the secondary port
        sFile_label = ttk.Label(file_frame, text="File Name (Secondary):")
        sFile_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.sFile_entry = ttk.Entry(file_frame, textvariable=self.sFilename, width=30)
        self.sFile_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Save button for both ports
        save_btn = ttk.Button(file_frame, text="Save Data", command=self.save_data)
        save_btn.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky=tk.W)

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
        self.pPort_dropdown['values'] = []
        self.sPort_dropdown['values'] = []

        # Get list of available COM ports
        com_ports = [port.device for port in serial.tools.list_ports.comports() if port.device.startswith('/dev/ttyAMA') or port.device.startswith('/dev/ttyUSB')]

        # Update dropdown menus with available COM ports
        if com_ports:
            self.pPort_dropdown['values'] = com_ports
            self.sPort_dropdown['values'] = com_ports
            if len(com_ports) > 0:
                self.pPort.set(com_ports[0])  # Select the first port by default
            if len(com_ports) > 1:
                self.sPort.set(com_ports[1])  # Select the second port by default

    def connect_serial(self):
        # Close previous connections if any
        if self.pSer and self.pSer.is_open:
            self.pSer.close()
        if self.sSer and self.sSer.is_open:
            self.sSer.close()

        # Open serial the primary port
        try:
            self.pSer = serial.Serial(self.pPort.get(), self.baudrate)
            self.root.after(5, self.connect_serial2)  # Wait 500ms before connecting to the secondary port
            self.root.after(100, self.read_p_serial_data)  # Start reading data from the primary port after 100ms
        except serial.SerialException as e:
            messagebox.showerror("Error", str(e))

    def connect_serial2(self):
        # Open serial the secondary port
        try:
            self.sSer = serial.Serial(self.sPort.get(), self.baudrate)
            self.root.after(100, self.read_s_serial_data)  # Start reading data from the secondary port after 100ms
        except serial.SerialException as e:
            messagebox.showerror("Error", str(e))

    def read_p_serial_data(self):
        if self.pSer and self.pSer.is_open:
            try:
                line = self.pSer.readline().decode().strip()
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
        if self.sSer and self.sSer.is_open:
            if self.sSer.in_waiting > 0:
                try:
                    line = self.sSer.readline().decode().strip()
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
        file_path1 = filedialog.asksaveasfilename(initialfile=self.pFilename.get(),
                                                  filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path1:
            try:
                # Close existing file for the primary port if any
                if self.pFile:
                    self.pFile.close()

                # Open new file for the primary port for writing
                self.pFile = open(file_path1, 'w')
                self.pFilename.set(file_path1)

                # Write existing data in scrolled text widget for the primary port to file
                data1 = self.data1_text.get('1.0', tk.END)
                self.pFile.write(data1)

            except IOError as e:
                messagebox.showerror("Error", f"Failed to save file for Primary Cosmic Watch: {e}")

        # Open file dialog to choose file location for the secondary port
        file_path2 = filedialog.asksaveasfilename(initialfile=self.sFilename.get(),
                                                  filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path2:
            try:
                # Close existing file for the secondary port if any
                if self.sFile:
                    self.sFile.close()

                # Open new file for the secondary port for writing
                self.sFile = open(file_path2, 'w')
                self.sFilename.set(file_path2)

                # Write existing data in scrolled text widget for the secondary port to file
                data2 = self.data2_text.get('1.0', tk.END)
                self.sFile.write(data2)

                messagebox.showinfo("File Saved", f"Data saved to {file_path1} and {file_path2}")

            except IOError as e:
                messagebox.showerror("Error", f"Failed to save file for Secondary Cosmic Watch: {e}")

    def cleanup(self):
        # Cleanup resources
        if self.pSer and self.pSer.is_open:
            self.pSer.close()
        if self.sSer and self.sSer.is_open:
            self.sSer.close()
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
