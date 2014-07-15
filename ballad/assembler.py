#!/usr/bin/python
import argparse
import os.path
import numpy as np
from bidict import bidict

symbolTable = bidict({
	'add' : 1,
	'sub' : 2,
	'mul' : 3,
	'div' : 4,
	'xor' :  5,
	'or' :  6,
	'and' : 7,
	'inv' : 8,
	'inc' : 9,
	'dec' : 10,
	'jmp' : 11,
	'jeq' : 12,
	'jne' : 13,
	'jlt' : 14,
	'jgt' : 15,
	'jlte' : 16,
	'jgte' : 17,
	'push' : 18,
	'pop' : 19,
	'movrm' : 21,
	'movrs' : 22,
	'lstat' : 23,
	'stget' : 24,
	'stput' : 25,
	'print' : 26,
	'read' : 27,
	'ret' : 28,
	'movis' : 29,
	'movim' : 30,
})

singleInstr = [
	'inv',
	'inc',
	'dec',
	'jmp',
	'push',
	'pop',
	'ret']
doubleInstr = [
	'add',
	'sub',
	'mul',
	'div',
	'xor',
	'or',
	'and',
	'lstat',
	'stget',
	'stput',
	'movis',
	'movim',
	'movrm',
	'movrs',
	'print',
	'read']
tripleInstr = [
	'jeq',
	'jne',
	'jlt',
	'jgt',
	'jlte',
	'jgte']

regTable = {
	'm0': 0,
	'm1': 1,
	'm2': 2,
	'm3': 3,
	'm4': 4,
	'm5': 5,
	'm6': 6,
	'm7': 7,
	's0': 0,
	's1': 1,
	's2': 2,
	's3': 3,
	's4': 4,
	's5': 5,
	's6': 6,
	's7': 7,
}

class AssemblyException(Exception):
	def __init__(self, value):
		self.message = value

	def __str__(self):
		return self.message
	
#NOTE:
#Data fields must be converted to twin-ASCII hex representations
# i.e., to do a newline (\n), do: 0a

