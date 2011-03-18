#!/bin/zsh -f

setopt braceccl

typeset -A color name time
set -A color A Lichtgroen B Blauw C Geel D Wit E Rood F Donkergroen G Paars H Bordeauxrood I Roze J Oranje 
set -A name A "Evolution" B "Have a Nice Day" C "Serial Numbers" D "Equal Is Not Really Equal" E "The Great Cleanup" F "Stock Market" G "Acrobat Reader" H "Farmer John" I "Imagine" J "My Cousin Obama"
set -A time A 2 B 1 C 5 D 1 E 5 F 2 G 3 H 3 I 2 J 3

for l in {A-J}; do
	szp addproblem $l $time[$l] $name[$l] $color[$l] ~/dkp2010/testdata/$l.in ~/dkp2010/testdata/$l.out ~/szp4/cli/check.sh
done
