f1 = open('pietSeq.txt', 'rb')
f1dat = f1.read()
'''
f2 = open('seq2.txt', 'rb')
f2dat = f2.read()
'''
f2dat = ''
for i in range(1, len(f1dat), 2):
	f2dat += chr(i)
f1dat_norm = []
for i in range(0, len(f1dat), 2):
	f1dat_norm.append(int(f1dat[i:i+2], 16))

f2dat_norm = [ord(char) for char in f2dat]
output = ''
for i in range(0, len(f2dat_norm)):
	output += chr(f1dat_norm[i] ^ f2dat_norm[i])

print output

