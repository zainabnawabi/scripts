num=[12,14,9,7]
print(num[0])
print(num[1])
print(num[2])
print(num[0])
print(num[3])

#marks
marks=[60,50,55,70]
marks.append(90)
marks.insert(0,61)
marks.remove(90)
for x in marks:
    print(x*2)

    #calculate average
    marks=[60.65,63,70]
    sum=0
    for x in marks:
        sum=sum+x
    avg=sum/len(marks)
    print(avg)

#another way

#even number
marks=[1,2,3]
sum=0
count=0
for x in marks:
    if x%2==0:
    sum=sum+x
    count=count+1
