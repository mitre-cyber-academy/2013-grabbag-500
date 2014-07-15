Name: Corporate Language

Description: You recently learned that Duckpond Industries was developing a
secret language with which to create their next big product. After a bit of
dumpster diving, you've recovered what you believe is the latest spec. A crafty
bit of social engineering has provided you with a program which you believe
contains a prototype of their flagship product. Can you figure it out?

How to Solve: Participants must implement a Ballad virtual machine based on
the spec provided. When they run the program, they will have to answer two
questions based around esoteric languages. The answers to the questions are
stored in solution/proginput.txt. For the test implementation of the VM, the
solution will appear when the following command is run:

./vm.py ../dist/chall.mid < ../solution/proginput.txt

from the ballad/ directory. This will output the flag.

NOTE:
Time permitting, additional layers will be added to this challenge, but this
should be sufficiently rigorous for the time being.

What to distribute:
dist/challenge-archive.zip

Flag: MCA-11121C41