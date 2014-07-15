LOAD_WORD:
#m0 = counter
#m1 = length
#m2 = offset in statmem
#m3 = return offset
xor m0, m0
lstat s0, m2 
push s0
inc m0 #i ++, jump
inc m2 #add the next character on the next loop
jlt m0, m1, LOAD_WORD
ret m3
