from tkinter import *
from tkinter import filedialog
from math import ceil, cos, pi
import os

# def dct(N):
# 	C = [[0 for i in range(N)] for i in range(N)]
# 	for i in range(N):
# 		for j in range(N):
# 			a = (1 / N) ** 0.5
# 			if i != 0:
# 				a = (2/N) ** 0.5
# 			C[i][j] = a * cos(((2*j+1)*i*pi) / (2*N))
# 	return C
# def printMat(x)	:
# 	for i in range(len(x)):
# 		for j in range(len(x[0])):
# 			print(x[i][j], end=' ')
# 		print()
def myround(value, lowerbound, higherbound):
    """ Round value back to the interval between [lowerbound, higherbound]"""
    if value < lowerbound:
        return lowerbound
    if value > higherbound:
        return higherbound
    return value

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

def matrixMult(a, b):
	a_h = len(a)
	a_w = len(a[0])
	b_h = len(b)
	b_w = len(b[0])
	if a_w != b_h:
		raise Exception("Width of a ({}x{}) must be equal to height of b({}:{})".format(a_h, a_w, b_h, b_w))
	c = [[0 for i in range(a_h)] for i in range(b_w)]
	for i in range(a_h):
		for j in range(b_w):
			for k in range(a_w):
				c[i][j] += a[i][k]*b[k][j]
	return c			
def transpose(a):
	h = len(a)
	w = len(a[0])
	res = [[0 for i in range(h)] for i in range(w)]
	for i in range(h):
		for j in range(w):
			res[j][i] = a[i][j]
	return res

def maxMatrix(a):
	# max_val = max(a[0])
	# for i in range(1,len(a)):
	# 	max_val = max(max(a[i]), max_val)
	# return max_val
	return [*zip(*a)]
class Bmp24BitImage():
    def __init__(self, path):
        if (not path.endswith('.bmp')):
            raise Exception("File must be bmp")
        self.path = path    
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
               
    def __readImg(self, path):
        img = bytearray()
        with open(path, "rb") as f:
            byte = f.read(1)
            while byte:
                img += byte
                byte = f.read(1)
        return img

