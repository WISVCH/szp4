#!/bin/zsh -f

setopt braceccl

typeset -A color name time
set -A color A Geel B Groen C Rood D Poepbruin
set -A name A "Lara Crofty" B "Klaverjassen" C "Het Land van CH" D "Het Delftsch Studenten Woordenboek"
set -A time A 10 B 10 C 10 D 10

for l in {A-D}; do
	szp addproblem $l $time[$l] $name[$l] $color[$l] files/testsets/$l/{$l:l}.in files/testsets/$l/{$l:l}.out ~/bzr/szp4/cli/check.sh
done
