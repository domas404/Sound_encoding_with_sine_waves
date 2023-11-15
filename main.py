import tkinter as tk
from tkinter import filedialog
import soundfile as sf
import numpy as np
import os

RESULTS_FILE_PATH = "compressed_audio.txt"

def write_to_txt_file(data):
    with open(RESULTS_FILE_PATH, "a") as file:
        for i in range(0,len(data)):
            file.write(str(data[i][0])+" "+str(data[i][1]) + ";")
        file.write("\n")
          
def delete_old_results_file():
    if os.path.exists(RESULTS_FILE_PATH):
        os.remove(RESULTS_FILE_PATH)

def calculate_file_size_differance(fileA, fileB):
    #check if files exist
    if os.path.exists(fileA) and os.path.exists(fileB):
        #get file sizes
        fileA_size = os.path.getsize(fileA)
        fileB_size = os.path.getsize(fileB)
        if fileA_size > fileB_size:
            temp = fileA_size
            fileA_size = fileB_size
            fileB_size = temp
        #compare file sizes
        ratio = int(fileB_size/fileA_size)
        print(f"{os.path.basename(fileA)} occupies {fileA_size} bytes.")
        print(f"{os.path.basename(fileB)} occupies {fileB_size} bytes.")
        print(f"{os.path.basename(fileA)} occupies {ratio} time{'s' if ratio != 1 else ''} less disk space than {os.path.basename(fileB)}.")
    else:
        print(f"The file {fileA} and/or file {fileB} does not exist.")
    
def compress_data(audio_data):
    max_amplitude = float('-inf')
    min_amplitude = float('inf')
    count = 0
    compressed_audio_data = []
    current_sign = audio_data[0] >= 0
    previous_sign = current_sign
    for value in audio_data:
        #calculating samples
        count += 1
        #searching for max positive amplitude
        if current_sign and value >= max_amplitude:
            max_amplitude = value
        #searching for max negative amplitude
        elif value < min_amplitude:
            min_amplitude = value
        #updating the sign
        current_sign = value >= 0
        #passed zero in the x axis
        if current_sign != previous_sign:
            # 1/(count*2/sample_rate) T = count/sample_rate, F = 1/T,
            # count*2 because we are calculating the frequency for the whole sine wave
            amplitude = max_amplitude if previous_sign else min_amplitude
            frequency = '{:.2f}'.format(sample_rate/(2*count))
            compressed_audio_data.append([amplitude, frequency])
            previous_sign = current_sign
            max_amplitude = float('-inf')
            min_amplitude = float('inf')
            count = 0
    return compressed_audio_data
if __name__ == "__main__":
    delete_old_results_file()
    root = tk.Tk()
    root.withdraw()
    selected_file = filedialog.askopenfilename(title="Select a file")
    
    if selected_file:
        audio_data, sample_rate = sf.read(selected_file)
        info = sf.info(selected_file)
        bits = int(info.subtype.split("_")[1])
        selected_file = os.path.basename(selected_file)
        audio_data = np.multiply(audio_data, 2**(bits-1))

        label = ""
        if info.duration < 2:
                time = [i / sample_rate * 1000 for i in range(len(audio_data))]
                label = 'Time (ms)'
        elif info.duration < 60:
            time = [i / sample_rate for i in range(len(audio_data))]
            label = 'Time (s)'
        else:
            time = [i / sample_rate / 60 for i in range(len(audio_data))]
            label = 'Time (min)'
       
        compressed_data = []
        if info.channels == 1:
            compressed_data = compress_data(audio_data)
            write_to_txt_file(compressed_data)
        else:
            for i in range(0,audio_data.shape[1]):
                compressed_data = compress_data(audio_data[:,i])
                write_to_txt_file(compressed_data)
        calculate_file_size_differance(os.path.abspath(RESULTS_FILE_PATH),os.path.abspath(selected_file))
    else:
        print("No file selected")
