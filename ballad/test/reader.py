import midi

z = midi.read_midifile('output.mid')
for track in z:
	hist = [0] * 11
	for event in track:
		if isinstance(event, midi.NoteEvent):
			idx = event.pitch % 11
			hist[idx] += 1
	l = sum(hist)
	hist = [(0.0 + x) / l for x in hist]
	print hist
	print sum(hist)

