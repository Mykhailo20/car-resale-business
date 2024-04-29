import csv

def get_file_length(filename):
    with open(filename, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        row_count = 0
        for row in csv_reader:
            row_count += 1

        # The first row contains the record headers
        return row_count - 1