from midiutil.MidiFile import MIDIFile

midi1 = MIDIFile(1)

track = 0
time = 0
midi1.addTrackName(track, time, 'Test track')
midi1.addTempo(track, time, 120)

for i in range(13):
	track = 0
	channel = 0
	pitch = 60 + i
	time = i
	duration = 1
	volume = 100
	midi1.addNote(track, channel, pitch, time, duration, volume)
binfile = open('output.mid', 'wb')
midi1.writeFile(binfile)
binfile.close()
