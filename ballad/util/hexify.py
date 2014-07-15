import sys

inString = sys.argv[1]
output = ''
for char in inString:
	output += '%02x' % ord(char)

print output
