#!/bin/bash
#--------------------------------------------------------------------------------
#General comments:
#ni is name of ith user name; pi passwd; hpi hash of input passwd; hi stored hash; vi verification status
#--------------------------------------------------------------------------------
#const-like var declaration
readonly num_attempts=3
#--------------------------------------------------------------------------------
# Color definitions
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
RESET='\033[1;0m'
#--------------------------------------------------------------------------------
#Printing helpers
PFX="${CYAN}\t||\t${RESET}"
println() { echo -e "${PFX}$@"; }
readln() { IFS= read -r -p "$(echo -e "${PFX}$1${YELLOW}")" "$2"; }
readln_silent() { IFS= read -r -s -p "$(echo -e "${PFX}$1")" "$2"; echo; }
#--------------------------------------------------------------------------------
#Terminal decor
#--------------------------------------------------------------------------------
#ASCII art title
	clear

	#Make space
	println ""
	println ""

	# Title: TriGrid Engine
	println "${CYAN}"
	println "${CYAN}████████╗██████╗ ██╗ ██████╗ ██████╗ ██╗██████╗ "
	println "${CYAN}╚══██╔══╝██╔══██╗██║██╔════╝ ██╔══██╗██║██╔══██╗"
	println "${CYAN}   ██║   ██████╔╝██║██║  ███╗██████╔╝██║██║  ██║"
	println "${CYAN}   ██║   ██╔══██╗██║██║   ██║██╔══██╗██║██║  ██║"
	println "${CYAN}   ██║   ██║  ██║██║╚██████╔╝██║  ██║██║██████╔╝"
	println "${CYAN}   ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝ "
	println "${BLUE}                ENGINE${RESET}"
	println ""

	# Grid motif (representing games)
	println "${YELLOW}      ┌───┬───┬───┐"
	println "${YELLOW}      │ X │ O │   │"
	println "${YELLOW}      ├───┼───┼───┤"
	println "${YELLOW}      │   │ X │ O │"
	println "${YELLOW}      ├───┼───┼───┤"
	println "${YELLOW}      │ O │   │ X │"
	println "${YELLOW}      └───┴───┴───┘${RESET}"
	println ""

	# Tagline
	println "${GREEN}A NumPy-powered framework for:${RESET}"
	println "${CYAN}  • Tic-Tac-Toe${RESET}"
	println "${CYAN}  • Othello${RESET}"
	println "${CYAN}  • Connect-4${RESET}"
	println ""

	# Footer line
	println "${BOLD_RED}====================================================${RESET}"
	println "${BLUE}         Deterministic Grid Strategy Engine${RESET}"
	println "${BOLD_RED}====================================================${RESET}"

	#Make space
	println ""
	println ""
show_title(){
	#Don't mind the name; I changed the function since clearing everytime lead to flicker
	tput cup 29 0
	tput ed
}
#End ASCII art title
#--------------------------------------------------------------------------------
#check for users.tsv
if [ ! -f ./users.tsv ]; then touch users.tsv; fi
#--------------------------------------------------------------------------------
#Taking input for user_1
show_title
i=0
while [ $i -lt $num_attempts ]; do
	readln "${CYAN}Enter username for user_1${RESET} " u1
	if [[ "$u1" != ""  && ! "$u1" =~ ^.*,.*$ ]]; then break
	else
		i=$(($i+1))
		if [ "$u1" == "" ]; then
			println "${RED}Username may not be empty.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
		else
			println "${RED}Username may not contain comma.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
		fi
		if [[ $i -eq ${num_attempts} ]]; then
			println "${BOLD_RED}You took too many attempts. Exiting...${RESET}"
			exit #exits script
		fi
	fi
done
n1=$(echo $u1 | sha256sum) #This should handle issues of special characters
#End input for user_1
#--------------------------------------------------------------------------------
#Name existence for user_1
l1=$(grep -E "^$n1	" users.tsv)
if [ $? -eq 0 ]; then v1=1; else v1=0; fi
#End Name existence for user_1
#--------------------------------------------------------------------------------
#New print function for user1
printu1(){
	show_title
	println "${GREEN}Hello, ${u1}!"
	println "$1"
}
readu1_silent() {
	show_title
	println "${GREEN}Hello, ${u1}!"
	IFS= read -r -s -p "$(echo -e "${PFX}$1")" "$2"; echo;
}
#END New print function for user1
#--------------------------------------------------------------------------------
#Conditional stuff for user_1
if [ $v1 -eq 1 ]; then
	#check hashed password
	h1=$(echo -e "${l1#$n1	}")
	i=0
	while [ $i -lt $num_attempts ]; do
		readu1_silent "${CYAN}Password for user_1${RESET} " p1
		hp1=$(echo $p1 | sha256sum)
		if [ "$h1" == "$hp1" ]; then break
		else
			v1=0
			i=$(($i+1))
			printu1 "${RED}Incorrect password.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
			if [[ $i -eq ${num_attempts} ]]; then
				printu1 "${BOLD_RED}Attempts for correct password expired. Exiting...${RESET}"
				exit #exits script
			fi
			readln "${CYAN}Type something to enter password again ${RESET}" throw
		fi
	done
