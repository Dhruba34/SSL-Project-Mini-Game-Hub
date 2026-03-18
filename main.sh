#!/bin/bash
#--------------------------------------------------------------------------------
#General comments:
#ni is name of ith user name; pi passwd; hpi hash of input passwd; hi stored hash; vi verification status
#--------------------------------------------------------------------------------
#check for users.tsv
if [ ! -f ./users.tsv ]; then touch users.tsv; fi
#--------------------------------------------------------------------------------
#Taking input for user_1
echo "Enter username for user_1"
read n1
echo "Password for user_1"
read p1
#End input for user_1
#--------------------------------------------------------------------------------
#Name existence for user_1
l1=$(grep $n1 users.tsv)
if [ $? -eq 0 ]; then v1=1; else v1=0; fi
#Name existence for user_1
#--------------------------------------------------------------------------------
#Conditional stuff for user_1
if [ $v1 -eq 1 ]; then
	#check hashed password
	h1=$(echo -e "${l1}" | cut -d$'\t' -f 2)
	hp1=$(echo $p1 | sha256sum)
	if [ h1!=hp1 ]; then v1=0; fi
else
	#sign up
	echo "Username not found. Do you wish to sign up?"
	echo "If yes, press \'y\' and then press \'Enter\' or \'Return\'. Otherwise, enter a random string which isn't \'y\'"
	read reg
	if [ reg=='y' ]; then
		echo "Confirm Password"
		read pc1
		if [ pc1==p1 ]; then
			hp1=$(echo $p1 | sha256sum)
			echo -e "${n1}\t${p1}" >> users.tsv
		else
			echo "Incorrect password. Exiting..."
			exit #exits the script
		fi
	else
		echo "Exiting..."
		exit
	fi
fi
#End Conditional stuff for user_1
#--------------------------------------------------------------------------------
#Taking input for user_2
echo "Enter username for user_2"
read n2
echo "Password for user_2"
read p2
#End input for user_2
#--------------------------------------------------------------------------------
#Name existence for user_2
l2=$(grep $n2 users.tsv)
if [ $? -eq 0 ]; then v2=1; else v2=0; fi
#Name existence for user_2
#--------------------------------------------------------------------------------
#Conditional stuff for user_2
if [ $v2 -eq 1 ]; then
	#check hashed password
	h2=$(echo -e "${l2}" | cut -d$'\t' -f 2)
	hp2=$(echo $p2 | sha256sum)
	if [ h2!=hp2 ]; then v2=0; fi
else
	#sign up
	echo "Username not found. Do you wish to sign up?"
	echo "If yes, press \'y\' and then press \'Enter\' or \'Return\'. Otherwise, enter a random string which isn't \'y\'"
	read reg
	if [ reg=='y' ]; then
		echo "Confirm Password"
		read pc2
		if [ pc2==p2 ]; then
			hp2=$(echo $p2 | sha256sum)
			echo -e "${n2}\t${p2}" >> users.tsv
		else
			echo "Incorrect password. Exiting..."
			exit #exits the script
		fi
	else
		echo "Exiting..."
		exit
	fi
fi
#End Conditional stuff for user_1
#--------------------------------------------------------------------------------
#Conditionally calling game.py
if [[ v1 && v2 ]]; then
	python3 game.py ${n1} ${n2}
fi
#EOF
