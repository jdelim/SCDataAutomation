import csv
import pandas as pd
import os
import traceback

COL_1, COL_2, COL_3 = "EVENT_ID", "SESSION_ID", "AGE"
COL_4, COL_5, COL_6 = "GRADE", "ORG_ID", "GENDER_ID"
COL_7, COL_8, COL_9 = "ETHNICITY_ID", "STUDENT_CODE", "POSTAL_CODE"
COL_10, COL_11, COL_12 = "IS_RETURNING_STUDENT_FLAG", "STUDENT_FIRST_NAME", "STUDENT_LAST_NAME"

def readCSV(csv_file_path: str):
    try:
        with open(csv_file_path, mode='r', newline='') as file:
            csv_reader = csv.reader(file)
            rows = []
            for row in csv_reader:
                converted_row = []
                for val in row:
                    # convert to int if digit
                    if val.isdigit():
                        converted_row.append(int(val))
                    else:
                        converted_row.append(val)
                rows.append(converted_row)
            return rows
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found!")
    except Exception as e:
        print(f"An error has occurred: {e}")

def clean_gender(rows):
    # takes in rows (list of lists)
    mapping = {'M': 1, 'MALE': 1,
               'F': 2, 'FEMALE': 2,
               'O': 3, 'OTHER': 3, 'NP': 3, 'OTHER/NP': 3}
    data = []
    for row in rows:
        new_row = []
        for val in row:
            if isinstance(val, str):
                new_val = mapping.get(val.upper(), val)
            else:
                new_val = val
            new_row.append(new_val)
        data.append(new_row)
    return data

def create_tsv_with_headers(file_path: str) -> bool:
    headers = [
        COL_1, COL_2, COL_3,
        COL_4, COL_5, COL_6,
        COL_7, COL_8, COL_9,
        COL_10, COL_11, COL_12
    ]
    try:
        df = pd.DataFrame(columns=headers)
        df.to_csv(file_path, sep="\t", index=False)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return True
        else:
            print(f"Error! File {file_path} was not created or is empty!")
            return False
    except Exception as e:
        print(f"Error! Failed to create TSV file {file_path}: {e}")
        print("TRACEBACK:")
        print(traceback.format_exc)
        return False

def pretty_print(data):
    # Convert all values to strings for consistent formatting
    str_rows = [[str(val) for val in row] for row in data]

    # Find the max width for each column
    col_widths = [max(len(row[i]) for row in str_rows) for i in range(len(str_rows[0]))]

    # Build each formatted row as a string with padding
    lines = []
    for row in str_rows:
        formatted_row = " | ".join(val.ljust(col_widths[i]) for i, val in enumerate(row))
        lines.append(formatted_row)
    
    # Join all rows with newline characters and return as one string
    return "\n".join(lines)

def main():
    #my_data = readCSV('data/Uncommon_Goods_Student_Demographics.csv')
    #print(pretty_print(clean_gender(my_data)))
    create_tsv_with_headers('data/test1.tsv')

if __name__ == "__main__":
    main()