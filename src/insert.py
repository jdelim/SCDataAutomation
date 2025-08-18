import csv
import pandas as pd
import os
import traceback

COL_1, COL_2, COL_3 = "EVENT_ID", "SESSION_ID", "AGE"
COL_4, COL_5, COL_6 = "GRADE", "ORG_ID", "GENDER_ID"
COL_7, COL_8, COL_9 = "ETHNICITY_ID", "STUDENT_CODE", "POSTAL_CODE"
COL_10, COL_11, COL_12 = "IS_RETURNING_STUDENT_FLAG", "STUDENT_FIRST_NAME", "STUDENT_LAST_NAME"

# read and clean CSV

def readCSV(csv_file_path: str) -> list[list[int | str]] | None:
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

def clean_gender(rows: list[list]) -> list[list [str | int]]:
    # takes in rows (list of lists)
    mapping = {'M': 1, 'MALE': 1,
               'F': 2, 'FEMALE': 2,
               'O': 3, 'OTHER': 3, 'NP': 3, 'OTHER/NP': 3}
    updated_data = [rows[0]]
    gender_column = find_column(rows[0], "GENDER")

    if gender_column is None:
        raise ValueError("Gender column cannot be identified!")
    
    for row in rows[1:]:
        new_row = row[:]
        gender_str = row[gender_column]
    # FIXME just realized, we can probably just create one function to clean column
    pass

def clean_ethnicity(rows: list[list]) -> list[list [str | int]]:
    mapping = {'AMERICAN INDIAN': 1, 'ALASKA NATIVE': 1,
               'ASIAN': 2, 'BLACK': 3, 'AFRICAN AMERICAN': 3,
               'HISPANIC': 4, 'LATINO': 4, 'WHITE': 5,
               'NATIVE HAWAIIAN': 6, 'PACIFIC ISLANDER': 6,
               'MULTIRACIAL': 7, 'OTHER': 8}
    updated_data = [[rows[0]]]
    # check which column (index value) to check
    ethnicity_column = find_column(rows[0], "ETHNICITY")
    
    # error check if column is not found
    if ethnicity_column is None:
        raise ValueError("Ethnicity column cannot be identified!")
    
    for row in rows[1:]: # skip over the column names row
        new_row = row[:]
        eth_str = row[ethnicity_column]

        if isinstance(eth_str, str): # FIXME doesn't take into account if some rows have already been turned into id (int)
            eth_upper = eth_str.upper()

        # check for exact match
        ethnicity_id = mapping.get(eth_upper)
        # partial match
        if ethnicity_id is None:
            for key, value in mapping.items():
                if key in eth_upper:
                    ethnicity_id = value
                    break
        # raise error if no match found
        if ethnicity_id is None:
            raise ValueError(f"{eth_str} not found in map!")
        new_row[ethnicity_column] = ethnicity_id
        updated_data.append(new_row)
    return updated_data

def clean_organization(rows: list[list]) -> list[list [str | int]]:
    pass 


def find_column(columns: list, column_name: str) -> int | None: # takes in first row (columns) of our CSV rows
    # FIXME doesn't take into account partial matches
    for col_ind, column in enumerate(columns):
        if column_name.upper() == column.upper():
            return col_ind
    return None
    

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


def main():
    my_data = readCSV('data/Uncommon_Goods_Student_Demographics.csv')
    print(clean_ethnicity(my_data))
    #create_tsv_with_headers('data/test1.tsv')

if __name__ == "__main__":
    main()