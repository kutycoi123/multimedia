import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog




def readSampleRate(offset):
    return int.from_bytes(offset[24:28], byteorder='little')
def readBitsPerSample(offset):
    return int.from_bytes(offset[34:36], byteorder='little')
def readBlockAlign(offset):
    return int.from_bytes(offset[32:34], byteorder='little')

def readSamples(path):
    offset = bytearray()
    with open(path, "rb") as f:
        byte = f.read(1)
        while byte:
            offset += byte
            byte = f.read(1)
    sampleRate = readSampleRate(offset)
    bytesPerSample = readBitsPerSample(offset)/8
    blockAlign = readBlockAlign(offset)
    totalSamples = 0 # Calculate total number of samples
    data = []
    data_offset = 44
    while data_offset < len(offset):
        sample = offset[data_offset:(data_offset+blockAlign)]
        #data.append(sample)
        if (bytesPerSample >= 2): #16-bit sample, 2's-complement value -32768 to 32767
            data.append(int.from_bytes(sample, byteorder='little', signed=True))
        else: #8-bit sample, unsigned value 0 to 255
            data.append(int.from_bytes(sample, byteorder='little'))
        data_offset += blockAlign
        totalSamples+=1
    print(bytesPerSample)
    print(totalSamples)
    return data, totalSamples

if __name__ == "__main__":
    #path = sys.argv[1]
    #data = readSamples(path)
    # Init size
    WINDOW_SIZE = "1400x700"
    CANVAS_WIDTH = 1200
    CANVAS_HEIGHT = 600
    # Init root
    root = Tk()
    root.title("Q2")
    root.geometry(WINDOW_SIZE)
    # Event handler
    def chooseFile():
        global cv
        global lines
        root.filename = filedialog.askopenfilename(initialdir="/", title="Select wav file", filetypes=(("wav files", "*.wav"),))
        #cv.delete(ALL)
        data, totalSamples  = readSamples(root.filename)
        points = []
        print(lines[:10])
        for idx, e in enumerate(data):
            x = 0 + idx * (CANVAS_WIDTH / totalSamples)
            y = 300+(-e / 300)
            points.append((x,y))
        lenNewLines = len(points) - 1
        if lenNewLines < len(lines):
            for line in lines[lenNewLines:]:
                cv.delete(line)
        lines = lines[:lenNewLines]
            
        for i in range(lenNewLines):
            p1 = points[i]
            p2 = points[i+1]
            if i >= len(lines):
                newLine = cv.create_line(p1, p2, fill="blue")
                lines.append(newLine)
            else:
                cv.coords(lines[i], p1[0], p1[1], p2[0], p2[1])
            
    def reset():
        global cv
        global lines
        lines = []
        cv.delete(ALL)
    # Choose file button
    chooseFileBtn = Button(root, text="Choose file", command=chooseFile)
    chooseFileBtn.pack()

    # Reset button
    resetBtn = Button(root, text="Reset", command=reset)
    resetBtn.pack()
    # Canvas
    cv = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    cv.pack()
    lines = []
    #cv.create_line(0, CANVAS_HEIGHT/2, CANVAS_WIDTH, CANVAS_HEIGHT/2)
    #print(cv)
    #plt.figure(figsize=(10,5))
    #plt.plot(data, 'b-')
    #plt.show()
    #plt.savefig("test.svg")

    root.mainloop()
        

    
    
            
            
