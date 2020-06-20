from PIL import Image
#img = Image.open('earth.bmp').convert('L')
#img.save('greyscale_test.bmp')


offset = bytearray()
with open("greyscale_test.bmp", "rb") as f:
    byte = f.read(1)
    while byte:
        offset += byte
        byte = f.read(1)
dataOffset = int.from_bytes(offset[10:14], byteorder='little')
colorUsed = int.from_bytes(offset[46:50], byteorder='little')
print("Data offset:",dataOffset)
print("Color used:",colorUsed)
for i in range(54,1078):
    print(offset[i])

