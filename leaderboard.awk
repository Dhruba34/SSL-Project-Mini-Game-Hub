BEGIN {
	FS=","
	OFS=","
}

#1->wins, 2->losses, 3->draws

{
	if ($1 == "DRAW"){
		l[$7][$2][3]++
		l[$7][$3][3]++
	}
	else {
		l[$7][$4][1]++
		l[$7][$5][2]++
	}
}

END {
	n=split(games, arr, " ") #https://www.geeksforgeeks.org/linux-unix/built-functions-awk
	for (x=1; x<=n; x++){
		i=arr[x]
		if (i in l){
			for (j in l[i]){
				if (l[i][j][2] == 0) {l[i][j][4]="inf"}
				else {l[i][j][4]=l[i][j][1]/l[i][j][2]}
				l[i][j][5]=l[i][j][1]+l[i][j][2]+l[i][j][3]
				print i "," j "," l[i][j][1] "," l[i][j][2] "," l[i][j][3] "," l[i][j][4]
			}
		}
	}
}
