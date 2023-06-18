import os

# Loop over all the files in the directory
for index in range(3500, 7686):
    file_path = f'version_1/Question_scrapper/Qdata/{index}/{index}.txt'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        print(f"Before modification - File: {file_path}")
        print(f"Lines: {lines}")

        # Check if the first line contains the specific text
        if lines and "Read problems" in lines[0] or"Read problem" in lines[0] :
            # Remove the first line
            lines = lines[1:]

        print(f"After modification - File: {file_path}")
        print(f"Lines: {lines}")

        # Write the modified contents back to the file
        with open(file_path, 'w') as file:
            file.writelines(lines)
    else:
        print(f"File not found: {file_path}")
