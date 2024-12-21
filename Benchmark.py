import subprocess
import json
import time
import numpy as np
import os
import pyopencl as cl
import pyopencl.array as cl_array
from tkinter import Tk, Frame, Label, Button
import pyautogui
from PIL import Image, ImageTk

# CPU Benchmark using matrix multiplication
def cpu_benchmark():
    print("CPU Benchmark")
    print("-------------")
    
    # Matrix multiplication parameters (smaller matrix for realistic scores)
    N = 200  # Reduced matrix size (200x200 matrix for realistic testing)
    A = np.random.rand(N, N)
    B = np.random.rand(N, N)
    
    # Perform matrix multiplication multiple times for more accurate results
    start_time = time.time()
    for _ in range(5):  # Repeat for more accuracy
        C = np.dot(A, B)  # Matrix multiplication
    elapsed_time = time.time() - start_time
    
    # Calculate GFLOPS (2 * N^3 operations per matrix multiplication)
    gflops = (2 * N**3 / 1e9) * 5 / elapsed_time  # 5 iterations for averaging
    print(f"CPU Performance: {gflops:.2f} GFLOPS")
    return gflops

# Network Benchmark using subprocess and speedtest-cli
def network_benchmark():
    print("\nNetwork Benchmark")
    print("-----------------")
    try:
        result = subprocess.run(["speedtest-cli", "--json"], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception("Speedtest failed.")
        
        output = json.loads(result.stdout)
        # Convert download/upload from bits per second to Mbit/s (divide by 1e6, then by 8 for bits to bytes)
        download_speed = output['download'] / 1e6  # Convert from bits/s to Mbit/s
        upload_speed = output['upload'] / 1e6  # Convert from bits/s to Mbit/s
        
        print(f"Download Speed: {download_speed:.2f} Mbit/s")
        print(f"Upload Speed: {upload_speed:.2f} Mbit/s")
        
        return {"Download Mbit/s": download_speed, "Upload Mbit/s": upload_speed}
    
    except Exception as e:
        print(f"Error during network benchmark: {e}")
        return None

# GPU Benchmark in GFLOPS (using more complex task)
def gpu_benchmark():
    print("\nGPU Benchmark")
    print("-------------")
    try:
        platforms = cl.get_platforms()
        device = platforms[0].get_devices()[0]  # Use first GPU device
        ctx = cl.Context([device])
        queue = cl.CommandQueue(ctx)

        # Use a more complex GPU operation (e.g., matrix multiplication)
        N = 200  # Reduced matrix size for realistic benchmarks (200x200 matrix)
        A = np.random.rand(N, N).astype(np.float32)
        B = np.random.rand(N, N).astype(np.float32)
        C = np.empty_like(A)

        mf = cl.mem_flags
        a_gpu = cl_array.to_device(queue, A)
        b_gpu = cl_array.to_device(queue, B)
        c_gpu = cl_array.to_device(queue, C)

        prg = cl.Program(ctx, """
        __kernel void matmul(__global float* a, __global float* b, __global float* c, int N) {
            int i = get_global_id(0);
            int j = get_global_id(1);
            float sum = 0;
            for (int k = 0; k < N; k++) {
                sum += a[i * N + k] * b[k * N + j];
            }
            c[i * N + j] = sum;
        }
        """).build()

        start = time.time()
        prg.matmul(queue, (N, N), None, a_gpu.data, b_gpu.data, c_gpu.data, np.int32(N))
        queue.finish()
        elapsed_time = time.time() - start
        gflops = (2 * N**3 / 1e9) / elapsed_time  # Adjust for matrix multiplication (2 * N^3 ops)
        print(f"GPU Performance: {gflops:.2f} GFLOPS")
        return gflops

    except Exception as e:
        print(f"Error during GPU benchmark: {e}")
        return None

# Drive Benchmark in MB/s
def drive_benchmark():
    print("\nDrive Benchmark")
    print("---------------")
    file_size_mb = 500  # 500 MB file
    file_path = "C:/temp/temp_drive_test.dat"
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

# Function to simulate Windows Key + Print Screen (take a screenshot)
def take_screenshot():
    pyautogui.hotkey('win', 'prtscr')
    print("Screenshot taken!")

# Main function for testing the updated benchmark
def main():
    cpu_score = cpu_benchmark()  # Perform CPU benchmark
    gpu_score = gpu_benchmark()  # Perform GPU benchmark
    ram_score = 30  # Placeholder for actual RAM benchmark result
    drive_scores = {"Write MB/s": 150, "Read MB/s": 200}  # Placeholder for actual drive test result
    network_scores = network_benchmark()  # Perform Network benchmark
    
    # Adjust if network data is missing
    if not network_scores:
        network_scores = {"Download Mbit/s": 0, "Upload Mbit/s": 0}
    
    overall_score = calculate_overall_score(cpu_score, gpu_score, ram_score, drive_scores, network_scores)

    # Create GUI to display results
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

    # Add Camera Icon Button to take screenshot
    camera_button = Button(root, text="\ud83d\udcf7", font=("Arial", 16), command=take_screenshot, borderwidth=0)
    camera_button.place(x=550, y=10)  # Position the button in the top-right corner

    root.mainloop()

# Running main
if __name__ == "__main__":
    main()
