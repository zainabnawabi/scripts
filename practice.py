'''
#list comprehension

raw_s=["80", "90", "100", "110", "120","95","85", "75", "65", "55"]

cleaned_s = [int(i) for i in raw_s]
print(cleaned_s)

avg=sum(cleaned_s)/len(cleaned_s)
print("average=",avg)

#for better understanding

raw_s=["80", "90", "100", "110", "120","95","85", "75", "65", "55"]
cleaned_s=[]

for x in raw_s:
    numeric= int(x)

    cleaned_s.append(numeric)

print(cleaned_s)

#create a * pyramid pattern

n=int(input("enter no of rows:"))

spaces=n-1
stars=1
for i in range(n):
    print(" "*spaces + "*"*stars)
    spaces= spaces-1
    stars= stars+2


click_delays = ["450", "30", "500", "15", "620", "22"]

# Extract suspicious rapid clicks (< 100 ms) indicating potential bot activity
bot_clicks= [int(x) for x in click_delays if int(x) <100]

print("bot clicks:", bot_clicks)

"0123456"
print("0123456".find('1'))  # Output: 1


#Consider the variable g, and find the first index of the sub-string snow:
g = "Mary had a little lamb Little lamb, little lamb Mary had a little lamb \
Its fleece was white as snow And everywhere that Mary went Mary went, Mary went \
Everywhere that Mary went The lamb was sure to go"



user_logs = ["login", "click", "download", "logout"]

# range(len(user_logs)) generates: 0, 1, 2, 3
for index in range(len(user_logs)):
    print(f"Action #{index}: {user_logs[index]}")

'''

