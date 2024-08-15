import os
import csv

# Step 1: Define the directory path
directory_path = r'C:\Users\matsa\Documents\mit\summer24\cochrane\allfiles'

# Step 2: Retrieve the file names
file_names = os.listdir(directory_path)

# Step 3: Sort the file names alphabetically
file_names.sort()

# Step 4: Define the output CSV file path
output_csv_path = r'C:\Users\matsa\Documents\mit\summer24\cochrane\allfilenames.csv' 

# Step 5: Write the file names to the CSV
with open(output_csv_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['File Name'])  # Writing the header
    for file_name in file_names:
        writer.writerow([file_name])

print(f"File names have been written to {output_csv_path}")