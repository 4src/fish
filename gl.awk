BEGIN { FS="," }
NR==1 { for(i=1;i<=NF;i++0) if ($i !~ /X$/) names[i] = $i }
NR>1  { for(i in names) data[NR-1][i] = $i == ($i+0) ? ($i+0) : $i } 
