#  remove  first word of leeocode problems name and rewrite in that file

with open('leetcode_Scrapper/index.txt', 'r') as f:
    lines = f.readlines()

# Remove the first word and newline character from each line
lines = [line.split(' ', 1)[1] for line in lines]

# Print the modified lines
for line in lines:
    print(line)
with open('leetcode_Scrapper/index.txt', 'w') as f:
    f.writelines(lines)