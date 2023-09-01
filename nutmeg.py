#!/usr/bin/env python3 -B

from nutm import *

for era,row,cols, in eras(csv(the.file), size=20): pass

print(cols.stats()) 

