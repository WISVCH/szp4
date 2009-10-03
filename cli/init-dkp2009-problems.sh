#!/bin/zsh -f

setopt braceccl

typeset -A color name
set -A color A "Green" B "Blue" C "Purple" D "Pink" E "Yellow" F "Red" G "White" H "Black" I "Orange"
set -A name A "All-Out Arctic Warfare" B "Hedge Maze Relay Race" C "Brick Stacking" D "Family Politics" E "Box City" F "Box Village" G "Word Search Puzzle" H "Blueprint" I "Typechecker"

for l in {A-I}; do
	szp addproblem $l 3 $name[$l] $color[$l] ~/dkp2009/testset/$l.in ~/dkp2009/testset/$l.out ~/szp4/cli/check.sh
done

