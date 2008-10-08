#!/bin/bash
/home/szp/szp4/manage.py syncdb --noinput
/home/szp/szp4/manage.py createsuperuser --username=admin --email=szp@ch.tudelft.nl

szp setcontest INITIALIZED 2008-10-04 'Delfts Kampioenschap Programmeren' 'Delft'

szp addautojudge 131.180.158.26
szp addautojudge 131.180.158.27
szp addautojudge 131.180.158.28
szp addautojudge 131.180.158.29
szp addautojudge 131.180.158.30

szp addcompiler submission.c "gcc -Wall -O2 -g -std=c99 -lm submission.c -o submission" "./submission" .c "GNU C Compiler" 4.3.1
szp addcompiler submission.cc "g++ -Wall -O2 -g -std=c++98 -lm submission.cc -o submission" "./submission" .cc "GNU C++ Compiler" 4.3.1
szp addcompiler 'Problem${LETTER}.java' 'javac -O Problem${LETTER}.java' 'java Problem${LETTER}' .java 'Sun Java Compiler' 1.6.0_07

szp addteamclass 1 contestants
szp addteamclass 2 spectators

pushd /home/szp/dkp2008
szp addproblem A 10 "Lanterns" Zeegroen a.in a.out check
szp addproblem B 3 "Burger King" Wit b.in b.out check
szp addproblem C 3 "Labyrinth" Geel c.in c.out check
szp addproblem D 3 "Walking the dog" Blauw d.in d.out check
szp addproblem E 3 "Power cables to sewer pipes" Groen e.in e.out check
szp addproblem F 3 "Sascha" Hardroze f.in f.out check
szp addproblem G 60 "Choir" Oranje g.in g.out check
szp addproblem H 3 "Recycling proteins" Rood h.in h.out check
popd

#szp setcontest RUNNING
