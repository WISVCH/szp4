#!/bin/sh
#sudo dropdb szp
#sudo createdb szp

# szp() {
# 	echo cli/szp.py $@
# }

./manage.py syncdb --noinput

echo Creating superuser \'admin\':
./manage.py createsuperuser --username=admin --email=szp@ch.tudelft.nl

#alias szp="~/bzr/szp4/cli/szp.py"

szp setcontest INITIALIZED 2009-10-03 'Delfts Kampioenschap Programmeren 2009' 'Delft'

szp addautojudge aj0

szp addcompiler submission.c "gcc -Wall -O2 -g -std=c99 -lm submission.c -o submission" "./submission" .c "GNU C Compiler" 4.3.2
szp addcompiler submission.cc "g++ -Wall -O2 -g -std=c++98 -lm submission.cc -o submission" "./submission" .cc "GNU C++ Compiler" 4.3.2
szp addcompiler 'Problem${LETTER}.java' 'javac -O Problem${LETTER}.java' 'java Problem${LETTER}' .java 'Sun Java Compiler' 1.6.0_12

szp addteamclass 0 Jury
szp addteamclass 1 Contestants
szp addteamclass 2 Business
szp addteamclass 3 Spectators

szp addteam 'Test team 1' 'TU Delft' 1 'EWI WPS' team0
#szp addteam 'Test team 2' 'TU Delft' 1 'DW 160.2' team02
#szp addteam 'OMG IPONIEZ' 'Appel' 2 'Cupertino' team03

#pushd /home/jeroen/szptest
#szp addproblem A 30 Obfuscate Pink A.in A.out check
#szp addproblem B 30 Epluribus Blue B.in B.out check
#szp addproblem C 30 Coneasoup Yellow C.in C.out check
#popd

#szp addjudge testjudge test

#szp setcontest RUNNING
