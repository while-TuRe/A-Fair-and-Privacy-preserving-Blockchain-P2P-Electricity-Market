offers = [1,2,2,5,0]
m = 2
s = 0
b = 0
for i in range(1,6):
    if offers[5-i]==0 or offers[5-i]<=m :
        b=b
    else:
        b = offers[5-i]
for i in range(5):
    if offers[i]==0 or offers[i]>=m :
        s=s
    else:
        s = offers[i]
print(s,b)