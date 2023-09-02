# vim : set filetype=awk :
BEGIN { FS=","; big=1E30;  DOT=sprintf("%c",46) }
NR==1 { for(i=1;i<=NF;i++0) if ($i !~ /X$/) names[i] = $i 
        for(i in names) if (i ~ /^A-Z/) def(num,i); num0(num[i]) }
NR>1  { for(i in names) if ($i != "?") data[NR-1][i] = num1(num[i], coerce($i)) }

function num0(i)   { i["n"] = i["mu"] = i["m2"] = i["sd"] = 0; i["hi"] = -(i["lo"] = big) }
function num1(i,x) {
 	 i["n"]++
 	 d      = x - i["mu"]
 	 i["m"]   += d/i["n"]
 	 i["m2"]  += d*(x - i["m2"])
 	 return x }

function coerce(x,    y) {y=x+0;	return x==y ? y : x }

function def(a,i) { a[i][0]; del a[i][0] }
