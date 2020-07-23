from tkinter import *
from tkinter import filedialog
from collections import defaultdict
from heapq import heappush, heappop


def convert_to_nbits(nBits):
	def convert(n):
		binary = format(n, 'b')
		binary = "0"*(nBits-len(binary)) + binary
		return binary
	return convert

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
		self.total_encoded_length = 0

	def extract_data(self):
		pass
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
			self.total_encoded_length += len(self.code_dict[sym])

	def get_encoded_string(self):
		res = " ".join(self.encoded)
		return res


class LZW:
	def __init__(self, input):
		self.input = input
		self.symbols = []
		self.encoded = []
		self.code_dict = defaultdict(str)
		self.code_dict_length = 0		
		self.total_encoded_length = 0

	def encode(self):
		if self.encoded: # Already encode
			return
		l = len(self.input)
		idx = 1
		s = str(self.input[0])
		while idx < l:
			c = str(self.input[idx])
			#print(int.from_bytes(c, byteorder='little', signed=True))
			if self.code_dict[s+c]:
				s = s + c
			else:
				self.encoded.append(self.code_dict[s])
				#print(s, self.code_dict[s])
				self.total_encoded_length += len(format(self.code_dict_length, 'b'))
				self.code_dict_length += 1
				self.code_dict[s+c] = str(self.code_dict_length)
				s = c
			idx += 1
		self.encoded.append(self.code_dict[s])
		self.total_encoded_length += len(format(self.code_dict_length, 'b'))
		self.code_dict_length += 1
		print("LZW total dict length:", self.code_dict_length)


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
	binaryConverter = convert_to_nbits(blockAlign * 8)
	subchunk1Size = readSubchunk1Size(offset)
    
	dataOffset = 20 + subchunk1Size + 8 # where samples data begin

	samples = []

    # Loop through samples data
	while dataOffset < len(offset):
		sample = offset[dataOffset:(dataOffset+blockAlign)]
		sampleVal = 0
		sampleVal = int.from_bytes(sample, byteorder='big')
		samples.append(binaryConverter(sampleVal))
		dataOffset += blockAlign
		# totalSamples += 1

	return samples, offset[44:]



    
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
		global huffmanRatioLbl, lzwRatioLbl
        # Choose file
		root.filename = filedialog.askopenfilename(initialdir=".", title="Select wav file", filetypes=(("wav files", "*.wav"),))
        # Extract sample data
		data, rawData = readSamples(root.filename)
		length_before = len(rawData) * 8 # in bits
		huffman = Huffman(data)
		lzw = LZW(data)
		huffman.encode()
		lzw.encode()

		print("Data length:",  length_before)
		print("Huffman:", huffman.total_encoded_length)
		print("Huffman ratio:", length_before / huffman.total_encoded_length)
		print("LZW:", lzw.total_encoded_length)
		print("LZW ratio:", length_before  / lzw.total_encoded_length)

		huffmanRatio = length_before / huffman.total_encoded_length
		lzwRatio = length_before / lzw.total_encoded_length
		huffmanRatioLbl.set("Huffman compression ratio: " + str(huffmanRatio))
		lzwRatioLbl.set("Lzw compression ratio: " + str(lzwRatio))

        # Update label

	chooseFileBtn = Button(root, text="Choose file", command=chooseFile)
	chooseFileBtn.pack()

	# # Label
	huffmanRatioLbl = StringVar()
	huffmanRatioLbl.set("Huffman compression ratio:")
	Label(root, textvariable=huffmanRatioLbl).pack()

	lzwRatioLbl = StringVar()
	lzwRatioLbl.set("Lzw compression ratio:")
	Label(root, textvariable=lzwRatioLbl).pack()

	root.mainloop()
        