class Compressor:
	def __init__(self, bmpImg):
		self.bmpImg = bmpImg
		if bmpImg:
			self.imgPixels = bmpImg.original()
			self.imgPixels.reverse()
		# self.quantization_table = [[1,1,2,4,8,16,32,64],
		# 							[1,1,2,4,8,16,32,64],
		# 							[2,2,2,4,8,16,32,64],
		# 							[4,4,4,4,8,16,32,64],
		# 							[8,8,8,8,8,16,32,64],
		# 							[16,16,16,16,16,16,32,64],
		# 							[32,32,32,32,32,32,32,64],
		# 							[64,64,64,64,64,64,64,64]]
		self.quantization_table = [[16,11,10,16,24,40,51,61],
									[12,12,14,19,26,58,60,65],
									[14,13,16,24,40,57,69,56],
									[14,17,22,29,51,87,80,62],
									[18,22,37,56,68,109,103,7],
									[24,35,55,64,81,104,113,92],
									[49,64,78,87,103,121,120,101],
									[72,92,95,98,112,100,103,99]]
		self.blockSize = 8


	def decompress(self, path):
		dct = self.dct(self.blockSize)
		img = bytearray()
		with open(path, "rb") as f:
			byte = f.read(1)
			while byte:
				img += byte
				byte = f.read(1)
		y_h = bytesToInt(img[0:2], byteorder='big')
		y_w = bytesToInt(img[2:4], byteorder='big')
		cb_h = bytesToInt(img[4:6], byteorder='big')
		cb_w = bytesToInt(img[6:8], byteorder='big')
		cr_h = bytesToInt(img[8:10], byteorder='big')
		cr_w = bytesToInt(img[10:12], byteorder='big')

		yEncoded_len = bytesToInt(img[12:15], byteorder='big')
		yEncoded_end = 15 + yEncoded_len
		yEncoded = img[15:yEncoded_end]

		cbEncoded_start = yEncoded_end + 3
		cbEncoded_len = bytesToInt(img[yEncoded_end:cbEncoded_start], byteorder='big')
		cbEncoded_end = cbEncoded_start + cbEncoded_len
		cbEncoded = img[cbEncoded_start:cbEncoded_end]

		crEncoded_start = cbEncoded_end + 3
		crEncoded_len = bytesToInt(img[cbEncoded_end:crEncoded_start], byteorder='big')
		crEncoded = img[crEncoded_start:]

		y = [[0 for i in range(y_w)] for i in range(y_h)]
		cb = [[0 for i in range(cb_w)] for i in range(cb_h)]
		cr = [[0 for i in range(cr_w)] for i in range(cr_h)]

		# Decode
		i,j = 0,0
		y_tmp = []
		while i < yEncoded_len:
			val = int.from_bytes(yEncoded[i:(i+2)], byteorder='big', signed=True)
			count = int.from_bytes(yEncoded[(i+2):(i+4)], byteorder='big')
			for k in range(count):
				y[j//y_w][j%y_w] = val
				y_tmp.append(val)
				j += 1
			i += 4

		i,j = 0,0
		while i < cbEncoded_len:
			val = int.from_bytes(cbEncoded[i:(i+2)], byteorder='big', signed=True)
			count = int.from_bytes(cbEncoded[(i+2):(i+4)], byteorder='big')
			for k in range(count):
				#print(j, k, count, i)
				cb[j//cb_w][j%cb_w] = val
				j += 1
			i += 4

		i,j = 0,0
		while i < crEncoded_len:
			val = int.from_bytes(crEncoded[i:(i+2)], byteorder='big', signed=True)
			count = int.from_bytes(crEncoded[(i+2):(i+4)], byteorder='big')
			for k in range(count):
				cr[j//cr_w][j%cr_w] = val
				j += 1
			i += 4



		# Dequantize
		self.dequantize(y)
		self.dequantize(cb)
		self.dequantize(cr)


		#print(y[0])
		# Revert
		self.revert(y, dct)
		self.revert(cb, dct)
		self.revert(cr, dct)

		# Convert to RGB
		r, g, b = self.ycbcr2rgb(y, cb, cr)
		# print(r[0])
		originalPixels = [[(0,0,0) for i in range(y_w)] for i in range(y_h)]	
		for i in range(y_h):
			for j in range(y_w):
				originalPixels[i][j] = (r[i][j], g[i][j], b[i][j])

		return originalPixels


	def compress(self):
		y, cb, cr = self.rgb2ycbcr()
		y = self.addPadding(y, self.blockSize)
		cb = self.addPadding(cb, self.blockSize)
		cr = self.addPadding(cr, self.blockSize)
		#self.downSampling()
		dct = self.dct(self.blockSize)


		self.transform(y, dct)
		self.transform(cb, dct)
		self.transform(cr, dct)

		self.quantize(y)
		self.quantize(cb)
		self.quantize(cr)

		y_h, y_w = len(y), len(y[0])
		cb_h, cb_w = len(cb), len(cb[0])
		cr_h, cr_w = len(cr), len(cr[0])
		yEncoded, cbEncoded, crEncoded = bytearray(), bytearray(), bytearray()

		i = 0
		while i < y_h * y_w:
			val = y[i//y_w][i%y_w]
			count = 1
			while i + 1 < y_h * y_w and val == y[(i+1)//y_w][(i+1)%y_w]:
				count += 1
				i += 1
			yEncoded += int(val).to_bytes(2, byteorder='big', signed=True)
			yEncoded += int(count).to_bytes(2, byteorder='big')
			i += 1
		# return
		i = 0
		while i < cb_h * cb_w:
			val = cb[i//cb_w][i%cb_w]
			count = 1
			while i + 1 < cb_h * cb_w and val == cb[(i+1)//cb_w][(i+1)%cb_w]:
				count += 1
				i += 1
			cbEncoded += int(val).to_bytes(2, byteorder='big', signed=True)
			cbEncoded += int(count).to_bytes(2, byteorder='big')
			i += 1
		i = 0
		while i < cr_h * cr_w:
			val = cr[i//cr_w][i%cr_w]
			count = 1
			while i + 1 < cr_h * cr_w and val == cr[(i+1)//cr_w][(i+1)%cr_w]:
				count += 1
				i += 1
			crEncoded += int(val).to_bytes(2, byteorder='big', signed=True)
			crEncoded += int(count).to_bytes(2, byteorder='big')
			i += 1
		self.save(y, cb, cr, yEncoded, cbEncoded, crEncoded)

	def save(self, y, cb, cr, yEncoded, cbEncoded, crEncoded):
		fileBytes = bytearray()
		y_h_byte = int(len(y)).to_bytes(2, byteorder='big')
		y_w_byte = int(len(y[0])).to_bytes(2, byteorder='big')
		cb_h_byte = int(len(cb)).to_bytes(2, byteorder='big')
		cb_w_byte = int(len(cb[0])).to_bytes(2, byteorder='big')
		cr_h_byte = int(len(cr)).to_bytes(2, byteorder='big')
		cr_w_byte = int(len(cr[0])).to_bytes(2, byteorder='big')	

		fileBytes += y_h_byte
		fileBytes += y_w_byte
		fileBytes += cb_h_byte
		fileBytes += cb_w_byte
		fileBytes += cr_h_byte
		fileBytes += cr_w_byte

		fileBytes += int(len(yEncoded)).to_bytes(3, byteorder='big')
		fileBytes += yEncoded
		fileBytes += int(len(cbEncoded)).to_bytes(3, byteorder='big')
		fileBytes += cbEncoded
		fileBytes += int(len(crEncoded)).to_bytes(3, byteorder='big')
		fileBytes += crEncoded

		f = open(os.path.splitext(self.bmpImg.path)[0] + ".IMG", "wb+")
		f.write(fileBytes)
		f.close()


	def quantize(self, x):
		blockSize = self.blockSize
		h = len(x)
		w = len(x[0])
		for i in range(0, h, blockSize):
			for j in range(0, w, blockSize):
				for k in range(i, i + blockSize):
					for g in range(j, j + blockSize):
						x[k][g] = round(x[k][g] / self.quantization_table[k - i][g - j])

	def dequantize(self, x):
		blockSize = self.blockSize
		h = len(x)
		w = len(x[0])
		for i in range(0, h, blockSize):
			for j in range(0, w, blockSize):
				for k in range(i, i + blockSize):
					for g in range(j, j + blockSize):
						x[k][g] = round(x[k][g] * self.quantization_table[k-i][g-j])


	def addPadding(self, x, size):
		h = len(x)
		w = len(x[0])
		if h % size != 0 :
			new_h = ceil(h / size) * size
			for i in range(new_h - h):
				x.append([255 for i in range(old_w)])
			h = new_h
		if w % size != 0:
			new_w = ceil(w / size) * size
			for i in range(h):
				x[i] = x[i] + [255 for j in range(new_w - w)]
			w = new_w
		return x


	def transform(self, x, dct):
		blockSize = len(dct)
		h = len(x)
		w = len(x[0])
		transposed_dct = transpose(dct)
		for i in range(h):
			for j in range(w):
				x[i][j] -= 128 # normalize to [-128, 127]

		for i in range(0, h, blockSize):
			for j in range(0, w, blockSize):
				block = [x[k][j:(j+blockSize)] for k in range(i, i + blockSize)]
				transformed_block = matrixMult(matrixMult(dct, block), transposed_dct)

				for k in range(i, i + blockSize):
					for g in range(j, j + blockSize):
						x[k][g] = round(transformed_block[k-i][g-j])
		return x

	def revert(self, x, dct):
		blockSize = len(dct)
		h = len(x)
		w = len(x[0])
		transposed_dct = transpose(dct)

		for i in range(0, h, blockSize):
			for j in range(0, w, blockSize):
				block = [x[k][j:(j+blockSize)] for k in range(i, i + blockSize)]
				transformed_block = matrixMult(matrixMult(transposed_dct, block), dct)

				for k in range(i, i + blockSize):
					for g in range(j, j + blockSize):
						x[k][g] = round(transformed_block[k-i][g-j])

		for i in range(h):
			for j in range(w):
				x[i][j] += 128 # normalize to [-128, 127]
		return x


	def dct(self, N):
		C = [[0 for i in range(N)] for i in range(N)]
		for i in range(N):
			for j in range(N):
				a = (1 / N) ** 0.5
				if i != 0:
					a = (2/N) ** 0.5
				C[i][j] = a * cos(((2*j+1)*i*pi) / (2*N))
		return C

	def rgb2ycbcr(self):
		"""
			Y = 0.299 R + 0.587 G + 0.114 B
			Cb = - 0.1687 R - 0.3313 G + 0.5 B + 128
			Cr = 0.5 R - 0.4187 G - 0.0813 B + 128
		"""
		Y = []
		Cb = []
		Cr = []
		for row in self.imgPixels:
			y_row = []
			cb_row = []
			cr_row = []
			for (r,g,b) in row:
				y_row.append(round(0.299*r + 0.587*g + 0.114*b))
				cb_row.append(round(-0.1687*r-0.3313*g+0.5*b+128))
				cr_row.append(round(0.5*r-0.4187*g-0.0813*b+128))
			Y.append(y_row)
			Cb.append(cb_row)
			Cr.append(cr_row)
		return Y, Cb, Cr

	def ycbcr2rgb(self, Y, Cb, Cr):
		h = len(Y)
		w = len(Y[0])
		R = [[0 for i in range(w)] for i in range(h)]
		G = [[0 for i in range(w)] for i in range(h)]
		B = [[0 for i in range(w)] for i in range(h)]
		for i in range(len(Y)):
			for j in range(len(Y[0])):
				R[i][j] = myround(round(Y[i][j] + 1.402 * (Cr[i][j] - 128)), 0, 255)
				G[i][j] = myround(round(Y[i][j] - 0.34414 * (Cb[i][j] - 128) - 0.71414*(Cr[i][j] - 128)), 0, 255)
				B[i][j] = myround(round(Y[i][j] + 1.772 * (Cb[i][j] - 128)), 0 ,255)
		return R, G, B


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
        root.filename = filedialog.askopenfilename(initialdir=".",title="Select an image",
        	filetypes=(("bmp files", "*.bmp"),("IMG files", "*.IMG"),))
        if root.filename:
        	ext = os.path.splitext(root.filename)[1]
        	if ext == '.bmp':
	            # Process image byte by byte
	            rawImg = Bmp24BitImage(root.filename)
	            #original = rawImg.original()
	            compressor = Compressor(rawImg)
	            compressor.compress()
	        elif ext == ".IMG" :
	        	depressor = Compressor(None)
	        	pixels = depressor.decompress(root.filename)
	        	#print(pixels[0], len(pixels), len(pixels[0]));return
	        	drawPixels(pixels)
	        else:
	        	print("File not supported")

    fileBtn = Button(root, text="Select BMP image", command=imgSelect)


    # Display buttons
    fileBtn.pack()

    # Canvas to draw image byte by byte
    cv = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    cv.pack()
    
    root.protocol("WM_DELETE_WINDOW", onExit)
    root.mainloop()