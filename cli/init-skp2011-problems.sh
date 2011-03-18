#!/bin/zsh -f

setopt braceccl

typeset -A color name time
set -A color A Oranje B Oranje C Oranje D Oranje E Oranje
set -A name A "Laura Croft" B "Het Land van CH" C "Gecodeerde berichten" D "Bescherm een medestudent" E "Sorteer de kogels"
set -A time A 2 B 1 C 5 D 1 E 5

for l in {A-E}; do
	szp addproblem $l $time[$l] $name[$l] $color[$l] ~/skp2011/input/$l.in ~/skp2011/output/$l.out ~/szp4/cli/check.sh
done
