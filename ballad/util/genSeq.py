current = 1
length = 45
outFile = open('seq2.txt', 'wb')
for i in range(length):
	outFile.write(chr(current))
	current += 2
outFile.close()
