print("please enter 2 value and select operation")
num1=int(input("num1:"))
num2=int(input("num2:"))
result= num1+num2
print("sum:",result)
#write a python script that should take two values from users. it should also let user input and display result on screem
num1=int(input("num1:"))
num2=int(input("num2:"))
op=input("select (+,-,*/):")
if op== '+':
    result=num1+num2
else: result=num1-num2
print("answer:",result)


marks=[60,65,63,70,70,80,85]
print(sum(marks)/len(marks))
