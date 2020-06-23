import sys
from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
from math import ceil


def bytesToInt(bytes, byteorder='little', signed=False):
    return int.from_bytes(bytes, byteorder=byteorder, signed=signed)
def clip(value, lowerbound, higherbound):
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
        
    def grayscale_24bit(self):
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
        
    def grayscale(self):
        """ Convert 24-bit bmp image to a grayscale image"""
        grayscale = self.img[:self.dataOffset]
        grayscale[2:6] = (0).to_bytes(4, byteorder='little') # file size
        grayscale[28:30] = (8).to_bytes(2, byteorder='little') # bit per pixel
        grayscale[46:50] = (256).to_bytes(4, byteorder='little') # color used
        # Construct color pallet or color table
        for i in range(256):
            grayscale += (i).to_bytes(1, byteorder='little') * 4
        
        i = self.dataOffset
        while i < len(self.img):
            for k in range(i, i + self.width * self.bytesPerPixel, self.bytesPerPixel): # loop through all bytes on a row, except for extra bytes for padding
                grayscale += (int(0.299 * self.img[k] + 0.587 * self.img[k+1] + 0.114 * self.img[k+2])).to_bytes(1, byteorder='little')
            if self.extraBytesPerRow > 0:
                grayscale += (0).to_bytes(self.extraBytesPerRow, byteorder='little') # for row padding 
            i += self.bytesPerRow
        newImgSize = self.height * (self.width + self.extraBytesPerRow) # We only used 1-byte for each grayscale pixel plus some extra bytes for row padding
        grayscale[34:38] = (newImgSize).to_bytes(4, byteorder='little') # Image size
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
                vivid[k] = clip(int(a*self.img[k] + b), 0, 255)
                vivid[k+1] = clip(int(a*self.img[k+1] + b), 0, 255)
                vivid[k+2] = clip(int(a*self.img[k+2] + b), 0, 255)
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
    


if __name__ == "__main__":
    
    #path = sys.argv[1]
    #img = Bmp24BitImage(path)
    #grayscale = img.grayscale()
    #with open("grayscale.bmp", 'wb') as f:
    #    f.write(grayscale)

    #dark = img.darken()
    #with open("dark.bmp", "wb") as f:
    #    f.write(dark)

    #vivid = img.vivid()
    #with open("vivid.bmp", "wb") as f:
    #    f.write(vivid)

    root = Tk()
    root.title("Q3")
    def onExit():
        # Clean files
        root.quit()
        
    label = None
        
    def imgSelect():
        global imgTkinter
        global label
        if label:
            label.destroy()
        root.filename = filedialog.askopenfilename(initialdir="/",title="Select an image",filetypes=(("bmp files", "*.bmp"),))
        rawImg = Bmp24BitImage(root.filename)
        grayscale = rawImg.grayscale_24bit()
        out = "grayscale.bmp"
        with open("grayscale.bmp", 'wb') as f:
            f.write(grayscale)
        #dark = rawImg.darken()
        #out = "dark.bmp"
        #with open(out, "wb") as f:
        #    f.write(dark)
        imgTkinter = ImageTk.PhotoImage(Image.open(out))
        label = Label(image=imgTkinter, width=700)
        label.pack()
            
    fileBtn = Button(root, text="Select BMP image", command=imgSelect)
    fileBtn.pack()

    root.protocol("WM_DELETE_WINDOW", onExit)
    root.mainloop()
    

    
