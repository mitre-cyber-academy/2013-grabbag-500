_data:
#TODO - change these to the correct values:
SEC:1f0a07114201001741084c2e0852392e245f4242545c612a5145
X:576a6b266b78696f647770365e5b504d651d
Y:566b647329627e2f70336565767c6f7e4c4e4c494e0b414e5f5440565e5e1d4828372d6739222e3b2421302466
#Y:48656c6c6f2c2074686572652c20776861742773207570
_text:
#m0 = counter
#m1 = length
#m2 = offset in statmem
#m3 = return offset
#Load X onto the stack
movim m0, X_OFF
movim m1, LEN_X #Length of x now in math reg
add m1, m0
OFF_T:
lstat s0, m0 
push s0
inc m0 #i ++, jump
jlt m0, m1, OFF_T

#Using s7 as start of stack, init to zero, so okay to leave
#And save the starting offset on stack of the second one:
movis s6, LEN_X

movim m0, Y_OFF
movim m1, LEN_Y #Length of y now in math reg
add m1, m0
OFF_T2:
lstat s0, m0 
push s0
inc m0 #i ++, jump
jlt m0, m1, OFF_T2

#Push the last message onto the stack:
movim m0, SEC_OFF
movim m1, LEN_SEC #Length of x now in math reg
add m1, m0
OFF_T3:
lstat s0, m0 
push s0
inc m0 #i ++, jump
jlt m0, m1, OFF_T3
#Put the starting offset for SEC into s5: 
movrm m0, s6
movim m1, LEN_Y
add m0, m1
movrs s5, m0

#Put 2 into m7 for addition
movim m7, 2
#Now, all of the messages should be on the stack. `decrypt' the first one:
xor m0, m0
xor m3, m3 #this will contain the even sequence
movim m1, LEN_X #put length of x into m1
movrm m2, s7 #Put the start of X into m3
OFF_T4:
#Load the first value into s0:
stget s0, m2
movrm m4, s0
#xor it:
xor m4, m3
#put back into s0:
movrs s0, m4
#and put back on stack:
stput m2, s0
#at end, increment address, counter and 2x number:
inc m0
inc m2
add m3, m7
jlt m0, m1, OFF_T4

#Now, repeat for the other string:
xor m0, m0
xor m3, m3 #this will contain the odd sequence
inc m3
movim m1, LEN_Y #put length of y into m1
movrm m2, s6 #Put the start of Y into m3
OFF_T5:
#Load the first value into s0:
stget s0, m2
movrm m4, s0
#xor it:
xor m4, m3
#put back into s0:
movrs s0, m4
#and put back on stack:
stput m2, s0
#at end, increment address, counter and 2x number:
inc m0
inc m2
add m3, m7
jlt m0, m1, OFF_T5

#Next, print the first message
#Get it's length:
movis s0, LEN_X
print s7, s0
#Sum the lengths of the various strings as a
# starting offset for the password buffer
movim m2, LEN_SEC
movrm m0, s5 #offset from zero for x
add m0, m2
read m0, m2 #read in at most LEN_SEC

#Put the length of the next message in s0:
movis s0, LEN_Y
#Print out the next message:
print s6, s0
#The number read in will be in m2
#First, we need LEN_SEC somewhere
movim m3, LEN_SEC
#Then, get how many are left to read:
sub m3, m2
#This is how many to read. Add the number
# we read to the start offset of the last one
add m0, m2
#And read, starting at m2, m3 bytes
read m0, m3
add m0, m3
#Okay, so, ending at m0, with length LEN_SEC, we have the passphrase
# The secret message starts at s5 and has length len-sec.
movim m4, LEN_SEC
movrm m5, s5
movrm m6, s5
add m5, m4
#Now, m5 should have the end of the secret, and m0 has the end of the pphrase
#Begin to decrypt the flag string:
OFF_T6:
#For loop body:
stget s0, m0
stget s1, m5
movrm m2, s0
movrm m3, s1
xor m2, m3
movrs s0, m2
stput m5, s0
dec m0 #increment our byte location
dec m5
jgte m5, m6, OFF_T6
#
##Now, print out the message:
#movis s0, LEN_SEC
#movim m0, LEN_SEC
#movrm m1, s5
#add m0, m1
#movrs s5, m0
movrs s0, m4
print s5, s0
