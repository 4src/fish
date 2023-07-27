TITLE=`gawk 'sub(/^# /,"")' $1`
cat<<EOF
<!DOCTYPE html>
<html>
<head>
  <title>$TITLE</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css?family='Roboto Mono'">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="b.css">
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.0.7/css/all.css">
  <script type="text/x-mathjax-config">
    MathJax.Hub.Config({
      extensions: ["tex2jax.js"],
      jax: ["input/TeX", "output/HTML-CSS"],
      tex2jax: {
        inlineMath: [ ['$','$'], ["\\(","\\)"] ],
        displayMath: [ ['$$','$$'], ["\\[","\\]"] ],
        processEscapes: true
      },
      "HTML-CSS": { fonts: ["TeX"] }
    });
  </script>
  <script type="text/javascript"
     src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js">
   </script>
   <style>
    body  { margin: 0;
            padding: 15px;
            font-family: Tahoma, Verdana, Segoe, sans-serif;
          }
    pre   { background-color: black;
            color: white;
            padding: 10px;
          }
    h1    { margin-top: 0px; padding-top: 0px; 
            color: rgb(72,14,120); 
            border-top: 1px solid rgb(72,14,120);
          } 
    
    .admonition       { border: 1px solid #EEE; box-shadow: 3px 3px 3px black; }
    .admonition-title { font-weight: bold; }
    .summary          { padding-left: 10px; padding-right: 10px;
                        margin-left:  20px; margin-right:  20px; 
                        background-color: #DDD; 
                      }
  </style>
</head>
<body>
  <img src="dots3.png" width=200 align=left
       style="margin-bottom: 0px; padding-bottom: 0px;"> 
  <p style="text-align:right;">
  
      <a  href="index.html">home</a> :: 
      <a href="">src</a> ::
      <a href="">issues</a><br> 
    
    <span style="float:left;color:rgb(72,14,120);"> 
  
      <b>SE+AI: a programmer's guide</b>

    </span><br>
    <span style="float:left;">
  
       <a href="license">&copy;2023</a> by <a href="">Tim Menzies</a>
  
    </span>
  </p>
  <br clear=all>
EOF

FMT= -x toc -x codehilite -x tables -x fenced_code -x footnotes -x attr_list -x admonition
gawk '
  sub("\"\"\":","") { print"```"); IN=1 }
  sub(":\"\"\"","") { print "\n``` python"; IN=0 }
                END {if (N==1) print "```"}
' | 
python3 -m markdown $(FMT) 

cat<<EOF
  </body>
</html>
EOF
