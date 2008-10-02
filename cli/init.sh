#!/bin/bash
#szp setcontest INITIALIZED 2008-09-28 'test contest' 'test location'

#szp addautojudge 127.0.0.1


szp addcompiler submission.c "gcc -Wall -O2 -g -std=c99 -lm submission.c -o submission" "./submission" .c "GNU C Compiler" 4.3.1
szp addcompiler submission.cc "g++ -Wall -O2 -g -std=c++98 -lm submission.cc -o submission" "./submission" .cc "GNU C++ Compiler" 4.3.1
szp addcompiler 'Problem${LETTER}.java' 'javac Problem${LETTER}.java' 'java Problem${LETTER}' .java 'Sun Java Compiler' 1.6.0_07
