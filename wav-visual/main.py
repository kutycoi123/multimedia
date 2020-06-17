import sys
import matplotlib.pyplot as plt
import wave




def readSampleRate(offset):
    return int.from_bytes(offset[24:28], byteorder='little')
def readBitsPerSample(bytes):
    return int.from_bytes(offset[34:36], byteorder='little')
def readBlockAlign(offset):
    return int.from_bytes(offset[32:34], byteorder='little')
        

if __name__ == "__main__":
    path = sys.argv[1]
    obj = wave.open(path)
    offset = b''
    with open(path, "rb") as f:
        byte = f.read(1)
        while byte:
            offset += byte
            byte = f.read(1)
    sampleRate = readSampleRate(offset)
    bytePerSample = readBitsPerSample(offset)/8
    blockAlign = readBlockAlign(offset)
    
    totalSamples = 0 # Calculate total number of samples
    data = []
    data_offset = 44
    while data_offset < len(offset):
        sample = offset[data_offset:(data_offset+blockAlign)]
        #data.append(sample)
        if (bytePerSample == 2): #16-bit sample, 2's-complement value -32768 to 32767
            data.append(int.from_bytes(sample, byteorder='little', signed=True))
        else: #8-bit sample, unsigned value 0 to 255
            data.append(int.from_bytes(sample, byteorder='little'))
        data_offset += blockAlign
    plt.figure(figsize=(10,5))
    plt.plot(data)
    plt.show()
    obj.close()
        
        

    
    
            
            
