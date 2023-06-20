
# read lines from index.txt (Problem names)
with open('version_1/Question_scrapper/Qdata/index.txt', 'r') as f:
    lines = f.readlines()

stop_words = ["Example", "Input", "Input:", "Example:", "###Input", "###Input:"]

# Open a new text file for writing
with open('version_1/TF_IDF/qdata.txt', 'w') as output_file:
    for index, line in enumerate(lines, start=1):
        file_path = f'version_1/Question_scrapper/Qdata/{index}/{index}.txt'
        with open(file_path, 'r') as f:
            file_lines = f.readlines()
        concatenated_line = ""
        for i in file_lines:
            current_line = i.strip()
            if any(word in current_line for word in stop_words):
                break
            concatenated_line += current_line + " "
        # Write the concatenated line to the output file
        output_file.write(concatenated_line.strip() + "\n")


