import csv
import sys

if len(sys.argv) < 2:
    raise ValueError('Please Input CSV File Name')
    
file = open(sys.argv[1])
reader = csv.reader(file)

subjects = next(reader)[1:]
sub_marks = [0] * len(subjects)
sub_top_names = [""] * len(subjects)

ranks =  [0] * 3
rank_names = [""] * 3

for marks in reader:
    name = marks.pop(0)
    total = 0
    for i in range(len(marks)):
        mark = int(marks[i])
        total += mark
        if mark > sub_marks[i]:
            sub_marks[i] = mark
            sub_top_names[i] = name

    if total > ranks[0]:
        ranks[2] = ranks[1]
        ranks[1] = ranks[0]
        ranks[0] = total
        rank_names[0] = name
    
    elif total > ranks[1]:
        ranks[2] = ranks[1]
        ranks[1] = total
        rank_names[1] = name

    elif total > ranks[2]:
        ranks[2] = total
        rank_names[2] = name

        
for sub,name in zip(subjects,sub_top_names):
    print("Topper in " +  sub  +" is " + name)

print("...")

print(f"Best students in the class are {rank_names[0]} first rank, {rank_names[1]} second rank, {rank_names[2]} third rank")

file.close()