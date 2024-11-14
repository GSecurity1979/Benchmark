import psutil
import time
import os
import tkinter as tk
from tkinter import font

# (All benchmark functions remain the same as in the previous code)

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
    root.geometry("600x400")  # Doubled the window size for better readability

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
