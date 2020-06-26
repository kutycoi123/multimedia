#import os
from tkinter import *
from tkinter import filedialog
from math import ceil


def bytesToInt(bytes, byteorder='little', signed=False):
    """ Convert bytes to integer"""
    return int.from_bytes(bytes, byteorder=byteorder, signed=signed)
def myround(value, lowerbound, higherbound):
    """ Round value back to the interval between [lowerbound, higherbound]"""
    if value < lowerbound:
        return lowerbound
    if value > higherbound:
        return higherbound
    return value
class Bmp24BitImage():
    def __init__(self, path):
        if (not path.endswith('.bmp')):
            raise Exception("File must be bmp")
        self.img = self.__readImg(path)
        self.fileSize = bytesToInt(self.img[2:6])
        self.width = bytesToInt(self.img[18:22], signed=True)
        self.height = bytesToInt(self.img[22:26], signed=True)
        self.bitsPerPixel = bytesToInt(self.img[28:30])
        self.dataOffset = bytesToInt(self.img[10:14])
        self.imgSize = bytesToInt(self.img[34:38])
        self.bytesPerPixel = self.bitsPerPixel // 8
        self.bytesPerRow = ceil((self.width * self.bytesPerPixel) / 4) * 4
        self.extraBytesPerRow = self.bytesPerRow - (self.width * self.bytesPerPixel)
        
    def original(self):
        pixels = []
        i = self.dataOffset
        while i < len(self.img):
            rowPixels = []
            for k in range(i, i + self.width * self.bytesPerPixel, self.bytesPerPixel):
                b = self.img[k]
                g = self.img[k+1]
                r = self.img[k+2]
                rowPixels.append((r,g,b))
            i += self.bytesPerRow
            pixels.append(rowPixels)
        return pixels
        
    def grayscale(self):
        """Return grayscale pixels"""
        pixels = []
        i = self.dataOffset
        while i < len(self.img):
            row = []
            for k in range(i, i + self.width * self.bytesPerPixel, self.bytesPerPixel):
                b = self.img[k]
                g = self.img[k+1]
                r = self.img[k+2]
                c = int(0.30*r + 0.59*g + 0.11*b)
                #grayscale[k] = grayscale[k+1] = grayscale[k+2] = c
                row.append((c,c,c))
            pixels.append(row)
            i += self.bytesPerRow
        return pixels

    def darken(self):
        """ Return darker pixels """
        pixels = []
        i = self.dataOffset
        while i < len(self.img):
            row = []
            for k in range(i, i + self.width * self.bytesPerPixel, self.bytesPerPixel):
                b = int(self.img[k]*0.5)
                g = int(self.img[k+1]*0.5)
                r = int(self.img[k+2]*0.5)
                row.append((r,g,b))
            pixels.append(row)
            i += self.bytesPerRow
        return pixels

    def vivid(self):
        """ Return vivid pixels """
        pixels = []
        i = self.dataOffset
        alpha = 2.2
        beta = 50
        while i < len(self.img):
            row = []
            for k in range(i, i + self.width * self.bytesPerPixel, self.bytesPerPixel):
                b = myround(int(alpha*self.img[k] + beta), 0, 255)
                g = myround(int(alpha*self.img[k+1] + beta), 0, 255)
                r = myround(int(alpha*self.img[k+2] + beta), 0, 255)
                row.append((r,g,b))
            pixels.append(row)
            i += self.bytesPerRow
        return pixels
        
    def __readImg(self, path):
        img = bytearray()
        with open(path, "rb") as f:
            byte = f.read(1)
            while byte:
                img += byte
                byte = f.read(1)
        return img



if __name__ == "__main__":
    # Init root
    root = Tk()
    root.title("Q3")
    root.geometry("1000x700")
    # Init global variables
    original = grayscale = dark = vividP = [] # array of pixel color: [(r,g,b)]
    CANVAS_WIDTH = 900
    CANVAS_HEIGHT = 700

    def onExit():
        root.quit()
        
    def drawPixels(pixels):
        global cv, cvImg
        global CANVAS_WIDTH, CANVAS_HEIGHT
        cv.delete(ALL) # Clean up canvas
        # Reset image
        cvImg = PhotoImage(width=CANVAS_WIDTH,height=CANVAS_HEIGHT)
        cv.create_image((CANVAS_WIDTH//2, CANVAS_HEIGHT//2), image=cvImg, state="normal")
        h = len(pixels) # image height
        w = len(pixels[0]) # image width
        colAlign = CANVAS_WIDTH // 2 - w // 2 # Align image to be center
        # Draw each pixel 
        for row in range(h):
            for col in range(w):
                color = "#%02x%02x%02x" % pixels[row][col] # Convert (r,g,b) to hexa
                xx, yy = colAlign+col, row
                cvImg.put(color, (xx,yy))

    def imgSelect():
        global label, cv, cvImg
        global original, grayscale, dark, vivid
        # Open dialog to choose file
        root.filename = filedialog.askopenfilename(initialdir=".",title="Select an image",filetypes=(("bmp files", "*.bmp"),))
        if root.filename:
            # Process image byte by byte
            rawImg = Bmp24BitImage(root.filename)
            original = rawImg.original()
            grayscale = rawImg.grayscale()
            dark = rawImg.darken()
            vivid = rawImg.vivid()

            # Reverse pixels because the way bmp format stores pixels is from last row to the beginning row of image
            original.reverse()
            grayscale.reverse()
            dark.reverse()
            vivid.reverse()

            # Draw original image
            drawPixels(original)
            
    
    def selectProcessedImg(pixels):
        drawPixels(pixels)

    # Buttons
    fileBtn = Button(root, text="Select BMP image", command=imgSelect)
    originalBtn = Button(root, text="Original image", command=lambda: selectProcessedImg(original))
    grayscaleBtn = Button(root, text="Make grayscale", command=lambda: selectProcessedImg(grayscale))
    darkBtn = Button(root, text="Make darker", command=lambda: selectProcessedImg(dark))
    vividBtn = Button(root, text="Make vivid", command=lambda: selectProcessedImg(vivid))

    # Display buttons
    fileBtn.pack()
    originalBtn.pack()
    grayscaleBtn.pack()
    darkBtn.pack()
    vividBtn.pack()

    # Canvas to draw image byte by byte
    cv = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    cv.pack()
    
    root.protocol("WM_DELETE_WINDOW", onExit)
    root.mainloop()
    

    
