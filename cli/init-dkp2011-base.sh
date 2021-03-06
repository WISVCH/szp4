#!/bin/sh
dropdb szp
createdb szp

# szp() {
# 	echo cli/szp.py $@
# }

./manage.py syncdb --noinput

echo Creating superuser \'admin\':
./manage.py createsuperuser --username=admin --email=szp@ch.tudelft.nl

szp setcontest INITIALIZED 2011-10-01 'Delfts Kampioenschap Programmeren 2011' 'Delft'

szp addautojudge aj1
szp addautojudge aj2
szp addautojudge aj3
szp addautojudge aj4
szp addautojudge aj5

szp addcompiler submission.c "gcc -Wall -O2 -g -std=c99 -lm submission.c -o submission" "./submission" .c "GNU C Compiler" 4.4.5
szp addcompiler submission.cc "g++ -Wall -O2 -g -std=c++98 -lm submission.cc -o submission" "./submission" .cc "GNU C++ Compiler"  4.4.5
szp addcompiler 'Problem${LETTER}.java' 'javac Problem${LETTER}.java' 'java -Xmx256M -Xms32M -Xss8M -server Problem${LETTER}' .java 'Sun Java Compiler' 1.6.0_26
#szp addcompiler 'SProblem${LETTER}.scala' 'scalac -optimise SProblem${LETTER}.scala' 'env JAVA_OPTS="-Xmx256M -Xms32M -server" scala SProblem${LETTER}' .scala 'Scala Compiler' 2.7.7
szp addcompiler 'Problem${LETTER}.cs' 'gmcs Problem${LETTER}.cs' 'mono Problem${LETTER}.exe' .cs 'Mono gmcs' 2.2.7

szp addteamclass 0 CHipCie
szp addteamclass 1 Contestants
szp addteamclass 2 Spectators
szp addteamclass 3 Companies

szp addteam 'TechNICie' 'CH' 0 'DW 01.010'
szp addteam 'Jury'      'CH' 0 'DW 01.010'

#szp addjudge -ip jury3 -team 2 marco
#szp addjudge -ip jury4 -team 2 wikash
#szp addjudge -ip jury5 -team 2 xanvier
