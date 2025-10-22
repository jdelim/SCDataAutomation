import csv
import pandas as pd
import os
import traceback
from difflib import get_close_matches
from .utils import *

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

def clean_column(column_name: str, raw_rows: list[list]) -> list[list [str]]: 
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

def map_csv_to_tsv_columns(csv_file_path: str) -> dict[str, str | None] | None: #TODO add fuzzy matchI
    """
    Maps a cleaned CSV file's column names to TSV column names. Maps through exact mapping, dictionary/synonym lookup, and fuzzy match.
    Manual user matching will be handled through the GUI.

    Args:
        csv_file_path (str): Path to CSV file.

    Returns:
        dict[str, str] | None: Dictionary mapping TSV column names to CSV column names.
        E.g., {'EVENT_ID': 'event_id', 'SESSION_ID': 'sessionID', ... , 'STUDENT_FIRST_NAME', 'first name', ...}.
    
    Raises:
        ValueError: If csv_file_path is empty or TSV headers are invalid.
        FileNotFoundError: If the CSV file doesn't exist.
        IOError: If the CSV file cannot be read.
        KeyboardInterrupt: If user cancels the mapping process.
    """
    
    if not csv_file_path:
        raise ValueError("CSV file path cannot be empty!")

    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"File '{csv_file_path}' does not exist!")
    
    tsv_headers = [
        COL_1, COL_2, COL_3,
        COL_4, COL_5, COL_6,
        COL_7, COL_8, COL_9,
        COL_10, COL_11, COL_12
    ]
    
    # read in CSV headers
    try:
        csv_rows = readCSV(csv_file_path)
    except Exception as e:
        raise IOError(f"Error reading CSV file: {e}") from e
    
    if csv_rows is None or len(csv_rows) == 0:
        raise IOError("Could not read CSV file or file is empty!")
    
    csv_headers = csv_rows[0]
    
    # check if csv headers is empty
    if ( # checking if first row is just data or actual headers
        not csv_headers
        or all(h.strip() == "" for h in csv_headers)
        or all(h.strip().isdigit() for h in csv_headers)
        or len(set(csv_headers)) == 1
    ):
        raise ValueError("CSV file has no headers")
    
    # normalize CSV headers and check for empty headers
    csv_headers = [str(header).strip() for header in csv_headers]
    if '' in csv_headers:
        print("Warning: CSV contains empty column headers!")
        
    column_mapping = {}
    used_csv_columns = set()
    
    print("\n=== Column Mapping ===")
    print(f"CSV has {len(csv_headers)} columns")
    print(f"TSV expects {len(tsv_headers)} columns")
    print("\nCSV Columns:", ", ".join(csv_headers))
    print()
    
    # load synonym mapping from json
    try:
        synonym_mapping = load_column_synonyms()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"WARNING: Could not load synonyms: {e}. Skipping synonym matching")
        synonym_mapping = {}
    
    # automatic mapping
    for tsv_col in tsv_headers:
        matched = False
        
        # look for exact match (case-insensitive, normalized)
        for csv_col in csv_headers:
            if not csv_col:
                continue
            if tsv_col == csv_col.upper():
                if csv_col in used_csv_columns:
                    # skips duplicate mappings
                    continue
                column_mapping[tsv_col] = csv_col
                used_csv_columns.add(csv_col)
                matched = True
                break
        
        if not matched and tsv_col in synonym_mapping:
            synonyms = synonym_mapping[tsv_col]
            for csv_col in csv_headers:
                if not csv_col:
                    continue
                if csv_col in used_csv_columns:
                    continue
                # check if csv col matches synonym
                csv_col_upper = csv_col.upper()
                if csv_col_upper in [syn.upper() for syn in synonyms]:
                    column_mapping[tsv_col] = csv_col
                    used_csv_columns.add(csv_col)
                    matched = True
                    break
        
        if not matched:
            column_mapping[tsv_col] = None
        
    return column_mapping
        
    
def transfer_csv_to_tsv_with_mapping():
    pass

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