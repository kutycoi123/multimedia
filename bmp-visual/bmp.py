import os
from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
from math import ceil


def bytesToInt(bytes, byteorder='little', signed=False):
    return int.from_bytes(bytes, byteorder=byteorder, signed=signed)
def myround(value, lowerbound, higherbound):
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
        
    def grayscale(self):
        grayscale = self.img[:]
        i = self.dataOffset
        while i < len(self.img):
            for k in range(i, i + self.width * self.bytesPerPixel, self.bytesPerPixel):
                r = self.img[k]
                g = self.img[k+1]
                b = self.img[k+2]
                c = int(0.30*r + 0.59*g + 0.11*b)
                grayscale[k] = grayscale[k+1] = grayscale[k+2] = c
            i += self.bytesPerRow
        return grayscale

    def darken(self):
        """ Darker 24-bit bmp image """
        dark = self.img[:]
        i = self.dataOffset
        while i < len(self.img):
            for k in range(i, i + self.width * self.bytesPerPixel, self.bytesPerPixel):
                dark[k] = int(self.img[k]*0.5)
                dark[k+1] = int(self.img[k+1]*0.5)
                dark[k+2] = int(self.img[k+2]*0.5)

            i += self.bytesPerRow
        return dark

    def vivid(self):
        """ Make image more vivid"""
        vivid = self.img[:]
        i = self.dataOffset
        a = 2.2
        b = 50
        while i < len(self.img):
            for k in range(i, i + self.width * self.bytesPerPixel, self.bytesPerPixel):
                vivid[k] = myround(int(a*self.img[k] + b), 0, 255)
                vivid[k+1] = myround(int(a*self.img[k+1] + b), 0, 255)
                vivid[k+2] = myround(int(a*self.img[k+2] + b), 0, 255)
            i += self.bytesPerRow
        return vivid
        
    def __readImg(self, path):
        img = bytearray()
        with open(path, "rb") as f:
            byte = f.read(1)
            while byte:
                img += byte
                byte = f.read(1)
        return img

    def getAllPixels(self):
        pixels = []
        i = self.dataOffset
        while i < len(self.img):
            rowPixels = []
            for k in range(i, i + self.width * self.bytesPerPixel, self.bytesPerPixel):
                r = self.img[k]
                g = self.img[k+1]
                b = self.img[k+2]
                rowPixels.append((b,g,r))
            i += self.bytesPerRow
            pixels.append(rowPixels)
        #print(pixels[:10])
        return pixels


if __name__ == "__main__":
    # Init root
    root = Tk()
    root.title("Q3")
    root.geometry("800x600")
    # Init global variables
    label = None
    grayscalePath = "grayscalecmpt365p1.bmp"
    darkPath = "darkcmpt365p1.bmp"
    vividPath = "vividcmpt365p1.bmp"
    processedImg = None

    def cleanFiles():
        global grayscalePath, darkPath, vividPath
        files = [grayscalePath, darkPath, vividPath]
        for path in files:
            if os.path.exists(path):
                os.remove(path)
    def onExit():
        # Clean files
        cleanFiles()
        root.quit()
        
    def imgSelect():
        global label, cv
        global grayscale, dark, vivid, original
        global grayscalePath, darkPath, vivid
        global processedImg
        cleanFiles()
        processedImg = None
        cv.delete(ALL)
        if label:
            label.destroy()
        root.filename = filedialog.askopenfilename(initialdir="/",title="Select an image",filetypes=(("bmp files", "*.bmp"),))
        if root.filename:
            rawImg = Bmp24BitImage(root.filename)
            grayscaleRaw = rawImg.grayscale()
            darkRaw = rawImg.darken()
            vividRaw = rawImg.vivid()

            with open(grayscalePath, 'wb') as f:
                f.write(grayscaleRaw)
            with open(darkPath, 'wb') as f:
                f.write(darkRaw)
            with open(vividPath, 'wb') as f:
                f.write(vividRaw)
            
            #original = ImageTk.PhotoImage(Image.open(root.filename))
            #label = Label(image=original, width=700)
            #label.pack()
            pixels = rawImg.getAllPixels()
            print(len(pixels))
            print(len(pixels[0]))
            y = 0
            for row in range(len(pixels)-1, -1, -1):
                for col in range(len(pixels[0])):
                    color = "#%02x%02x%02x" % pixels[row][col]
                    #cv.create_rectangle((100+x, 50+col)*2, outline="", fill=color)
                    xx, yy = 100+col, 50+y
                    cv.create_line(xx, yy, xx+1,yy, fill=color)
                y += 1
        
    def selectProcessedImg(path):
        global label, cv
        global processedImg
        cv.delete(ALL)
        if label:
            label.destroy()
        try:
            processedImg = ImageTk.PhotoImage(Image.open(path))
        except:
            pass
        if processedImg:
            label = Label(image=processedImg, width=700)
            label.pack()

                
    fileBtn = Button(root, text="Select BMP image", command=imgSelect)
    fileBtn.pack()

    originalBtn = Button(root, text="Original image", command=lambda: selectProcessedImg(root.filename))
    originalBtn.pack()
    grayscaleBtn = Button(root, text="Make grayscale", command=lambda: selectProcessedImg(grayscalePath))
    grayscaleBtn.pack()
    darkBtn = Button(root, text="Make darker", command=lambda: selectProcessedImg(darkPath))
    darkBtn.pack()
    vividBtn = Button(root, text="Make vivid", command=lambda: selectProcessedImg(vividPath))
    vividBtn.pack()

    
    cv = Canvas(root, width=800, height=800)
    cv.pack()
    #for x in range(100):
    #    cv.create_rectangle((x,100)*2, outline="",fill="red")
    root.protocol("WM_DELETE_WINDOW", onExit)
    root.mainloop()
    

    