def assemble(program):
	lines = program.split('\n')
	lineCount = 1
	dataMode=True
	labels = {}
	offset = 0
	byteStr = ''
	statMem = []
	statMemTable = {}
	for line in lines:
		if dataMode:
			if '#' in line:
				line = line[0:line.find('#')]
			if line == '_data:':
				pass
			elif line == '_text:':
				dataMode = False
			elif ':' in line:
				symbol, data = line.split(':')
				dataBlock = ''
				for i in range(0, len(data), 2):
					currHex = data[i:i+2]
					num = int(currHex, 16)
					dataBlock += chr(num)
				dataLen = len(dataBlock)
				statOff = len(statMem)
				statMemTable[symbol] = (dataLen, statOff)
				for elem in dataBlock:
					statMem.append(elem)
		else:
			if '#' in line:
				line = line[0:line.find('#')]
			spaceArgs = line.strip().split(' ')
			instr = spaceArgs[0]
			del spaceArgs[0]
			if not instr:
				#Don't increment the offset, ignore (should happen
				# for commented out lines)
				pass
			elif instr in symbolTable:
				#Get the correct opcode
				opcode = symbolTable[instr]
				#Parse out any ',' in the arguments and then strip:
				args = [arg.replace(',','').strip() for arg in spaceArgs]
				if instr in singleInstr:
					if len(args) == 1:
						arg = args[0]
						#Handle single instruction
						if arg in regTable:
							arg = regTable[arg]
						elif arg in labels:
							arg = labels[arg]
						elif 'LEN_' in arg:
							dataLen, statOff = statMemTable[arg[len('LEN_'):]]
							arg = dataLen
						elif '_OFF' in arg:
							dataLen, statOff = statMemTable[arg.split('_OFF')[0]]
							arg = statOff
						elif ('%d' % int(arg)) == arg:
							arg = int(arg)
						else:
							raise AssemblyException('Argument not found: %s on line %d' %
								(arg, lineCount))
						byteStr += chr(opcode)
						byteStr += chr(arg)
						#handle instruction, increment offset
						offset += 2

					else:
						raise AssemblyException(
							'Incorrect number of arguments for instruction %s on line %d' %
							(instr, lineCount))
				elif instr in doubleInstr:
					if len(args) == 2:
						#Handle double instructions
						arg1 = args[0]
						arg2 = args[1]
						if arg1 in regTable:
							arg1 = regTable[arg1]
						elif arg1 in labels:
							arg1 = labels[arg1]
						elif 'LEN_' in arg1:
							dataLen, statOff = statMemTable[arg1[len('LEN_'):]]
							arg1 = dataLen
						elif '_OFF' in arg1:
							dataLen, statOff = statMemTable[arg1.split('_OFF')[0]]
							arg1 = statOff
						elif ('%d' % int(arg1)) == arg1:
							arg1 = int(arg1)
						else:
							raise AssemblyException('Argument not found: %s on line %d' %
								(arg, lineCount))
						if arg2 in regTable:
							arg2 = regTable[arg2]
						elif arg2 in labels:
							arg2 = labels[arg2]
						elif 'LEN_' in arg2:
							dataLen, statOff = statMemTable[arg2[len('LEN_'):]]
							arg2 = dataLen
						elif '_OFF' in arg2:
							dataLen, statOff = statMemTable[arg2.split('_OFF')[0]]
							arg2 = statOff
						elif ('%d' % int(arg2)) == arg2:
							arg2 = int(arg2)
						else:
							raise AssemblyException('Argument not found: %s on line %d' %
								(arg, lineCount))
						byteStr += chr(opcode)
						byteStr += chr(arg1)
						byteStr += chr(arg2)
						#handle instruction, increment offset
						offset += 3
					else:
						raise AssemblyException(
							'Incorrect number of arguments for instruction %s on line %d' %
							(instr, lineCount))
				elif instr in tripleInstr:
					if len(args) == 3:
						#Handle three argument instructions
						arg1 = args[0]
						arg2 = args[1]
						arg3 = args[2]
						if arg1 in regTable:
							arg1 = regTable[arg1]
						elif arg1 in labels:
							arg1 = labels[arg1]
						elif 'LEN_' in arg1:
							dataLen, statOff = statMemTable[arg1[len('LEN_'):]]
							arg1 = dataLen
						elif '_OFF' in arg1:
							dataLen, statOff = statMemTable[arg1.split('_OFF')[0]]
							arg1 = statOff
						elif ('%d' % int(arg1)) == arg1:
							arg1 = int(arg1)
						else:
							raise AssemblyException('Argument not found: %s on line %d' %
								(arg1, lineCount))
						if arg2 in regTable:
							arg2 = regTable[arg2]
						elif arg2 in labels:
							arg2 = labels[arg2]
						elif 'LEN_' in arg2:
							dataLen, statOff = statMemTable[arg2[len('LEN_'):]]
							arg2 = dataLen
						elif '_OFF' in arg2:
							dataLen, statOff = statMemTable[arg2.split('_OFF')[0]]
							arg2 = statOff
						elif ('%d' % int(arg2)) == arg2:
							arg2 = int(arg2)
						else:
							raise AssemblyException('Argument not found: %s on line %d' %
								(arg2, lineCount))
						if arg3 in regTable:
							arg3 = regTable[arg3]
						elif arg3 in labels:
							arg3 = labels[arg3]
						elif 'LEN_' in arg3:
							dataLen, statOff = statMemTable[arg3[len('LEN_'):]]
							arg3 = dataLen
						elif '_OFF' in arg3:
							dataLen, statOff = statMemTable[arg3.split('_OFF')[0]]
							arg3 = statOff
						elif ('%d' % int(arg3)) == arg3:
							arg3 = int(arg3)
						else:
							raise AssemblyException('Argument not found: %s on line %d' %
								(arg3, lineCount))
						byteStr += chr(opcode)
						byteStr += chr(arg1)
						byteStr += chr(arg2)
						byteStr += chr(arg3)
						#handle instruction, increment offset
						offset += 4
					else:
						raise AssemblyException(
							'Incorrect number of arguments for instruction %s on line %d' %
							(instr, lineCount))
			else:
				#Check for presence of ':' at end of line:
				if instr[-1] == ':':
					#this must be a label, add it to the label dict
					labels[instr[:-1]] = offset
				else:
					raise AssemblyException('Error: instruction not found: %s on line %d'
						% (instr, lineCount))
				#don't increment offset
		lineCount += 1
	statMem = ''.join(statMem)
	return (byteStr, statMem)

def main():
	parser = argparse.ArgumentParser(description='This will assemble Ballad assembly to Ballad bytecode.')
	parser.add_argument('basm', help='The .b file to assemble')
	parser.add_argument('-o', '--obFile', help='The .ob file to output to, default = BASM.ob', nargs='?', 
		default=False)
	parser.add_argument('-sm', '--statMem', help='The .smb file to output to, default = BASM.smb', nargs='?', 
		default=False)
	args = parser.parse_args()

	baseName = os.path.basename(args.basm).split('.')[0]
	if not args.obFile:
		args.obFile = baseName + '.ob'
	if not args.statMem:
		args.statMem = baseName + '.smb'
	
	basmFile = open(args.basm, 'r')

	obj, sm = assemble(basmFile.read())
	basmFile.close()
	objFile = open(args.obFile, 'wb')
	objFile.write(obj)
	objFile.close()
	statMemFile = open(args.statMem, 'wb')
	statMemFile.write(sm)
	statMemFile.close()

if __name__ == '__main__':
	main()
