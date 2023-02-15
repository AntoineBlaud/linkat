#include <stdio.h>
#include <stdlib.h>
#include<unistd.h> 

int marker() {
    // Change to the tmp folder
    chdir("/tmp");

    // Create 40 files
    for (int i = 0; i < 40; i++) {
        char filename[30];
        sprintf(filename, "/tmp/fileflow_%d", i);
        FILE *fp = fopen(filename, "w");
        fclose(fp);
    }

    // Delete the files 
   for (int i = 0; i < 40; i++) {
        char filename[30];
        sprintf(filename, "/tmp/fileflow_%d", i);
        remove(filename);
    }

    printf("marker writed.\n");

    return 0;
}