#include <stdio.h>
#include <sys/stat.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char* argv[])
{
	struct stat fStats;
	FILE* inFile1, *inFile2, *outFile;
	char* f1Cons, *f2Cons;
	size_t f1Size, f2Size;
	int count;
	if(argc < 4)
	{
		printf("Usage: %s <firstIn> <secondIn> <outName>\n", argv[0]);
		exit(0);
	}
	inFile1 = fopen(argv[1], "rb");
	if(inFile1 == NULL)
	{
		perror("Couldn't open input file for reading");
		exit(1);
	}
	inFile2 = fopen(argv[2], "rb");
	if(inFile2 == NULL)
	{
		perror("Couldn't open input file for reading");
		exit(2);
	}
	outFile = fopen(argv[3], "wb");
	if(outFile == NULL)
	{
		perror("Couldn't open output file for writing");
		exit(3);
	}

	stat(argv[1], &fStats);
	f1Size = fStats.st_size;
	stat(argv[2], &fStats);
	f2Size = fStats.st_size;
	if(f1Size != f2Size)
	{
		fprintf(stderr, "Error: input files of unequal length %lu vs %lu\n",
			f1Size, f2Size);
		exit(4);
	}
	f1Cons = (char*) malloc(f1Size * sizeof(char));
	fread(f1Cons, fStats.st_size, 1, inFile1);
	f2Cons = (char*) malloc(f1Size * sizeof(char));
	fread(f2Cons, fStats.st_size, 1, inFile2);
	fclose(inFile1);
	fclose(inFile2);
	for(count = 0; count < f1Size; count ++)
	{
		printf("%02x | %02x\n", f1Cons[count], f2Cons[count]);
		fprintf(outFile, "%02x", f1Cons[count] ^ f2Cons[count]);
	}
	fclose(outFile);
	/* Remove pesky \0's at the end: */
	truncate(argv[3], 2*f1Size);
	return 0;
}
