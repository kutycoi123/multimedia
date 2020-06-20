import sys
from math import ceil

def bytesToInt(bytes, byteorder='little', signed=False):
    return int.from_bytes(bytes, byteorder=byteorder, signed=signed)

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
                grayscale += (int(0.3 * self.img[k] + 0.59 * self.img[k+1] + 0.11 * self.img[k+2])).to_bytes(1, byteorder='little')
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
        
    def __readImg(self, path):
        img = bytearray()
        with open(path, "rb") as f:
            byte = f.read(1)
            while byte:
                img += byte
                byte = f.read(1)
        return img
    


if __name__ == "__main__":
    path = sys.argv[1]
    img = Bmp24BitImage(path)
    #grayscale = img.grayscale()
    #with open("grayscale.bmp", 'wb') as f:
    #    f.write(grayscale)

    dark = img.darken()
    with open("dark.bmp", "wb") as f:
        f.write(dark)
        
    
