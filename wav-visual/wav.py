from tkinter import *
from tkinter import filedialog


def readSampleRate(offset):
    return int.from_bytes(offset[24:28], byteorder='little')
def readBitsPerSample(offset):
    return int.from_bytes(offset[34:36], byteorder='little')
def readBlockAlign(offset):
    return int.from_bytes(offset[32:34], byteorder='little')
def readSubchunk1Size(offset):
    return int.from_bytes(offset[16:20], byteorder='little')

def fadeIn(samples):
    """ Make samples faded in"""
    newSamples = []
    factor = 0
    step = 1 / len(samples)
    for samp in samples:
        newSamples.append(samp*factor)
        factor += step
    return newSamples

def fadeOut(samples):
    """Make samepls faded out, which means apply fade in in reverse order"""
    copy = samples[:]
    copy.reverse()
    fadedIn = fadeIn(copy)
    fadedIn.reverse() # reverse back to the original order
    return fadedIn

def readSamples(path):
    """ Main function to read wav file byte by byte
        Retuns: sample data, total number of samples, maximum sample value, maximum absolute sample value
    """
    offset = bytearray()
    # Read bmp file as binary
    with open(path, "rb") as f:
        byte = f.read(1)
        while byte:
            offset += byte
            byte = f.read(1)
    # Extract useful information from header
    sampleRate = readSampleRate(offset)
    bytesPerSample = readBitsPerSample(offset)/8
    blockAlign = readBlockAlign(offset)
    subchunk1Size = readSubchunk1Size(offset)
    
    totalSamples = 0 # Calculate total number of samples
    maxValue = -(2**16) # maxumum sample value
    maxAbsValue = 0 # maximum absolute value
    samples = [] 
    dataOffset = 20 + subchunk1Size + 8 # where samples data begin
    # Loop through samples data
    while dataOffset < len(offset):
        sample = offset[dataOffset:(dataOffset+blockAlign)]
        sampleVal = 0
        if (bytesPerSample >= 2): #16-bit sample, 2's-complement value -32768 to 32767
            sampleVal = int.from_bytes(sample, byteorder='little', signed=True)
        else: #8-bit sample, unsigned value 0 to 255
            sampleVal = int.from_bytes(sample, byteorder='little')
            
        if sampleVal > maxValue:
            maxValue = sampleVal
        if abs(sampleVal) > maxAbsValue:
            maxAbsValue = abs(sampleVal)
            
        samples.append(sampleVal)
        dataOffset += blockAlign
        totalSamples += 1
    # Fade in and fade out samples
    samplesLen = len(samples)
    samples[:samplesLen//2] = fadeIn(samples[:samplesLen//2]) # Fade in first half
    samples[samplesLen//2:] = fadeOut(samples[samplesLen//2:]) # Fade out another half
    return samples, totalSamples, maxValue, maxAbsValue


    
if __name__ == "__main__":

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
        # Choose file
        root.filename = filedialog.askopenfilename(initialdir="/", title="Select wav file", filetypes=(("wav files", "*.wav"),))
        # Extract sample data
        samples, totalSamples, maxValue, maxAbsValue  = readSamples(root.filename)
        # Update label
        totalSamplesLbl.set("Total number of samples: " + str(totalSamples))
        maxValueLbl.set("Maximum value among samples: " + str(maxValue))
        maxAbsValueLbl.set("Maximum absolute value among samples: " + str(maxAbsValue))
        # Prepare to draw waveform by scaling samples data to fit into canvas window
        points = []
        offset = CANVAS_HEIGHT / 2 # offset = 300
        for idx, e in enumerate(samples):
            x = 0 + idx * (CANVAS_WIDTH / totalSamples)
            y = offset+(-e / offset)
            points.append((x,y))
        # Reuse old lines instead of just removing all of them
        lenNewLines = len(points) - 1
        if lenNewLines < len(lines):
            for line in lines[lenNewLines:]:
                cv.delete(line)
        lines = lines[:lenNewLines]

        for i in range(lenNewLines):
            p1 = points[i]
            p2 = points[i+1]
            if i >= len(lines): # Draw new line
                newLine = cv.create_line(p1, p2, fill="blue")
                lines.append(newLine)
            else: # Update old line with new coordinate
                cv.coords(lines[i], p1[0], p1[1], p2[0], p2[1])
        # Create the base horizontal line
        cv.create_line(0, CANVAS_HEIGHT/2, CANVAS_WIDTH, CANVAS_HEIGHT/2, fill="white")
            
    def reset():
        global cv
        global lines
        global totalSamplesLbl, maxValueLbl, maxAbsValueLbl
        # Update labels
        totalSamplesLbl.set("Total number of samples: ")
        maxValueLbl.set("Maximum value among samples: ")
        maxAbsValueLbl.set("Maximum absolute value among samples: ")
        # Remove all lines
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
    
    maxValueLbl = StringVar()
    maxValueLbl.set("Maximum value among samples:")
    Label(root, textvariable=maxValueLbl).pack()

    maxAbsValueLbl = StringVar()
    maxAbsValueLbl.set("Maximum absolute value among samples:")
    Label(root, textvariable=maxAbsValueLbl).pack()

    
    # Canvas
    cv = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    cv.pack()
    lines = []

    root.mainloop()
        

    
    
            
            
