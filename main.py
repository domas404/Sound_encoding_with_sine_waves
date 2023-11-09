import tkinter as tk
from tkinter import filedialog
import soundfile as sf
import numpy as np
import os
def writeToFile(data, channels):
    file_path = "compressed_audio.txt"
    
    if channels == 1:
        with open(file_path, "w") as file:
            for i in range(0,len(data)):
                file.write(str(data[i][0]) + ", " +str(data[i][1]) + ";")
    else:
        with open(file_path, "w") as file:
            for i in range(0,len(data)): 
                for j in range(0,len(data[i])):
                    file.write(str(data[i][j][0]) + ", " +str(data[i][j][1]) + ";")
                file.write(str("\n"))
def writeToBinaryFile(channels,data):
    array = np.array(data)
    print(array)
    array = array.tobytes()
    file_path = "compressed_audio.bin"
    if channels == 1:
        with open(file_path, 'wb') as file:
            file.write(array)
    else:
        with open(file_path, "w") as file:
            for i in range(0,len(data)): 
                for j in range(0,len(data[i])):
                    file.write(str(data[i][j][0]) + ", " +str(data[i][j][1]) + ";")
                file.write(str("\n"))
    
def calculateFileSizeDifferance(fileA, fileB):
    #check if files exist
    if os.path.exists(fileA) and os.path.exists(fileB):
        #get file sizes
        fileA_size = os.path.getsize(fileA)
        fileB_size = os.path.getsize(fileB)
        print(fileA_size)
        print(fileB_size)
        if fileA_size > fileB_size:
            temp = fileA_size
            fileA_size = fileB_size
            fileB_size = temp
        #calculate differences
        print(f"{os.path.basename(fileA)} occupies {'{0:.2f}'.format((1 - fileA_size/fileB_size)*100)} % ({fileB_size - fileA_size} bytes) less than {os.path.basename(fileB)}.")
    else:
        print(f"The file {fileA} and/or file {fileB} does not exist.")
    
def compress_data(audio_data):
    max_amplitude = float('-inf')
    min_amplitude = float('inf')
    count = 0
    compressed_audio_data = []
    current_sign = True if audio_data[0] >= 0 else False 
    previous_sign = current_sign
    for i in range(0,len(audio_data)):
        #calculating samples
        count += 1
        #searching for max positive amplitude
        if current_sign and audio_data[i] >= max_amplitude:
            max_amplitude = audio_data[i]
        #searching for max negative amplitude
        elif not current_sign and audio_data[i] < min_amplitude:
            min_amplitude = audio_data[i]
        #updating the sign
        current_sign = True if audio_data[i] >= 0 else False
        #passed zero in the x axis
        if current_sign != previous_sign:
            compressed_audio_data.append([max_amplitude if previous_sign else min_amplitude,count])
            previous_sign = current_sign
            max_amplitude = float('-inf')
            min_amplitude = float('inf')
            count = 0
    return compressed_audio_data
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select a file")

    if file_path:

        audio_data, sample_rate = sf.read(file_path)
        info = sf.info(file_path)
        bits = int(info.subtype.split("_")[1])
        file_path = os.path.basename(file_path)
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
        else:
            for i in range(0,audio_data.shape[1]):
                compressed_data.append(compress_data(audio_data[:,i]))
        writeToFile(compressed_data,info.channels)
        writeToBinaryFile(info.channels,compressed_data)
        calculateFileSizeDifferance(os.path.abspath("compressed_audio.txt"),os.path.abspath(file_path))
    else:
        print("No file selected")
