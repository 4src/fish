#!/usr/bin/env gawk -f
BEGIN                       { First =1;Code=1 }
/usr.bin.env/               { next }
/vim:.*set/                 { next }
sub(/^"""/,"")              { if (!First) print "```\n\n"; First=0; next; Code=0}
sub(/"""$/,"\n\n```python") { print $0 ; next; Code=1}
                            { print $0 }
