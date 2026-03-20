#!/bin/bash
#--------------------------------------------------------------------------------
#General comments:
#ni is name of ith user name; pi passwd; hpi hash of input passwd; hi stored hash; vi verification status
#--------------------------------------------------------------------------------
#const-like var declaration
readonly num_attempts=3
#--------------------------------------------------------------------------------
#check for users.tsv
if [ ! -f ./users.tsv ]; then touch users.tsv; fi
#--------------------------------------------------------------------------------
#Taking input for user_1
i=0
while [ $i -lt $num_attempts ]; do
	echo "Enter username for user_1"
	read u1
	if [ "$u1" != "" ]; then break
	else
		i=$(($i+1))
		echo "Username may not be empty. $((${num_attempts}-${i})) attempts left."
		if [[ $i -eq ${num_attempts} ]]; then
			echo "You took too many attempts. Exiting..."
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
		echo "Password for user_1"
		read -s p1
		hp1=$(echo $p1 | sha256sum)
		if [ "$h1" == "$hp1" ]; then break
		else
			v1=0
			i=$(($i+1))
			echo "Incorrect password. $((${num_attempts}-${i})) attempts left."
			if [[ $i -eq ${num_attempts} ]]; then
				echo "Attempts for correct password expired. Exiting..."
				exit #exits script
			fi
		fi
	done
else
	#sign up
	echo "Username not found. Do you wish to sign up?"
	echo "If yes, press \'y\' and then press \'Enter\' or \'Return\'. Otherwise, enter a random string which isn't \'y\'"
	read reg
	if [ $reg == 'y' ]; then
		i=0
		while [ $i -lt $num_attempts ]; do
			echo "Password for user_1"
			read -s p1
			echo "Confirm Password"
			read -s pc1
			if [ $pc1 == $p1 ]; then
				hp1=$(echo $p1 | sha256sum)
				echo -e "${n1}\t${hp1}" >> users.tsv
				break
			else
				i=$(($i+1))
				echo "Passwords not matching. $((${num_attempts}-${i})) attempts left."
				if [[ $i -eq ${num_attempts} ]]; then
					echo "You took too many attempts. Exiting..."
					exit
				fi
			fi
		done
	else
		echo "Exiting..."
		exit
	fi
fi
#End Conditional stuff for user_1
#--------------------------------------------------------------------------------
#Taking input for user_2
i=0
while [ $i -lt $num_attempts ]; do
	echo "Enter username for user_2"
	read u2
	if [ "$u2" != "$u1" ]; then
		if [ "$u2" != "" ]; then break
		else
			i=$(($i+1))
			echo "Username may not be empty. $((${num_attempts}-${i})) attempts left."
			if [[ $i -eq ${num_attempts} ]]; then
				echo "You took too many attempts. Exiting..."
				exit #exits script
			fi
		fi
	else
		i=$(($i+1))
		echo "user_2 may not have same username as user_1. $((${num_attempts}-${i})) attempts left."
		if [[ $i -eq ${num_attempts} ]]; then
			echo "You took too many attempts. Exiting..."
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
		echo "Password for user_2"
		read -s p2
		hp2=$(echo $p2 | sha256sum)
		if [ "$h2" == "$hp2" ]; then break
		else
			v2=0
			i=$(($i+1))
			echo "Incorrect password. $((${num_attempts}-${i})) attempts left."
			if [[ $i -eq ${num_attempts} ]]; then
				echo "Attempts for correct password expired. Exiting..."
				exit #exits script
			fi
		fi
	done
else
	#sign up
	echo "Username not found. Do you wish to sign up?"
	echo "If yes, press \'y\' and then press \'Enter\' or \'Return\'. Otherwise, enter a random string which isn't \'y\'"
	read reg
	if [ $reg == 'y' ]; then
		i=0
		while [ $i -lt $num_attempts ]; do
			echo "Password for user_2"
			read -s p2
			echo "Confirm Password"
			read -s pc2
			if [ $pc2 == $p2 ]; then
				hp2=$(echo $p2 | sha256sum)
				echo -e "${n2}\t${hp2}" >> users.tsv
				break
			else
				i=$(($i+1))
				echo "Passwords not matching. $((${num_attempts}-${i})) attempts left."
				if [[ $i -eq ${num_attempts} ]]; then
					echo "You took too many attempts. Exiting..."
					exit
				fi
			fi
		done
	else
		echo "Exiting..."
		exit
	fi
fi
#End Conditional stuff for user_2
#--------------------------------------------------------------------------------
#Conditionally calling game.py
if [[ v1 && v2 ]]; then
	python3 game.py "${u1}" "${u2}"
fi
#EOF
