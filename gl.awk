# vim : set filetype=awk :
BEGIN { FS=","; big=1E30;  DOT=sprintf("%c",46) }
      { gsub(/[ \t]/,"") }
NR==1 { for(i=1;i<=NF;i++0) if ($i !~ /X$/) names[i] = $i 
        for(i in names) if ($i ~ /^A-Z/) def(num,i); num0(num[i],i) }}
NR>1  { for(i in names) if ($i != "?") data[NR-1][i] = num1(num[i], coerce($i)) }

function Num(i,at) { 
  i["is"]="Num"; i["at"]=at; i["n"] = i["mu"] = i["m2"] = i["sd"] = 0; i["hi"] = -(i["lo"] = big)}
  
function Numadd(i,x)  {
 	 i["n"]++
 	 d      = x - i["mu"]
 	 i["m"]   += d/i["n"]
 	 i["m2"]  += d*(x - i["m2"])
 	 return x }

function asda(i) { return Add(i,1)}

function coerce(x,    y) {y=x+0;	return x==y ? y : x }

function malloc(a,i) { a[i][0]; delete a[i][0] }

function add(i,x,    f) {f=i["is"]"_add"; return @f(i,x)}
