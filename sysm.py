import tkinter as tk
from tkinter import ttk
from psutil import cpu_percent, virtual_memory
from subprocess import check_output
from platform import system

# No macOS support because there is no easy way to get system stats on macOS (also i hate macOS).

class Main:
    def __init__(self, root):
        self.root = root
        self.root.title("sysm")
        self.root.geometry("800x800")  
        self.root.configure(bg="#1F1F1F")  

        style = ttk.Style()
        
        style.configure("TProgressbar", 
                        troughcolor="#2B2B2B", 
                        background="#66FF00",
                        bd = 2,
                        releif = tk.SUNKEN)


# MAIN FRAME

        self.frame = tk.Frame(root, bg="#1F1F1F")
        self.frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

# ALL CHILDREN OF THE MAIN FRAME!

        # Title Label
        self.titleLabel = tk.Label(self.frame, text="System Statistics", font=("JetBrains Mono", 18, "bold", "underline"), bg="#1F1F1F", fg="#FF5733")                                                                                                                      
        self.titleLabel.pack(pady=10)                                                                                                               

        # HostName Label
        self.hostLabel = tk.Label(self.frame, text = f"Host Name : {self.hostName()}", font = ("JetBrains Mono", 10, "bold"),bg="#1F1F1F", fg="#FFFFFF")
        self.hostLabel.pack(pady=5)
        
        # CPU Group 
        self.cpuProg = tk.DoubleVar()
        self.cpuLabel = tk.Label(self.frame, text="CPU Usage: 0%", font=("JetBrains Mono", 14), bg="#1F1F1F", fg="#2980B9")
        self.createGroup("CPU", self.cpuName(), self.cpuLabel, self.cpuProg)

        # GPU Group
        self.gpuProg = tk.DoubleVar()
        self.gpuLabel = tk.Label(self.frame, text="GPU Usage: 0%", font=("JetBrains Mono", 14), bg="#1F1F1F", fg="#27AE60")
        self.createGroup("GPU", self.gpuName(), self.gpuLabel, self.gpuProg)

        # Memory Group 
        self.memProg = tk.DoubleVar()
        self.memLabel = tk.Label(self.frame, text="Memory Usage: 0%", font=("JetBrains Mono", 14), bg="#1F1F1F", fg="#8E44AD")
        self.createGroup("Memory", f"{self.maxRamAmt()} GB", self.memLabel, self.memProg)

        self.update()

# CREATE GROUP!!!

    def createGroup(self, title, name, usage_label, progress_var):
        """Create a section with a title, name label, usage label, and progress bar."""

        frame = tk.Frame(self.frame, bg="#1F1F1F", bd=5, relief=tk.GROOVE)
        frame.pack(pady=10, fill=tk.X)

        titles= tk.Label(frame, text=title, font=("JetBrains Mono", 16, "bold"), bg="#1F1F1F", fg="#FF5733")
        titles.pack(pady=5)

        name = tk.Label(frame, text=name, font=("JetBrains Mono", 14), bg="#1F1F1F", fg="#AB2733")
        name.pack(pady=5)

        # Update the usage label to show the actual usage percentage later
        self.usage_label = usage_label
        usage_label.pack(pady=5)

        progress_var.set(0)
        val = progress_var.get()   
        if val <= 50:
            style = ttk.Style()
            style.configure("TProgressbar", 
                        troughcolor="#2B2B2B", 
                        background="#66FF00",
                        bd = 2,
                        releif = tk.SUNKEN) 
            
        else:
            style = ttk.Style()
        
            style.configure("TProgressbar", 
                        troughcolor="#2B2B2B", 
                        background="#B10000",
                        bd = 2,
                        releif = tk.SUNKEN)
            
        progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100, style="TProgressbar")
        progress_bar.pack(pady=5, fill=tk.X)

            
# FUNCTONS FOR FETCHING ALL NEEDED VALUES!

    def update(self):
        cpuUsage = cpu_percent(interval=1)
        gpuUsage = self.gpuUsage()
        memoryUsage = self.memUsage()

        # Update the usage labels with actual values

        self.cpuLabel.config(text=f"CPU Usage: {cpuUsage}%")
        self.gpuLabel.config(text=f"GPU Usage: {gpuUsage:.1f}%")
        self.memLabel.config(text=f"Memory Usage: {memoryUsage:.1f}%")

        # Update progress bars
        self.cpuProg.set(cpuUsage)
        self.gpuProg.set(gpuUsage)
        self.memProg.set(memoryUsage)

        
        self.root.after(500, self.update) 


    def maxRamAmt(self):
        return round(virtual_memory().total / (1024 ** 3), 2) #omg stackoverflow was right


    def memUsage(self):
        meminuse = virtual_memory()
        return meminuse.percent
    
    def hostName(self):
        if system() == "Linux":
            try:
                with open("/etc/hostname", "r") as f:
                    for line in f:
                        return line
                    
            except Exception:
                return None
            
        elif system() == "Windows":
            try:
                host = check_output("whoami", shell=True)
                output = host.split()

                return output
            
            except Exception:
                return None
            
            
        return None

    def cpuName(self):

        if system() == "Windows":
        
            try:
                output = check_output("wmic cpu get name", shell=True)
                cpuName = output.split()[1:7] 
                return cpuName if cpuName else "Unknown CPU"
        
            except Exception:
                return "Unknown CPU"
        
        elif system() == "Linux":
        
            try:
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()  
        
            except FileNotFoundError:
                return "Unknown CPU"
        
        return "Unknown CPU"

    def gpuName(self):

        if system() == "Windows":
            
            try:
                output = check_output("wmic path win32_VideoController get name", shell=True)
                gpuName = output.split()[1:4]  
                return gpuName if gpuName else "Unknown GPU"    
            
            except Exception:
                return "Unknown GPU"
            
        
        
        elif system() == "Linux":

            try:
                output = check_output("lspci | grep -i 3D", shell=True) #previously VGA! now its the 3D Controller listed in lspci

                gpuName = output.decode().strip().split(":")[2]  

                if not(gpuName):
                    output = check_output("lspci | grep -i vga", shell=True)
                    gpuName = output.decode().strip().split(":")[1] # to check if you have integrated gpu
                     
                return gpuName if gpuName else "Unknown GPU"
            
            except Exception:
                return "Unknown GPU"
            
        return "Unknown GPU"

    def gpuUsage(self):
        
        if system() == "Windows":
            try:
                output = check_output("wmic path win32_VideoController get loadpercentage", shell=True)
                gpu_loads = output.decode().splitlines()[1:]  # Skip the header (only for windows)
                gpu_load = [float(load.strip()) for load in gpu_loads if load.strip()]
                return gpu_load[0] if gpu_load else 0.0
            
            except Exception:
                return 0.0
            
        elif system() == "Linux":
            try:
                output = check_output("nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader", shell=True)
                return float(output.decode().strip().rstrip('%'))  
            
            except Exception:
                try:
                    output = check_output("radeontop -d -", shell=True)
                    return self.parse_amd_gpu_usage(output.decode())
                
                except Exception:
                    return 0.0
                
        return 0.0

    def parse_amd_gpu_usage(self, output):
        # Parse the output from `radeontop` to extract usage percentage.
        for line in output.splitlines():
            if "GPU" in line:
                return float(line.split()[4].rstrip('%'))  # Extract the usage value
        return 0.0

# START THE MONITOR

def run():
    root = tk.Tk()
    app = Main(root)
    root.mainloop()

run()
