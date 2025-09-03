import csv
import pandas as pd
import os
import traceback
from difflib import get_close_matches
from utils import *

COL_1, COL_2, COL_3 = "EVENT_ID", "SESSION_ID", "AGE"
COL_4, COL_5, COL_6 = "GRADE", "ORG_ID", "GENDER_ID"
COL_7, COL_8, COL_9 = "ETHNICITY_ID", "STUDENT_CODE", "POSTAL_CODE"
COL_10, COL_11, COL_12 = "IS_RETURNING_STUDENT_FLAG", "STUDENT_FIRST_NAME", "STUDENT_LAST_NAME"

def readCSV(csv_file_path: str) -> list[list[str]] | None:
    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            rows = []
            for row in csv_reader:
                if not row:
                    continue
                converted_row = []
                for val in row:
                    converted_row.append(str(val)) # everything stays a string
                rows.append(converted_row)
                #     if val.isdigit():
                #         converted_row.append(int(val))
                #     else:
                #         converted_row.append(val)
                # rows.append(converted_row)
            return rows
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found!")
    except Exception as e:
        print(f"An error has occurred: {e}")

def manual_find_column(column_name: str, column_name_list: list) -> int:
    for col_ind, col in enumerate(column_name_list):
        if column_name.upper() == col.upper():
            return col_ind
    return None

def clean_column(column_name: str, raw_rows: list[list]) -> list[list [str]]: #FIXME have it return strings only
    mappings = create_mapping(column_name)
    normalized_mappings = {}
    for k, v in mappings.items():
        normalized_key = normalize(k)
        normalized_mappings[normalized_key] = v
    
    col_pos = None
    first_row = raw_rows[0]
    updated_rows = [first_row]
    
    # find which column to check
    for col_ind, col in enumerate(raw_rows[0]):
        if column_name.upper() == col.upper():
            col_pos = col_ind
            break
        
    #if col_pos is None, call manual_find_column with user input
    if col_pos is None:
        input_col_name = input(f"Column {column_name} not found! Please enter the name of the column closest to \'{column_name}\'" +
                        " on the CSV file!")
        col_pos = manual_find_column(input_col_name, raw_rows[0])
        
    # assign values from mappings
    for row in raw_rows[1:]:
        new_row = row[:]
        raw_value = row[col_pos]
        normalized_value = normalize(raw_value)
        
        # 1) check for exact match
        data_id = normalized_mappings.get(normalized_value)
        
        # 2) substring scan on normalized keys
        if data_id is None:
            for key, value in normalized_mappings.items():
                if key in normalized_value or normalized_value in key:
                    data_id = value
                    break
    
        # 3) fuzzy match on normalized keys
        if data_id is None:
            matches = get_close_matches(normalized_value, normalized_mappings.keys(), n=1, cutoff=0.6)
            if matches:
                suggested_key = matches[0]
                confirm = input(
                    f"No exact match for '{raw_value}'. Did you mean '{suggested_key}'? (y/n): "
                )
                if confirm.lower().startswith("y"):
                    data_id = normalized_mappings[suggested_key]
        
        if data_id is None: 
            print(f"No match found for '{raw_value}'. Keeping original value.")
            data_id = raw_value
            
        new_row[col_pos] = str(data_id) # wrap cleaned value as string
        updated_rows.append(new_row)
        
    return updated_rows

def insert_tsv_values(file_path: str, cleaned_rows: list[list[str]]):
    tsv_headers = [
        COL_1, COL_2, COL_3,
        COL_4, COL_5, COL_6,
        COL_7, COL_8, COL_9,
        COL_10, COL_11, COL_12
    ]
    matched_indices = {}
    tsv_headers_dict = dict(tsv_headers)
    print(tsv_headers_dict)
    cleaned_headers = cleaned_rows[0]
    
    # match cleaned_row headers to tsv_headers indices
    
    # iterate over headers of the cleaned rows
    # for header in cleaned_headers:
        
    
    return

def create_tsv_with_headers(file_path: str) -> bool:
    """"
    Creates a .tsv file in the desired file path with headers that match the EVENT_STUDENT_DEMOGRAPHICS table in Snowflake.

    Args:
        file_path (str): enter the desired file path and filename. e.g. 'data/example.tsv'

    Returns:
        bool: Returns True if .tsv file successfully created, false otherwise.
    """
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

def pretty_print(rows: list[list]) -> None:
    """
    Prints a list of lists in a tabular format.
    """
    if not rows:
        print("No data.")
        return

    # find max width for each column
    col_widths = [max(len(str(item)) for item in col) for col in zip(*rows)]

    for row in rows:
        formatted = " | ".join(str(item).ljust(width) for item, width in zip(row, col_widths))
        print(formatted)
    print("\n")


def main():
    # mycolumns = ['ethnicity', 'gender', 'organization']
    # my_data = readCSV('data/Uncommon_Goods_Student_Demographics.csv')
    # pretty_print(my_data)
    # for column in mycolumns:
    #     cleaned_data = clean_column(column, my_data)
    # pretty_print(cleaned_data)    
    # print(create_tsv_with_headers('data/example.tsv'))
    pass

    

if __name__ == "__main__":
    main()