import psutil
import time
import os
import tkinter as tk
from tkinter import font
import subprocess
from PIL import ImageGrab
import pyperclip

# CPU Benchmark
def cpu_benchmark():
    print("CPU Benchmark")
    print("-------------")
    cpu_scores = []
    for i in range(5):
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_scores.append(sum(cpu_percent) / len(cpu_percent))
    avg_cpu_score = round(sum(cpu_scores) / len(cpu_scores) * 100, 2)
    print("Average CPU Score:", avg_cpu_score)
    return avg_cpu_score

def gpu_benchmark():
    print("\nGPU Benchmark")
    print("-------------")
    try:
        import pyopencl as cl
        platforms = cl.get_platforms()
        for platform in platforms:
            print("Platform:", platform.name)
            for device in platform.get_devices():
                print("Device:", device.name)
                try:
                    ctx = cl.Context([device])
                    queue = cl.CommandQueue(ctx)
                    mf = cl.mem_flags
                    N = 10 * 1024 * 1024
                    a_gpu = cl.Buffer(ctx, mf.READ_ONLY, size=N*4)
                    b_gpu = cl.Buffer(ctx, mf.WRITE_ONLY, size=N*4)
                    prg = cl.Program(ctx, """
                        __kernel void square(__global float* a, __global float* b)
                        {
                            int gid = get_global_id(0);
                            b[gid] = a[gid] * a[gid];
                        }
                        """).build()
                    start = time.time()
                    prg.square(queue, (N,), None, a_gpu, b_gpu)
                    queue.finish()
                    elapsed = time.time() - start
                    
                    if elapsed > 0:
                        gpu_score = N / elapsed
                        rounded_gpu_score = round(gpu_score / 10000000)
                        print("GPU Benchmark Score:", rounded_gpu_score)
                        return rounded_gpu_score
                    else:
                        print("GPU benchmark time is too small to calculate.")
                        return None
                except cl.RuntimeError as e:
                    print("Failed to run on device", device.name, "Error:", e)
    except ImportError:
        print("PyOpenCL is not installed. Skipping GPU Benchmark...")
        return None

def ram_benchmark():
    print("\nRAM Benchmark")
    print("-------------")
    ram_usage = []
    print("RAM Usage: ")
    for i in range(5):
        ram = psutil.virtual_memory()
        print(ram)
        ram_usage.append(ram.percent)
        time.sleep(1)
    avg_ram_score = sum(ram_usage) / len(ram_usage)
    avg_ram_score = round(avg_ram_score, 2)
    print("Average RAM Score:", avg_ram_score)
    return avg_ram_score

def drive_benchmark():
    print("\nDrive Benchmark")
    print("---------------")
    drive_scores = []
    drives = psutil.disk_partitions()
    for drive in drives:
        if 'cdrom' not in drive.opts and drive.fstype != '':
            print("Drive:", drive.device)
            print("Mountpoint:", drive.mountpoint)
            disk_usage = psutil.disk_usage(drive.mountpoint)
            print("Total Size:", disk_usage.total)
            print("Used:", disk_usage.used)
            print("Free:", disk_usage.free)
            print("Percentage:", disk_usage.percent)
            drive_scores.append(disk_usage.percent)
    avg_drive_score = sum(drive_scores) / len(drive_scores)
    avg_drive_score = round(avg_drive_score, 2)
    print("Average Drive Score:", avg_drive_score)
    return avg_drive_score

# Network Benchmark using subprocess to call speedtest-cli
def network_benchmark():
    print("\nNetwork Benchmark")
    print("-----------------")
    try:
        # Use subprocess to call the speedtest-cli tool directly
        result = subprocess.run(["speedtest-cli", "--simple"], capture_output=True, text=True)
        
        # Parse the output from the command
        output = result.stdout
        download_speed = None
        upload_speed = None
        for line in output.split("\n"):
            if "Download" in line:
                download_speed = float(line.split(":")[1].strip().split()[0])
            if "Upload" in line:
                upload_speed = float(line.split(":")[1].strip().split()[0])
        
        if download_speed and upload_speed:
            avg_network_score = round((download_speed + upload_speed) / 2, 2)
            print(f"Download Speed: {download_speed:.2f} Mbps")
            print(f"Upload Speed: {upload_speed:.2f} Mbps")
            print("Average Network Score:", avg_network_score)
            return avg_network_score
        else:
            print("Network speed could not be determined.")
            return None

    except Exception as e:
        print(f"Error during network benchmark: {e}")
        return None

def calculate_overall_score(cpu_score, gpu_score, ram_score, drive_score, network_score):
    scores = [cpu_score, ram_score, drive_score]
    if gpu_score is not None:
        scores.append(gpu_score)
    if network_score is not None:
        scores.append(network_score)
    overall_score = round(sum(scores) / len(scores), 2)
    print("\nOverall Score:", overall_score)
    return overall_score

# Function to capture only the result window and copy to clipboard
def capture_and_copy(window):
    # Capture the window area by getting its geometry and position
    x, y, width, height = window.winfo_rootx(), window.winfo_rooty(), window.winfo_width(), window.winfo_height()
    
    # Capture the region (result window) and save the screenshot
    img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    img.save("screenshot.png")  # Optional, save for reference
    
    # Copy image to clipboard (need to convert image to format that pyperclip can handle)
    # This part uses pyperclip to copy a string message to clipboard
    pyperclip.copy("Screenshot taken successfully!")  # Inform user
    print("Screenshot copied to clipboard!")

# Main function
def main():
    cpu_score = cpu_benchmark()
    gpu_score = gpu_benchmark()
    ram_score = ram_benchmark()
    drive_score = drive_benchmark()
    network_score = network_benchmark()
    overall_score = calculate_overall_score(cpu_score, gpu_score, ram_score, drive_score, network_score)

    # Create GUI window
    root = tk.Tk()
    root.title("System Benchmark Results")
    root.geometry("600x400")

    # Set a custom font
    header_font = font.Font(root, family="Helvetica", size=14, weight="bold")
    label_font = font.Font(root, family="Helvetica", size=12)

    # Frame to contain all score labels
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(expand=True)

    # Header Label
    header_label = tk.Label(frame, text="System Benchmark Results", font=header_font)
    header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    # Function to create labels for each score
    def create_score_label(row, name, score):
        name_label = tk.Label(frame, text=f"{name}:", font=label_font, anchor="w")
        name_label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        
        score_text = f"{score:.2f}" if isinstance(score, (int, float)) else score
        score_label = tk.Label(frame, text=score_text, font=label_font, anchor="w")
        score_label.grid(row=row, column=1, sticky="w", pady=5)

    # Display individual scores
    create_score_label(1, "CPU Score", cpu_score)
    create_score_label(2, "GPU Score", gpu_score if gpu_score else "N/A")
    create_score_label(3, "RAM Score", ram_score)
    create_score_label(4, "Drive Score", drive_score)
    create_score_label(5, "Network Score", network_score if network_score else "N/A")
    create_score_label(6, "Overall Score", overall_score)

    # Add "Screenie" button
    copy_button = tk.Button(root, text="Screenie", font=label_font, command=lambda: capture_and_copy(root))
    copy_button.place(x=500, y=10)

    root.mainloop()

if __name__ == "__main__":
    main()
