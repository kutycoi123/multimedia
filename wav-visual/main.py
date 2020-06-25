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
    maxValue = -(2**16) 
    maxAbsValue = 0
    data = []
    data_offset = 44
    while data_offset < len(offset):
        sample = offset[data_offset:(data_offset+blockAlign)]
        sampleVal = 0
        if (bytesPerSample >= 2): #16-bit sample, 2's-complement value -32768 to 32767
            sampleVal = int.from_bytes(sample, byteorder='little', signed=True)
        else: #8-bit sample, unsigned value 0 to 255
            sampleVal = int.from_bytes(sample, byteorder='little')
        if sampleVal > maxValue:
            maxValue = sampleVal
        if abs(sampleVal) > maxAbsValue:
            maxAbsValue = abs(sampleVal)
        data.append(sampleVal)
        data_offset += blockAlign
        totalSamples+=1
    
    return data, totalSamples, maxValue, maxAbsValue

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
        global totalSamplesLbl, maxValueLbl, maxAbsValueLbl
        root.filename = filedialog.askopenfilename(initialdir="/", title="Select wav file", filetypes=(("wav files", "*.wav"),))
        data, totalSamples, maxValue, maxAbsValue  = readSamples(root.filename)
        totalSamplesLbl.set("Total number of samples: " + str(totalSamples))
        maxValueLbl.set("Maximum value among samples: " + str(maxValue))
        maxAbsValueLbl.set("Maximum absolute value among samples: " + str(maxAbsValue))
        points = []
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
        cv.create_line(0, CANVAS_HEIGHT/2, CANVAS_WIDTH, CANVAS_HEIGHT/2, fill="white")
            
    def reset():
        global cv
        global lines
        global totalSamplesLbl, maxValueLbl, maxAbsValueLbl
        totalSamplesLbl.set("Total number of samples: ")
        maxValueLbl.set("Maximum value among samples: ")
        maxAbsValueLbl.set("Maximum absolute value among samples: ")
        lines = []
        cv.delete(ALL)
    # Choose file button
    chooseFileBtn = Button(root, text="Choose file", command=chooseFile)
    chooseFileBtn.pack()
    
    # Reset button
    resetBtn = Button(root, text="Reset", command=reset)
    resetBtn.pack()
    
    # Label
    totalSamplesLbl = StringVar()
    totalSamplesLbl.set("Total number of samples:")
    Label(root, textvariable=totalSamplesLbl, anchor='w').pack()
    #totalSamplesLbl.pack()
    maxValueLbl = StringVar()
    maxValueLbl.set("Maximum value among samples:")
    Label(root, textvariable=maxValueLbl).pack()
    #maxValueLbl.pack()
    maxAbsValueLbl = StringVar()
    maxAbsValueLbl.set("Maximum absolute value among samples:")
    Label(root, textvariable=maxAbsValueLbl).pack()
    #maxAbsValueLbl.pack()
    
    # Canvas
    cv = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    cv.pack()
    lines = []

    root.mainloop()
        

    
    
            
            
