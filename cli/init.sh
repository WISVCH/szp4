#!/bin/bash
dropdb szp
createdb szp

/home/jeroen/bzr/szp4/manage.py syncdb --noinput
/home/jeroen/bzr/szp4/manage.py createsuperuser --username=admin --email=szp@ch.tudelft.nl

szp setcontest INITIALIZED 2008-10-04 'test contest' 'test location'

szp addautojudge 127.0.0.1


szp addcompiler submission.c "gcc -Wall -O2 -g -std=c99 -lm submission.c -o submission" "./submission" .c "GNU C Compiler" 4.3.1
szp addcompiler submission.cc "g++ -Wall -O2 -g -std=c++98 -lm submission.cc -o submission" "./submission" .cc "GNU C++ Compiler" 4.3.1
szp addcompiler 'Problem${LETTER}.java' 'javac -O Problem${LETTER}.java' 'java Problem${LETTER}' .java 'Sun Java Compiler' 1.6.0_07

szp addteamclass 1 testers

szp addteam tester qa 1 'dw 160' 127.0.0.1 team1 test

pushd /home/jeroen/szptest
szp addproblem A 30 Obfuscate Pink A.in A.out check
szp addproblem B 30 Epluribus Blue B.in B.out check
szp addproblem C 30 Coneasoup Yellow C.in C.out check
popd

szp addjudge testjudge test

szp setcontest RUNNING
