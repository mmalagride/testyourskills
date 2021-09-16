import random
from pandas import *
height = 50
width  = 50
matrix = []
for h in range(height):
    row = []
    for w in range(width):
        if h in (0,height-1) or w in (0,width-1):
            cell = 1 #Fix the outer boundary to 1
        else:
            cell = random.randint(0,1) # Randomly Assign 0 or 1 in space between boundary
        row.append(cell)
    matrix.append(row)
print(DataFrame(matrix).to_string(index=False,header=False))