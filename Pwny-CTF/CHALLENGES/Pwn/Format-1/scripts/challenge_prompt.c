#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

void setup() {
    // you can ignore this. it's just here to make netcat work nicely
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
}

void vuln(char *string)
{
  volatile int target;
  char buffer[64];

  target = 0;

  sprintf(buffer, string);
  
  if(target == 0xdeadbeef) {
      printf("FLAG\n");
  }
}

int main(int argc, char **argv)
{
  setup();
  vuln(argv[1]);
}