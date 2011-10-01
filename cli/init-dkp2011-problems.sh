#!/bin/zsh -f

setopt braceccl

typeset -A color
set -A color A Oranje B Wit C Blauw D Paars E Rood F Groen G Felroze H Geel I Roodpaars J Roze

for l in {A-J}; do
	cd ~/dkp2011/$l
	NAME=`grep 'name=' domjudge-problem.ini | cut -d '=' -f 2`
	TIME=`grep 'timelimit=' domjudge-problem.ini | cut -d '=' -f 2`
	COMPARE=`grep 'special_compare=' domjudge-problem.ini | cut -d '=' -f 2`
	if [ -n "$COMPARE" ]; then
		COMPARE=~/dkp2011/compare_$COMPARE
	else
		COMPARE=~/szp4/cli/check.sh
	fi
	szp addproblem $l $TIME $NAME $color[$l] $l.in $l.out $COMPARE
done
