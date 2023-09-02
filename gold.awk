
/^#/ {print; next}
/^func(tion)?[ \t]+[A-Z][^\(]*\(/ {
    split($0,tmp,/[ \t\(]/)
    klass = tmp[2] }
{ gsub(/[ \t]_/," " klass) }
{ print  gensub(/\.([^0-9\\*\\$\\+])([a-zA-Z0-9_]*)/, 
                "[\"\\1\\2\"]","g", $0) }
            
