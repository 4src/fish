BEGIN{FS=","; Bins=5}
NR==1{for(i=1;i<=NF;i++) {
	 if ($i ~ /^[A-Z]/) isNum[i] 
         if ($i ~ /[!\-\+]$/) isGoal[i] 
	 if (i in isNum) {lo[i] = 1000000000; hi[i]= -100000000000}}}
NR>1{ for(i=1;i<=NF;i++) {
	 D[NR-1][i] = $i
	 if( (i in isNum)  && (! (i in isGoal)) && ($i != "?"))  {
             if ($i<lo[i]) lo[i] = $i
             if ($i>hi[i]) hi[i] = $i }}}
END{  for (r in D) {
	for (c in D[r]) {
	   if (c in isNum) {
	      x = D[r][c]
	      D[r][c] = x=="?"	? x : int(.5 + Bins*(x - lo[c])/(hi[c]-lo[c] + 0.0000000001))  }
        }}
      print(".")
      for(r in D) {if ((r % 100)==0) print(r);
        for(i = 1;i<=NF;i++) 
	   if (! (i in isGoal))
            for(j=i+1;j<=NF;j++) 
	       if (! (j in isGoal))
                  for(k=j+1;k<=NF;k++) 
	            if (! (k in isGoal))
      	              for(l=k+1;l<=NF;l++) 
	                 if (! (l in isGoal)) { m++
      	                   F[D[r][i],  D[r][j], D[r][k], D[r][l]]++  }}
     for (x in F) print(x " " log(F[x]/m)) }


