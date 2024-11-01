import psutil
import time
import os
import tkinter as tk

# CPU Benchmark
def cpu_benchmark():
    print("CPU Benchmark")
    print("-------------")
    cpu_scores = []
    print("CPU Usage: ")
    for i in range(5):
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        print(cpu_percent)
        cpu_scores.append(sum(cpu_percent) / len(cpu_percent))
    avg_cpu_score = sum(cpu_scores) / len(cpu_scores)
    avg_cpu_score = round(avg_cpu_score, 2)  # Rounding to two decimal places
    print("Average CPU Score:", avg_cpu_score)
    return avg_cpu_score

# GPU Benchmark
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
                    gpu_score = N / elapsed
                    # Round the GPU benchmark score to the first two figures
                    rounded_gpu_score = round(gpu_score / 10000000)  # Rounding to first two figures
                    print("GPU Benchmark Score:", rounded_gpu_score)
                    return rounded_gpu_score
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

# Calculate Overall Score
def calculate_overall_score(cpu_score, gpu_score, ram_score, drive_score):
    if gpu_score is None:
        overall_score = (cpu_score + ram_score + drive_score) / 3
    else:
        overall_score = (cpu_score + gpu_score + ram_score + drive_score) / 4
    overall_score = round(overall_score, 2)  # Rounding to two decimal places
    print("\nOverall Score:", overall_score)
    return overall_score

# Main function
def main():
    cpu_score = cpu_benchmark()
    gpu_score = gpu_benchmark()
    ram_score = ram_benchmark()
    drive_score = drive_benchmark()
    overall_score = calculate_overall_score(cpu_score, gpu_score, ram_score, drive_score)

    # Create GUI window
    root = tk.Tk()
    root.title("System Benchmark Results")

    # CPU Score
    cpu_label = tk.Label(root, text="CPU Score:")
    cpu_label.grid(row=0, column=0, sticky=tk.W)
    cpu_score_label = tk.Label(root, text=f"{cpu_score:.2f}")
    cpu_score_label.grid(row=0, column=1, sticky=tk.W)

    # GPU Score
    gpu_label = tk.Label(root, text="GPU Score:")
    gpu_label.grid(row=1, column=0, sticky=tk.W)
    gpu_score_label = tk.Label(root, text=f"{gpu_score:.2f}" if gpu_score else "N/A")
    gpu_score_label.grid(row=1, column=1, sticky=tk.W)

    # RAM Score
    ram_label = tk.Label(root, text="RAM Score:")
    ram_label.grid(row=2, column=0, sticky=tk.W)
    ram_score_label = tk.Label(root, text=f"{ram_score:.2f}")
    ram_score_label.grid(row=2, column=1, sticky=tk.W)

    # Drive Score
    drive_label = tk.Label(root, text="Drive Score:")
    drive_label.grid(row=3, column=0, sticky=tk.W)
    drive_score_label = tk.Label(root, text=f"{drive_score:.2f}")
    drive_score_label.grid(row=3, column=1, sticky=tk.W)

    # Overall Score
    overall_label = tk.Label(root, text="Overall Score:")
    overall_label.grid(row=4, column=0, sticky=tk.W)
    overall_score_label = tk.Label(root, text=f"{overall_score:.2f}")
    overall_score_label.grid(row=4, column=1, sticky=tk.W)

    root.mainloop()

if __name__ == "__main__":
    main()
