#!/usr/bin/python 
from music21 import note, chord, stream, duration, midi, tempo
import argparse
from bidict import bidict

#Let the start of the stream be a whole note indicating
# the key
key_note_length = 4.0
#Define an array to calculate steps from the tonic:
#(for two octaves + 2 notes to make a full 16)
offsetArr = bidict({
	0 :0 , 
	1 :2 , 
	2 :4 , 
	3 :5 , 
	4 :7 , 
	5 :9 , 
	6 :11, 
	7 :12, 
	8 :14, 
	9 :16, 
	10:17, 
	11:19, 
	12:21, 
	13:23, 
	14:24, 
	15:26})
def transcode(blob):
	#By default, the key will be `middle C'
	key = 0
	#Which is midi 60
	midiBase = 60
	#Key ranges from 0 = C to 12 = B
	#Tempo ranges: 90 - 168
	bpm = 90
	#with 90 by default
	try:
		bpm = (ord(blob[1]) % (168 - 90)) + 90
		key = ord(blob[0]) % 12
	except:
		try:
			key = ord(blob[0]) % 12
		except:
			pass
	key += midiBase
	
	#length array - mapping numeric values to note length:
	lenArr = [
		0.5,
		1.0,
		1.5,
		2.0,
		2.5,
		3.0,
		3.5,
		4.0,
		]

	#This array holds offsets to add to the root for a chord:
	chordArr = [
		[0, 2, 4, 7],
		[0, 4],
		[0, 2, 4],
		[0]]

	#Make a music21 Part to hold this particular run. This allows tracks
	melTrack = stream.Part()

	#add the tempo
	melTrack.append(tempo.MetronomeMark(number=bpm))
	
	#should start every data section with a whole note of the proper key
	keyNote = note.Note()

	keyNote.midi = key
	#Add the key note to the start of the stream
	keyNote.duration = duration.Duration(key_note_length)
	melTrack.append(keyNote)
	#Start parsing the bytes in the blob, using each of the bytes as a pair
	# of hex digits
	for byte in blob:
		byte = ord(byte)
		hexes = '%02x' % byte
		#Take each 0-F hex value and transcode it to a MIDI note based
		# on the key
		for hexDig in hexes:
			hexNum = int(hexDig, 16)
			noteLen = lenArr[hexNum % len(lenArr)]
			chordOffs = chordArr[hexNum % len(chordArr)]
			currChordList = []
			for elem in chordOffs:
				try:
					noteOff = offsetArr[hexNum + elem]
					tmpNote = note.Note()
					tmpNote.midi = key + noteOff
					currChordList.append(tmpNote)
				except KeyError:
					#Truncate chords which have higher notes above our limit
					pass
			currNotes = chord.Chord(currChordList)
			currNotes.duration = duration.Duration(noteLen)
			melTrack.append(currNotes)
	return melTrack

def main():
	parser = argparse.ArgumentParser(description='This program will read in Ballad bytecode and transcode it to a MIDI file')
	parser.add_argument('balbyc', help='The common name of the Ballad .ob and .smb files')
	args = parser.parse_args()
	
	obFile = open(args.balbyc + '.ob', 'rb')
	smbFile = open(args.balbyc + '.smb', 'rb')
	
	obPart = transcode(obFile.read())
	smbPart = transcode(smbFile.read())
	#Add a long rest to the second track to avoid time collision when playing
	r1 = note.Rest()
	r1.duration = duration.Duration(obPart.highestTime)
	obPart.insertAndShift(0, r1)

	ballad = stream.Score()
	ballad.insert(0, smbPart)
	ballad.append(obPart)

	mf = midi.translate.streamToMidiFile(ballad)
	mf.open(args.balbyc + '.mid', 'wb')
	mf.write()
	mf.close()

if __name__ == '__main__':
	main()