else
	#sign up
	printu1 "${BLUE}Username not found. Do you wish to sign up?${RESET}"
	println "${CYAN}If yes, press 'y' and then press 'Enter' or 'Return'. Otherwise, enter a random string which isn't 'y'${RESET}"
	readln "" reg
	if [ $reg == 'y' ]; then
		i=0
		while [ $i -lt $num_attempts ]; do
			readu1_silent "${CYAN}Password for user_1${RESET} " p1
			readu1_silent "${CYAN}Confirm Password${RESET} " pc1
			if [ "$pc1" == "$p1" ]; then
				hp1=$(echo $p1 | sha256sum)
				echo -e "${n1}\t${hp1}" >> users.tsv
				break
			else
				i=$(($i+1))
				println "${RED}Passwords not matching.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
				if [[ $i -eq ${num_attempts} ]]; then
					println "${BOLD_RED}You took too many attempts. Exiting...${RESET}"
					exit
				fi
				readln "${CYAN}Type something to enter password again " throw
			fi
		done
		v1=1
	else
		printu1 "${BLUE}Exiting...${RESET}"
		exit
	fi
fi
#End Conditional stuff for user_1
#--------------------------------------------------------------------------------
#Taking input for user_2
show_title
i=0
while [ $i -lt $num_attempts ]; do
	readln "${CYAN}Enter username for user_2${RESET} " u2
	if [ "$u2" != "$u1" ]; then
		if [[ "$u2" != "" && ! "$u2" =~ ^.*,.*$ ]]; then break
		else
			i=$(($i+1))
			if [ "$u2" == "" ]; then
				println "${RED}Username may not be empty.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
			else
				println "${RED}Username may not contain comma.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
			fi
			if [[ $i -eq ${num_attempts} ]]; then
				println "${BOLD_RED}You took too many attempts. Exiting...${RESET}"
				exit #exits script
			fi
		fi
	else
		i=$(($i+1))
		println "${RED}user_2 may not have same username as user_1.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
		if [[ $i -eq ${num_attempts} ]]; then
			println "${BOLD_RED}You took too many attempts. Exiting...${RESET}"
			exit
		fi
	fi
done
n2=$(echo $u2 | sha256sum)
#End input for user_2
#--------------------------------------------------------------------------------
#New print function for user2
printu2(){
	show_title
	println "${GREEN}Hello, ${u2}!"
	println "$1"
}
readu2_silent() {
	show_title
	println "${GREEN}Hello, ${u2}!"
	IFS= read -r -s -p "$(echo -e "${PFX}$1")" "$2"; echo;
}
#END New print function for user2
#--------------------------------------------------------------------------------
#Name existence for user_2
l2=$(grep -E "^$n2	" users.tsv)
if [ $? -eq 0 ]; then v2=1; else v2=0; fi
#End existence for user_2
#--------------------------------------------------------------------------------
#Conditional stuff for user_2
if [ $v2 -eq 1 ]; then
	#check hashed password
	h2=$(echo -e "${l2#$n2	}")
	i=0
	while [ $i -lt $num_attempts ]; do
		readu2_silent "${CYAN}Password for user_2${RESET} " p2
		hp2=$(echo $p2 | sha256sum)
		if [ "$h2" == "$hp2" ]; then break
		else
			v2=0
			i=$(($i+1))
			println "${RED}Incorrect password.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
			if [[ $i -eq ${num_attempts} ]]; then
				printu2 "${BOLD_RED}Attempts for correct password expired. Exiting...${RESET}"
				exit #exits script
			fi
			readln "${CYAN}Type something to enter password again ${RESET}" throw
		fi
	done
else
	#sign up
	printu2 "${BLUE}Username not found. Do you wish to sign up?${RESET}"
	println "${CYAN}If yes, press 'y' and then press 'Enter' or 'Return'. Otherwise, enter a random string which isn't 'y'${RESET}"
	readln "" reg
	if [ $reg == 'y' ]; then
		i=0
		while [ $i -lt $num_attempts ]; do
			readu2_silent "${CYAN}Password for user_2${RESET} " p2
			readu2_silent "${CYAN}Confirm Password${RESET} " pc2
			if [ "$pc2" == "$p2" ]; then
				hp2=$(echo $p2 | sha256sum)
				echo -e "${n2}\t${hp2}" >> users.tsv
				break
			else
				i=$(($i+1))
				println "${RED}Passwords not matching.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
				if [[ $i -eq ${num_attempts} ]]; then
					println "${BOLD_RED}You took too many attempts. Exiting...${RESET}"
					exit
				fi
				readln "${CYAN}Type something to enter password again ${RESET}" throw
			fi
		done
		v2=1
	else
		printu2 "${BLUE}Exiting...${RESET}"
		exit
	fi
fi
#End Conditional stuff for user_2
#--------------------------------------------------------------------------------
#Conditionally calling game.py
clear
if [[ $v1 -eq 1 && $v2 -eq 1 ]]; then
	python3 game.py "${u1}" "${u2}"
fi
#EOF
