#!/bin/zsh -f

setopt braceccl

typeset -A color name time
set -A color A "Green" B "Blue" C "Purple" D "Pink" E "Yellow" F "Red" G "White" H "Black" I "Orange"
set -A name A "All-Out Arctic Warfare" B "Hedge Maze Relay Race" C "Brick Stacking" D "Family Politics" E "Box City" F "Box Village" G "Word Search Puzzle" H "Blueprint" I "Typechecker"
set -A time A 30 B 30 C 30 D 30 E 30 F 30 G 30 H 30 I 30

for l in {A-I}; do
	szp addproblem $l $time[$l] $name[$l] $color[$l] ~/dkp2009/testset/$l.in ~/dkp2009/testset/$l.out ~/szp4/cli/check.sh
done

