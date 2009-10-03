#!/bin/zsh -f

setopt braceccl

typeset -A color name time
set -A color A Geel B Groen C Rood D Felroze E Zalmroze F Wit G Paars H Blauw I Zeegroen
set -A name A "All-Out Arctic Warfare" B "Hedge Maze Relay Race" C "Brick Stacking" D "Family Politics" E "Box City" F "Box Village" G "Word Search Puzzle" H "Blueprint" I "Typechecker"
set -A time A 8 B 4 C 8 D 30 E 20 F 1 G 6 H 1 I 1

for l in {A-I}; do
	szp addproblem $l $time[$l] $name[$l] $color[$l] ~/dkp2009/testset/$l.in ~/dkp2009/testset/$l.out ~/szp4/cli/check.sh
done

