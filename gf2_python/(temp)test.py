import sys
import os

path_test = os.getcwd() + "/(temp)text_file.txt"

file_test = open(path_test)
print(file_test.read(23))

current_pos = file_test.tell()

file_test.seek(0)
linelengths = []
i = 0
for line in file_test:
    i += 1
    if len(linelengths) == 0:
        linelengths.append(len(line))
    else:
        linelengths.append(len(line) + linelengths[-1])
num_line = i

current_line = ''
pos_in_line = ''
file_test.seek(current_pos)

for n in range(num_line):
    if n == 0:
        if file_test.tell() <= linelengths[n]:
            current_line = 1
            pos_in_line = file_test.tell()
        else:
            current_line = ''
            pos_in_line = ''
    elif file_test.tell() <= linelengths[n] and file_test.tell() > linelengths[n-1]:
        current_line = n + 1
        pos_in_line = file_test.tell() - linelengths[n-1]

marker = 0

file_test.seek(0)

for line in file_test:
    marker += 1
    if marker == current_line:
        print(line, " "*(pos_in_line-3), "^")

file_test.seek(current_pos)

file_test.close()
