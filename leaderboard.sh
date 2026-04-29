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
# Following priority is to be interpretted as grouping constraints: ($7)
#	game, game_rev;

#--------------------------------------------------------------------------------
# Color definitions
RED='\033[1;31m'
GREEN='\033[1;32m'
BLINK_GREEN='\033[1;5;4;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
GOLD='\033[1;38;2;255;193;7m'
RESET='\033[1;0m'
#--------------------------------------------------------------------------------
#Assisting function(s)
PFX="${GOLD}\t||\t${RESET}"
PFXTITLE="${GOLD}\t||\t"
println() { echo -e "${PFX}$@"; }
printtitle() { echo -e "${PFXTITLE}$@"; }
#--------------------------------------------------------------------------------
# Terminal decorprint_leaderboard_title(){

clear
printtitle 
printtitle ' _        _______  _______  ______   _______  _______  ______   _______  _______  _______  ______'
printtitle '( \      (  ____ \(  ___  )(  __  \ (  ____ \(  ____ )(  ___ \ (  ___  )(  ___  )(  ____ )(  __  \' 
printtitle '| (      | (    \/| (   ) || (  \  )| (    \/| (    )|| (   ) )| (   ) || (   ) || (    )|| (  \  )'
printtitle '| |      | (__    | (___) || |   ) || (__    | (____)|| (__/ / | |   | || (___) || (____)|| |   ) |'
printtitle '| |      |  __)   |  ___  || |   | ||  __)   |     __)|  __ (  | |   | ||  ___  ||     __)| |   | |'
printtitle '| |      | (      | (   ) || |   ) || (      | (\ (   | (  \ \ | |   | || (   ) || (\ (   | |   ) |'
printtitle '| (____/\| (____/\| )   ( || (__/  )| (____/\| ) \ \__| )___) )| (___) || )   ( || ) \ \__| (__/  )'
printtitle '(_______/(_______/|/     \|(______/ (_______/|/   \__/|/ \___/ (_______)|/     \||/   \__/(______/ '
println
println "                              ${BLINK_GREEN}TriGrid Engine • Multi-Game Leaderboard${RESET}"
println
                                                                                                   
#--------------------------------------------------------------------------------

a=("connect_4" "Othello" "TicTacToe")

file=$(gawk -v games="${a[*]}" -f leaderboard.awk  history.csv)

#making the sort command: -k part

cm=$(echo -e $7"\n"$1"\n"$2"\n"$3"\n"$4"\n"$5"\n"$6 | awk '{ if ($1 > 0){printf "-k %d,%dr ",$1,$1} else if ($1<0) {printf "-k %d,%d ",-$1,-$1}}')

echo -en ${GOLD}
sort -t "," ${cm} <<< "$file" | column -s, -o " || " -t | sed 's/^/\t||\t/' #echo not needed here.
echo -en ${RESET}
