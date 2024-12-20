# System Benchmark Script with Realistic Metrics

import psutil
import time
import os
import subprocess
import numpy as np
from tkinter import Tk, Frame, Label, Button
from PIL import Image, ImageTk
import pyautogui

# CPU Benchmark in GFLOPS
def cpu_benchmark():
    print("CPU Benchmark")
    print("-------------")
    num_operations = 10**8  # 100 million operations for a realistic test
    x = np.random.rand(num_operations)
    start_time = time.time()
    for _ in range(10):
        x = x * 1.0001 / 1.0001  # Perform operations
    elapsed_time = time.time() - start_time
    gflops = (num_operations * 10 / 1e9) / elapsed_time  # Adjust for 10 iterations
    print(f"CPU Performance: {gflops:.2f} GFLOPS")
    return gflops

# GPU Benchmark in GFLOPS
def gpu_benchmark():
    print("\nGPU Benchmark")
    print("-------------")
    try:
        import pyopencl as cl
        import pyopencl.array as cl_array

        platforms = cl.get_platforms()
        device = platforms[0].get_devices()[0]  # Use first GPU device
        ctx = cl.Context([device])
        queue = cl.CommandQueue(ctx)

        # GPU benchmark parameters
        N = 10**7
        mf = cl.mem_flags
        a_gpu = cl_array.to_device(queue, np.random.rand(N).astype(np.float32))
        b_gpu = cl_array.empty_like(a_gpu)
        
        prg = cl.Program(ctx, """
        __kernel void compute(__global float* a, __global float* b) {
            int gid = get_global_id(0);
            b[gid] = a[gid] * 2.0f;
        }
        """).build()

        start = time.time()
        prg.compute(queue, (N,), None, a_gpu.data, b_gpu.data)
        queue.finish()
        elapsed_time = time.time() - start
        gflops = (N / 1e9) / elapsed_time
        print(f"GPU Performance: {gflops:.2f} GFLOPS")
        return gflops

    except ImportError:
        print("PyOpenCL not installed. GPU Benchmark skipped.")
        return None
    except Exception as e:
        print(f"Error during GPU benchmark: {e}")
        return None

# RAM Benchmark in GB/s
def ram_benchmark():
    print("\nRAM Benchmark")
    print("-------------")
    array_size = 10**7  # 10 million floats (~40 MB)
    a = np.random.rand(array_size).astype(np.float32)
    b = np.empty_like(a)

    start_time = time.time()
    for _ in range(100):
        np.copyto(b, a)
    elapsed_time = time.time() - start_time

    total_data = (array_size * 4 * 100) / (1024**3)  # Convert bytes to GB
    gbps = total_data / elapsed_time
    print(f"RAM Bandwidth: {gbps:.2f} GB/s")
    return gbps

# Drive Benchmark in MB/s
def drive_benchmark():
    print("\nDrive Benchmark")
    print("---------------")
    file_size_mb = 500  # 500 MB file
    file_path = "temp_drive_test.dat"
    data = os.urandom(file_size_mb * 1024 * 1024)

    # Write speed
    start_time = time.time()
    with open(file_path, "wb") as f:
        f.write(data)
    write_time = time.time() - start_time
    write_speed = file_size_mb / write_time

    # Read speed
    start_time = time.time()
    with open(file_path, "rb") as f:
        f.read()
    read_time = time.time() - start_time
    read_speed = file_size_mb / read_time

    os.remove(file_path)
    print(f"Write Speed: {write_speed:.2f} MB/s")
    print(f"Read Speed: {read_speed:.2f} MB/s")
    return {"Write MB/s": write_speed, "Read MB/s": read_speed}

# Network Benchmark in Mbit/s
def network_benchmark():
    print("\nNetwork Benchmark")
    print("-----------------")
    try:
        result = subprocess.run(["speedtest", "--format=json"], capture_output=True, text=True)
        import json
        output = json.loads(result.stdout)
        download_speed = output['download']['bandwidth'] * 8 / 1e6  # Convert bytes/s to Mbit/s
        upload_speed = output['upload']['bandwidth'] * 8 / 1e6
        print(f"Download Speed: {download_speed:.2f} Mbit/s")
        print(f"Upload Speed: {upload_speed:.2f} Mbit/s")
        return {"Download Mbit/s": download_speed, "Upload Mbit/s": upload_speed}
    except Exception as e:
        print(f"Error during network benchmark: {e}")
        return None

# Overall Score Calculation
def calculate_overall_score(cpu_score, gpu_score, ram_score, drive_scores, network_scores):
    scores = [cpu_score, ram_score]
    if gpu_score is not None:
        scores.append(gpu_score)
    if network_scores:
        scores.append((network_scores["Download Mbit/s"] + network_scores["Upload Mbit/s"]) / 2)
    scores.append((drive_scores["Write MB/s"] + drive_scores["Read MB/s"]) / 2)
    overall_score = round(sum(scores) / len(scores), 2)
    print("\nOverall Score:", overall_score)
    return overall_score

# Function to simulate Windows Key + Print Screen
def take_screenshot():
    pyautogui.hotkey('win', 'prtscr')
    print("Screenshot taken!")

# Main GUI Display
def main():
    cpu_score = cpu_benchmark()
    gpu_score = gpu_benchmark()
    ram_score = ram_benchmark()
    drive_scores = drive_benchmark()
    network_scores = network_benchmark()
    overall_score = calculate_overall_score(cpu_score, gpu_score, ram_score, drive_scores, network_scores)

    # Create GUI
    root = Tk()
    root.title("System Benchmark Results")
    root.geometry("600x400")

    frame = Frame(root, padx=20, pady=20)
    frame.pack(expand=True)

    # Display Results
    Label(frame, text=f"CPU: {cpu_score:.2f} GFLOPS").pack()
    Label(frame, text=f"GPU: {gpu_score:.2f} GFLOPS" if gpu_score else "GPU: N/A").pack()
    Label(frame, text=f"RAM Speed: {ram_score:.2f} GB/s").pack()
    Label(frame, text=f"Drive Write: {drive_scores['Write MB/s']:.2f} MB/s").pack()
    Label(frame, text=f"Drive Read: {drive_scores['Read MB/s']:.2f} MB/s").pack()
    if network_scores:
        Label(frame, text=f"Download: {network_scores['Download Mbit/s']:.2f} Mbit/s").pack()
        Label(frame, text=f"Upload: {network_scores['Upload Mbit/s']:.2f} Mbit/s").pack()
    Label(frame, text=f"Overall Score: {overall_score:.2f}").pack()

    # Add Camera Icon Button
    camera_button = Button(root, text="\ud83d\udcf7", font=("Arial", 16), command=take_screenshot, borderwidth=0)
    camera_button.place(x=550, y=10)

    root.mainloop()

if __name__ == "__main__":
    main()
