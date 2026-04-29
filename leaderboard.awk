BEGIN {
	FS=","
	OFS=","
}

#1->wins, 2->losses, 3->draws

{
	if ($1 == "DRAW"){
		if ($2 in l[$7]){
			l[$7][$2][3]++
		}
		else {
			l[$7][$2][1]=0
			l[$7][$2][2]=0
			l[$7][$2][3]=1
			l[$7][$2][4]=0
		}
		if ($3 in l[$7]){
			l[$7][$3][3]++
		}
		else {
			l[$7][$3][1]=0
			l[$7][$3][2]=0
			l[$7][$3][3]=1
			l[$7][$3][4]=0
		}
	}
	else {
		if ($4 in l[$7]){
			l[$7][$4][1]++
		}
		else {
			l[$7][$4][1]=1
			l[$7][$4][2]=0
			l[$7][$4][3]=0
			l[$7][$4][4]=0
		}
		if ($5 in l[$7]){
			l[$7][$5][2]++
		}
		else {
			l[$7][$5][1]=0
			l[$7][$5][2]=1
			l[$7][$5][3]=0
			l[$7][$5][4]=0
		}
	}
}

END {
	n=split(games, arr, ",") #https://www.geeksforgeeks.org/linux-unix/built-functions-awk
	for (x=1; x<=n; x++){
		i=arr[x]
		if (i in l){
			for (j in l[i]){
				if (l[i][j][2] == 0) {l[i][j][4]="UNDEF"}
				else {l[i][j][4]=l[i][j][1]/l[i][j][2]}
				l[i][j][5]=l[i][j][1]+l[i][j][2]+l[i][j][3]
				print i "," j "," l[i][j][1] "," l[i][j][2] "," l[i][j][3] "," l[i][j][4]
			}
		}
	}
}
