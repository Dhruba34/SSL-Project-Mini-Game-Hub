#!/bin/bash
#--------------------------------------------------------------------------------
#General comments:
#ni is name of ith user name; pi passwd; hpi hash of input passwd; hi stored hash; vi verification status
#--------------------------------------------------------------------------------
#const-like var declaration
readonly num_attempts=3
#--------------------------------------------------------------------------------
# Color definitions
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
CYAN='\033[36m'
BOLD_RED='\033[1;31m'
RESET='\033[0m'
#--------------------------------------------------------------------------------
#check for users.tsv
if [ ! -f ./users.tsv ]; then touch users.tsv; fi
#--------------------------------------------------------------------------------
#Taking input for user_1
i=0
while [ $i -lt $num_attempts ]; do
	echo -e "${CYAN}Enter username for user_1${RESET}"
	read u1
	if [[ "$u1" != ""  && ! "$u1" =~ ^.*,.*$ ]]; then break
	else
		i=$(($i+1))
		if [ "$u1" == "" ]; then
			echo -e "${RED}Username may not be empty.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
		else
			echo -e "${RED}Username may not contain comma.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
		fi
		if [[ $i -eq ${num_attempts} ]]; then
			echo -e "${BOLD_RED}You took too many attempts. Exiting...${RESET}"
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
#Conditional stuff for user_1
if [ $v1 -eq 1 ]; then
	#check hashed password
	h1=$(echo -e "${l1#$n1	}")
	i=0
	while [ $i -lt $num_attempts ]; do
		echo -e "${CYAN}Password for user_1${RESET}"
		read -s p1
		hp1=$(echo $p1 | sha256sum)
		if [ "$h1" == "$hp1" ]; then break
		else
			v1=0
			i=$(($i+1))
			echo -e "${RED}Incorrect password.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
			if [[ $i -eq ${num_attempts} ]]; then
				echo -e "${BOLD_RED}Attempts for correct password expired. Exiting...${RESET}"
				exit #exits script
			fi
		fi
	done
else
	#sign up
	echo -e "${BLUE}Username not found. Do you wish to sign up?${RESET}"
	echo -e "${CYAN}If yes, press 'y' and then press 'Enter' or 'Return'. Otherwise, enter a random string which isn't 'y'${RESET}"
	read reg
	if [ $reg == 'y' ]; then
		i=0
		while [ $i -lt $num_attempts ]; do
			echo -e "${CYAN}Password for user_1${RESET}"
			read -s p1
			echo -e "${CYAN}Confirm Password${RESET}"
			read -s pc1
			if [ "$pc1" == "$p1" ]; then
				hp1=$(echo $p1 | sha256sum)
				echo -e "${n1}\t${hp1}" >> users.tsv
				break
			else
				i=$(($i+1))
				echo -e "${RED}Passwords not matching.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
				if [[ $i -eq ${num_attempts} ]]; then
					echo -e "${BOLD_RED}You took too many attempts. Exiting...${RESET}"
					exit
				fi
			fi
		done
	else
		echo -e "${BLUE}Exiting...${RESET}"
		exit
	fi
fi
#End Conditional stuff for user_1
#--------------------------------------------------------------------------------
#Taking input for user_2
i=0
while [ $i -lt $num_attempts ]; do
	echo -e "${CYAN}Enter username for user_2${RESET}"
	read u2
	if [ "$u2" != "$u1" ]; then
		if [[ "$u2" != "" && ! "$u2" =~ ^.*,.*$ ]]; then break
		else
			i=$(($i+1))
			if [ "$u2" == "" ]; then
				echo -e "${RED}Username may not be empty.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
			else
				echo -e "${RED}Username may not contain comma.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
			fi
			if [[ $i -eq ${num_attempts} ]]; then
				echo -e "${BOLD_RED}You took too many attempts. Exiting...${RESET}"
				exit #exits script
			fi
		fi
	else
		i=$(($i+1))
		echo -e "${RED}user_2 may not have same username as user_1.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
		if [[ $i -eq ${num_attempts} ]]; then
			echo -e "${BOLD_RED}You took too many attempts. Exiting...${RESET}"
			exit
		fi
	fi
done
n2=$(echo $u2 | sha256sum)
#End input for user_2
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
		echo -e "${CYAN}Password for user_2${RESET}"
		read -s p2
		hp2=$(echo $p2 | sha256sum)
		if [ "$h2" == "$hp2" ]; then break
		else
			v2=0
			i=$(($i+1))
			echo -e "${RED}Incorrect password.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
			if [[ $i -eq ${num_attempts} ]]; then
				echo -e "${BOLD_RED}Attempts for correct password expired. Exiting...${RESET}"
				exit #exits script
			fi
		fi
	done
else
	#sign up
	echo -e "${BLUE}Username not found. Do you wish to sign up?${RESET}"
	echo -e "${CYAN}If yes, press 'y' and then press 'Enter' or 'Return'. Otherwise, enter a random string which isn't 'y'${RESET}"
	read reg
	if [ $reg == 'y' ]; then
		i=0
		while [ $i -lt $num_attempts ]; do
			echo -e "${CYAN}Password for user_2${RESET}"
			read -s p2
			echo -e "${CYAN}Confirm Password${RESET}"
			read -s pc2
			if [ "$pc2" == "$p2" ]; then
				hp2=$(echo $p2 | sha256sum)
				echo -e "${n2}\t${hp2}" >> users.tsv
				break
			else
				i=$(($i+1))
				echo -e "${RED}Passwords not matching.${YELLOW} $((${num_attempts}-${i})) attempts left.${RESET}"
				if [[ $i -eq ${num_attempts} ]]; then
					echo -e "${BOLD_RED}You took too many attempts. Exiting...${RESET}"
					exit
				fi
			fi
		done
	else
		echo -e "${BLUE}Exiting...${RESET}"
		exit
	fi
fi
#End Conditional stuff for user_2
#--------------------------------------------------------------------------------
#Conditionally calling game.py
if [[ v1 -eq 1 && v2 -eq 1 ]]; then
	python3 game.py "${u1}" "${u2}"
fi
#EOF
