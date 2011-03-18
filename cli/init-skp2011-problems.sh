#!/bin/zsh -f

setopt braceccl

typeset -A color name time
set -A color A Geel B Rood C Blauw D Wit E Groen
set -A name A "Laura Croft" B "Het Land van CH" C "Gecodeerde berichten" D "Bescherm een medestudent" E "Sorteer de kogels"
set -A time A 3 B 3 C 3 D 2 E 15

for l in {A-E}; do
	szp addproblem $l $time[$l] $name[$l] $color[$l] ~/skp2011/input/$l.in ~/skp2011/output/$l.out ~/szp4/cli/check.sh
done
