import psutil
import time
import os
import tkinter as tk
from tkinter import font
import speedtest

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
                    
                    # Check if elapsed is too small
                    if elapsed > 0:
                        gpu_score = N / elapsed
                        # Round the GPU benchmark score to the first two figures
                        rounded_gpu_score = round(gpu_score / 10000000)  # Rounding to first two figures
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

# RAM Benchmark
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
    avg_ram_score = round(avg_ram_score, 2)  # Rounding to two decimal places
    print("Average RAM Score:", avg_ram_score)
    return avg_ram_score

# Drive Benchmark
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
    avg_drive_score = round(avg_drive_score, 2)  # Rounding to two decimal places
    print("Average Drive Score:", avg_drive_score)
    return avg_drive_score

# Network Benchmark
def network_benchmark():
    print("\nNetwork Benchmark")
    print("-----------------")
    try:
        st = speedtest.Speedtest()
        st.download()
        st.upload()
        download_speed = st.results.download / 1e6  # Convert to Mbps
        upload_speed = st.results.upload / 1e6  # Convert to Mbps
        avg_network_score = round((download_speed + upload_speed) / 2, 2)
        print(f"Download Speed: {download_speed:.2f} Mbps")
        print(f"Upload Speed: {upload_speed:.2f} Mbps")
        print("Average Network Score:", avg_network_score)
        return avg_network_score
    except ImportError:
        print("Speedtest-cli is not installed. Skipping Network Benchmark...")
        return None

# Calculate Overall Score
def calculate_overall_score(cpu_score, gpu_score, ram_score, drive_score, network_score):
    scores = [cpu_score, ram_score, drive_score]
    if gpu_score is not None:
        scores.append(gpu_score)
    if network_score is not None:
        scores.append(network_score)
    overall_score = round(sum(scores) / len(scores), 2)
    print("\nOverall Score:", overall_score)
    return overall_score

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
    root.geometry("600x400")  # Doubled the window size

    # Set a custom font
    header_font = font.Font(root, family="Helvetica", size=14, weight="bold")
    label_font = font.Font(root, family="Helvetica", size=12)

    # Frame to contain all score labels
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(expand=True)

    # Header Label
    header_label = tk.Label(frame, text="System Benchmark Results", font=header_font)
    header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    # Define a function to create labels for each score
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

    root.mainloop()

if __name__ == "__main__":
    main()
