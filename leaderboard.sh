#!/bin/bash

# history.csv: Draw_status,pl1_uname,pl2_uname,Winner,Loser,Date,Game
# Winner,Loser = NA,NA if DRAW, else contain approp usernames
# Beware of username format: may contain '$'. Disallowed ',' in username.
# $1 to $6: sort priorities
# Some possible priorities (more important priority to be given earlier):
#	uname, uname_rev --> 2 or -2
#	wins, wins_rev --> 3 or -3 as input
#	losses, losses_rev --> 4 or -4 as input
#	draws, draws_rev --> 5 or -5
#	win_loss_ratio, win_loss_ratio_rev --> 6 or -6
#	tot_played, tot_played_rev --> 7 or -7
# TODO setup logic which allows dealing with min conditions, ex. if wins,losses_rev,username then win_loss_ratio & tot_played become redundant
# Following priority is to be interpretted as grouping constraints: ($7)
#	game, game_rev; default: game
#
# TODO learn about the column utility

#grouping: pass an array to awk for game order

if [ $7 -eq 1 ]; then
	a=("connect_4" "othello" "TicTacToe")
else
	a=("TicTacToe" "othello" "connect_4")
fi

file=$(gawk -v games="${a[*]}" -f leaderboard.awk  history.csv)

#making the sort command: -k part

cm=$(echo -e $1"\n"$2"\n"$3"\n"$4"\n"$5"\n"$6 | awk '{ if ($1 > 0){printf "-k %d,%d ",$1,$1} else {printf "-k %d,%dr",-$1,-$1}}')

echo $(sort -t "," ${cm} <<< "$file") 


