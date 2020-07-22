from tkinter import *
from tkinter import filedialog
from collections import defaultdict
from heapq import heappush, heappop
class Node:
	def __init__(self, freq, symbol):
		self.freq = freq
		self.symbol = symbol
		self.left = None
		self.right = None

class Huffman:
	def __init__(self, input):
		self.input = input
		self.symbols = []
		self.encoded = []
		self.root = None
		self.code_dict = defaultdict(str)
		self.freq = defaultdict(int)

	def encode(self):
		self.symbols = [c for c in self.input]
		self.compute_freq()
		self.construct_codes()
		self.encode_string()

	def compute_freq(self):
		l = len(self.symbols)
		for sym in self.symbols:
			self.freq[sym] += 1
		for sym in self.freq:
			self.freq[sym] = self.freq[sym] / l

	def construct_codes(self):
		h = [] #heap
		index = 0
		for sym in self.freq:
			heappush(h, (self.freq[sym], index, Node(self.freq[sym], sym)))
			index += 1
		while len(h) > 1:
			_, _, left_node = heappop(h)
			_, _, right_node = heappop(h)
			parent = Node(left_node.freq + right_node.freq, left_node.symbol+right_node.symbol)
			parent.left = left_node
			parent.right = right_node
			heappush(h, (parent.freq, index, parent))
			index += 1
		if len(h) == 1 and self.root is None:
			_, _, root = heappop(h)
			self.root = root
		self.assign_codes(node=self.root)

	def assign_codes(self, node, code=""):
		isLeaf = (not node.left) and (not node.right)
		if isLeaf:
			self.code_dict[node.symbol] = code
		else:
			if node.left:
				self.assign_codes(node.left, code + '0')
			if node.right:
				self.assign_codes(node.right, code + '1')

	def encode_string(self):
		for sym in self.symbols:
			self.encoded.append(self.code_dict[sym])

	def get_encoded_string(self):
		res = " ".join(self.encoded)
		return res



def readSampleRate(offset):
	return int.from_bytes(offset[24:28], byteorder='little')
def readBitsPerSample(offset):
	return int.from_bytes(offset[34:36], byteorder='little')
def readBlockAlign(offset):
	return int.from_bytes(offset[32:34], byteorder='little')
def readSubchunk1Size(offset):
	return int.from_bytes(offset[16:20], byteorder='little')

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
	return samples, totalSamples, maxValue, maxAbsValue


    
if __name__ == "__main__":


    # Init size
	WINDOW_SIZE = "1400x700"
	CANVAS_WIDTH = 1200
	CANVAS_HEIGHT = 600

	root = Tk()
	root.title("Q2")
	root.geometry(WINDOW_SIZE)

        # Event handler
	def chooseFile():
		global cv
		global lines
		global totalSamplesLbl, maxValueLbl, maxAbsValueLbl
        # Choose file
		root.filename = filedialog.askopenfilename(initialdir=".", title="Select wav file", filetypes=(("wav files", "*.wav"),))
        # Extract sample data
		samples, totalSamples, maxValue, maxAbsValue  = readSamples(root.filename)

		huffman = Huffman(samples)
		huffman.encode()
		#print(huffman.get_encoded_string())
        # Update label
	chooseFileBtn = Button(root, text="Choose file", command=chooseFile)
	chooseFileBtn.pack()

	root.mainloop()
        