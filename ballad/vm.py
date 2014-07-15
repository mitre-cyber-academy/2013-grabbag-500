#!/usr/bin/python
import numpy as np
import sys
import argparse
from assembler import symbolTable, singleInstr, doubleInstr, tripleInstr
from transcoder import key_note_length, offsetArr
from music21 import midi, note, chord

#The stack size and the program size are both 256 for easy addressing
STACK_SIZE = 256
PROG_SIZE = 256

#Create a `vm themed' error
class VMError(Exception):
	def __init__(self, value):
		self.message = value

	def __str__(self):
		return self.message

class BalladVM:
	#Initialize the stack, stack pointer, et. al. as zero
	def __init__(self):
		self.stack = np.zeros(STACK_SIZE, dtype=np.uint8)
		self.sp = np.uint8(0)
		self.pc = np.uint8(0)
		self.s_regs = np.zeros(8, dtype=np.uint8)
		self.m_regs = np.zeros(8, dtype=np.uint8)
		self.progmem = np.zeros(PROG_SIZE, dtype=np.uint8)

	#This loads an object from the paired code and static 
	# memory files
	def load_obj(self, obj_fname, statmem_fname):
		obj_file = open(obj_fname, 'rb')
		statmem_file = open(statmem_fname, 'rb')
		statmem = statmem_file.read()
		obj = obj_file.read()
		for i in range(len(obj)):
			self.progmem[i] = ord(obj[i])
		self.statmem = []
		for i in range(len(statmem)):
			self.statmem.append(ord(statmem[i]))

	#This loads an object from the proper midi file using music21
	def load_midi(self, midi_fname):
		midi_file = midi.base.MidiFile()
		midi_file.open(midi_fname, 'rb')
		midi_file.read()
		if len(midi_file.tracks) != 2:
			raise VMError(
				'Error: Incorrect number of tracks in Ballad program: %d',
				len(midi_file.tracks))
		else:
			#Stream 0 has the static data section
			static_stream = midi.translate.midiTrackToStream(
				midi_file.tracks[0])
			#Stream 1 has the program code section
			code_stream = midi.translate.midiTrackToStream(
				midi_file.tracks[1])
			tmp_note = note.Note()
			tmp_chord = chord.Chord()
			static_string = ''
			code_string = ''
			midi_key = -1
			#Transcode the static data
			for curr_note in static_stream:
				midi_num = -1
				note_type = type(curr_note)
				if note_type == type(tmp_note):
					midi_num = curr_note.midi
				elif note_type == type(tmp_chord):
					midi_num = curr_note[0].midi
				if note_type == type(tmp_note) or  \
					note_type == type(tmp_chord):
					if curr_note.duration.quarterLength == key_note_length and midi_key < 0:
						midi_key = midi_num
					elif midi_key >= 0:
						curr_num = offsetArr[:midi_num - midi_key]
						static_string += '%1x' % curr_num
			midi_key = -1
			#Transcode the program code
			for curr_note in code_stream:
				midi_num = -1
				note_type = type(curr_note)
				if note_type == type(tmp_note):
					midi_num = curr_note.midi
				elif note_type == type(tmp_chord):
					midi_num = curr_note[0].midi
				if note_type == type(tmp_note) or  \
					note_type == type(tmp_chord):
					if curr_note.duration.quarterLength == key_note_length and midi_key < 0:
						midi_key = midi_num
					else:
						curr_num = offsetArr[:midi_num - midi_key]
						code_string += '%1x' % curr_num
			self.statmem = []
			for i in range(0, len(static_string), 2):
				self.statmem.append(int(static_string[i: i+2], 16))
			for i in range(0, len(code_string), 2):
				self.progmem[i/2] = (int(code_string[i: i+2], 16))

	#This will run one step of execution of the
	# program
	def exec_timestep(self):
		#Fetch instruction at pc:
		curr_opcode = self.progmem[self.pc]
		if curr_opcode == 0:
			pass
		else:
			curr_instr = symbolTable[:curr_opcode]
			#Deal with the fact that or, and and print are
			# all reserved words
			if curr_instr == 'or' or  \
				curr_instr == 'and' \
				or curr_instr == 'print':
				curr_instr += '_'
			func = getattr(self, curr_instr)
			curr_instr = curr_instr.replace('_','')
			#Determine how many arguments we need
			# then run the appropriate instruction
			if curr_instr in singleInstr:
				self.pc += 1
				func(self.progmem[self.pc])
			elif curr_instr in doubleInstr:
				self.pc += 1
				arg1 = self.progmem[self.pc]
				self.pc += 1
				arg2 = self.progmem[self.pc]
				func(arg1, arg2)
			elif curr_instr in tripleInstr:
				self.pc += 1
				arg1 = self.progmem[self.pc]
				self.pc += 1
				arg2 = self.progmem[self.pc]
				self.pc += 1
				arg3 = self.progmem[self.pc]
				func(arg1, arg2, arg3)
			else:
				raise VMError('Error: Instruction %s not found near offset %d'
					 % (curr_instr, self.pc))
			self.pc += 1

	#Mathematical functions:
	def add(self, m0, m1):
		self.m_regs[m0] = self.m_regs[m0] + self.m_regs[m1]
	def sub(self, m0, m1):
		self.m_regs[m0] = self.m_regs[m0] - self.m_regs[m1]
	def mul(self, m0, m1):
		self.m_regs[m0] = self.m_regs[m0] * self.m_regs[m1]
	def div(self, m0, m1):
		self.m_regs[m0] = self.m_regs[m0] / self.m_regs[m1]
	def xor(self, m0, m1):
		self.m_regs[m0] = self.m_regs[m0] ^ self.m_regs[m1]
	def or_(self, m0, m1):
		self.m_regs[m0] = self.m_regs[m0] | self.m_regs[m1]
	def and_(self, m0, m1):
		self.m_regs[m0] = self.m_regs[m0] & self.m_regs[m1]
	def inv(self, m0):
		self.m_regs[m0] = ~self.m_regs[m0]
	def inc(self, m0):
		self.m_regs[m0] += 1
	def dec(self, m0):
		self.m_regs[m0] -= 1

	#Jump instructions:
	#Subtraction of 1 is so that when the PC gets incremented,
	# it ends up at in the correct places
	def jmp(self, off):
		self.pc = off - 1
	def jeq(self, m0, m1, off):
		if self.m_regs[m0] == self.m_regs[m1]:
			self.pc = off - 1
	def jne(self, m0, m1, off):
		if self.m_regs[m0] != self.m_regs[m1]:
			self.pc = off - 1
	def jlt(self, m0, m1, off):
		if self.m_regs[m0] < self.m_regs[m1]:
			self.pc = off - 1

	def jgt(self, m0, m1, off):
		if self.m_regs[m0] > self.m_regs[m1]:
			self.pc = off - 1
	def jlte(self, m0, m1, off):
		if self.m_regs[m0] <= self.m_regs[m1]:
			self.pc = off - 1
	def jgte(self, m0, m1, off):
		if self.m_regs[m0] >= self.m_regs[m1]:
			self.pc = off - 1
	def ret(self, m0):
		self.pc = self.m_regs[m0] - 1

	#Memory instructions:
	def push(self, s0):
		self.stack[self.sp] = self.s_regs[s0]
		self.sp += 1
	def pop(self, s0):
		self.s_regs[s0] = self.stack[self.sp]
		self.sp -= 1
	def lstat(self, s0, m0):
		self.s_regs[s0] = self.statmem[
			self.m_regs[m0]]

	def stget(self, s0, m0):
		self.s_regs[s0] = self.stack[
			self.m_regs[m0]]
	def stput(self, m0, s0):
		self.stack[
			self.m_regs[m0]] = self.s_regs[s0]
	# - Move instructions
	def movim(self, m0, byte):
		self.m_regs[m0] = byte
	def movis(self, s0, byte):
		self.s_regs[s0] = byte
	def movrm(self, m0, s0):
		self.m_regs[m0] = self.s_regs[s0]
	def movrs(self, s0, m0):
		self.s_regs[s0] = self.m_regs[m0]

	#Utility instructions
	#This prints out a message
	def print_(self, s0, s1):
		message = (self.stack[
			self.s_regs[s0]:
			self.s_regs[s0] +
			self.s_regs[s1]])
		message = ''.join(['%c' % char for char in message])
		stackString = ''.join([chr(char) for char in self.stack])
		sys.stdout.write(message)

	#This reads in to the stack
	def read(self, m0, m1):
		message = raw_input()
		message = message[0:self.m_regs[m1]]
		oLen = len(message)
		mDiff = self.m_regs[m1] - oLen
		message += mDiff * '\x00'
		message = [ord(char) for char in message]
		self.stack[self.m_regs[m0]:
			self.m_regs[m0] +
			self.m_regs[m1]] = message
		self.m_regs[m1] = oLen


def main():
	parser = argparse.ArgumentParser(
		description='This is a VM to run Ballad (byte)code')
	parser.add_argument('-bc', action='store_true', 
		help='Run Ballad through bytecode')
	parser.add_argument('name', help='The name of the Ballad file(s)')
	
	args = parser.parse_args()
	
	#If we're running in bytecode mode, dispatch to the bytecode loader
	if args.bc:
		sm_name = args.name + '.smb'
		obj_name = args.name + '.ob'
		vm = BalladVM()
		vm.load_obj(obj_name, sm_name)
	else: #Otherwise, use the midi loader
		vm = BalladVM()
		vm.load_midi(args.name)

	#Initialize the PC to the current one - this is how we track exit 
	# conditions
	curr_pc = vm.pc
	prev_pc = -1
	while curr_pc != prev_pc:
		#Loop until the program is done (the PC doesn't move anymore)
		vm.exec_timestep()
		prev_pc = curr_pc
		curr_pc = vm.pc

if __name__ == '__main__':
	main()
