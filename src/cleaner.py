import csv
import pandas as pd
import os
import json
import traceback
from difflib import get_close_matches
from utils import *

COL_1, COL_2, COL_3 = "EVENT_ID", "SESSION_ID", "AGE"
COL_4, COL_5, COL_6 = "GRADE", "ORG_ID", "GENDER_ID"
COL_7, COL_8, COL_9 = "ETHNICITY_ID", "STUDENT_CODE", "POSTAL_CODE"
COL_10, COL_11, COL_12 = "IS_RETURNING_STUDENT_FLAG", "STUDENT_FIRST_NAME", "STUDENT_LAST_NAME"

# HELPER FUNCTIONS

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
            return rows
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found!")
    except Exception as e:
        print(f"An error has occurred: {e}")

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

def manual_find_column(column_name: str, column_name_list: list) -> int:
    for col_ind, col in enumerate(column_name_list):
        if column_name.upper() == col.upper():
            return col_ind
    return None

def find_column_by_name(target_column: str, csv_headers: list[str]) -> int | None:
    """
    Finds the index of a column in CSV headers using exact match and synonym lookup.
    
    Args:
        target_column (str): The standard column name to find (e.g., "GENDER_ID")
        csv_headers (list[str]): List of column headers from the CSV
        
    Returns:
        int | None: Index of the matching column, or None if not found
    """
    # look for exact match
    for col_ind, csv_col in enumerate(csv_headers):
        if not csv_col:
            continue
        if target_column.upper() == csv_col.upper():
            return col_ind
        
    # synonym matching
    try:
        synonym_mapping = load_column_synonyms()
        if target_column in synonym_mapping:
            synonyms = synonym_mapping[target_column]
            for col_ind, csv_col in enumerate(csv_headers):
                if not csv_col:
                    continue
                csv_col_upper = csv_col.upper()
                if csv_col_upper in [syn.upper() for syn in synonyms]:
                    return col_ind
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"WARNING: Could not load column synonyms: {e}. Skipping synonym matching.")
    
    return None

# CORE FUNCTIONS

def clean_column(column_name: str, raw_rows: list[list]) -> list[list [str]]: 
    """
    Cleans a column by mapping its values to database IDs using exact match and substring matching.
    
    Args:
        column_name (str): The name of the column to clean (e.g., "GENDER_ID", "ETHNICITY_ID", "ORG_ID")
        raw_rows (list[list]): The CSV data with headers in the first row
        
    Returns:
        list[list[str]]: Updated rows with cleaned values replaced by their database IDs
    """
    # get mappings from key_ids.json
    mappings = create_mapping(column_name)
    
    # load value synonyms
    try:
        value_synonyms = load_value_synonyms()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"WARNING: Could not load value synonyms: {e}. Using only exact matching.")
        value_synonyms = {}
        
    # build normalized lookup table: normalized_value -> data_id
    # this includes both canonical values and their synonyms
    normalized_lookup = {}
    
    for original_key, data_id in mappings.items():
        # add the canonical form from database
        normalized_lookup[normalize(original_key)] = data_id
        
        # add synonyms if they exist for this column and value
        if column_name in value_synonyms and original_key in value_synonyms[column_name]:
            for synonym in value_synonyms[column_name][original_key]:
                normalized_lookup[normalize(synonym)] = data_id
                
    # find which column to clean
    csv_headers = raw_rows[0]
    col_pos = find_column_by_name(column_name, csv_headers)
    
    # ask user manually if col not found
    # If still not found, ask user manually
    if col_pos is None:
        input_col_name = input(
            f"Column {column_name} not found! Please enter the name of the column closest to '{column_name}' on the CSV file: "
        )
        col_pos = manual_find_column(input_col_name, csv_headers)
        
    # process rows and clean values
    first_row = raw_rows[0]
    updated_rows = [first_row]
    
    for row in raw_rows[1:]:
        new_row = row[:]
        raw_value = row[col_pos]
        normalized_value = normalize(raw_value)
        
        # 1) check for exact match on normalized value (includes all synonyms)
        data_id = normalized_lookup.get(normalized_value)
        
        # 2) substring scan on normalized keys
        # this handles cases like "Hispanic" matching "Hispanic or Latino"
        if data_id is None:
            for key, value in normalized_lookup.items():
                if key in normalized_value or normalized_value in key:
                    data_id = value
                    break
        
        # if no match found, keep original value
        if data_id is None: 
            print(f"No match found for '{raw_value}'. Keeping original value.")
            data_id = raw_value
            
        new_row[col_pos] = str(data_id)  # Convert to string for CSV consistency
        updated_rows.append(new_row)
        
    return updated_rows

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

def map_csv_to_tsv_columns(csv_file_path: str) -> dict[str, str | None] | None:
    """
    Maps a cleaned CSV file's column names to TSV column names. Maps through exact mapping and dictionary/synonym lookup.
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
    
    # automatic mapping using find_column_by_name helper
    for tsv_col in tsv_headers:
        col_index = find_column_by_name(tsv_col, csv_headers)
        
        if col_index is not None:
            csv_col = csv_headers[col_index]
            # Check if this CSV column was already used
            if csv_col not in used_csv_columns:
                column_mapping[tsv_col] = csv_col
                used_csv_columns.add(csv_col)
            else:
                # Column already mapped, mark as not found
                column_mapping[tsv_col] = None
        else:
            column_mapping[tsv_col] = None
        
    return column_mapping

def transfer_csv_to_tsv_with_mapping(csv_file_path: str, tsv_file_path: str, column_mapping: dict[str, str | None]) -> bool:
    """
    Transfers data from CSV to TSV using the provided column mapping.
    
    Args:
        csv_file_path (str): Path to the source CSV file.
        tsv_file_path (str): Path to the destination TSV file.
        column_mapping (dict[str, str | None]): Mapping from TSV columns to CSV columns.
    
    Returns:
        bool: True if transfer successful, False otherwise.
    
    Raises:
        IOError: If CSV file cannot be read, is empty, or has no data rows.
        ValueError: If column mapping is invalid or CSV structure is incorrect.
    """
    try:
        # read CSV file and error handling
        tsv_headers = [
            COL_1, COL_2, COL_3,
            COL_4, COL_5, COL_6,
            COL_7, COL_8, COL_9,
            COL_10, COL_11, COL_12
        ]
        
        csv_rows = readCSV(csv_file_path)
        
        if csv_rows is None:
            raise IOError(f"Failed to read CSV file: {csv_file_path}")
        if len(csv_rows) < 1:
            raise IOError(f"CSV file is empty: {csv_file_path}")
        
        csv_headers = csv_rows[0]
        csv_data = csv_rows[1:]
        
        if len(csv_data) == 0:
            raise IOError(f"CSV file has headers but no data rows: {csv_file_path}")
        
        # mapping for csv col to index
        csv_col_to_index = {col: idx for idx, col in enumerate(csv_headers)}
        
        tsv_data = []
        
        # processing logic
        for row_idx, csv_row in enumerate(csv_data, start=2):
            tsv_row = []
            
            for tsv_col in tsv_headers:
                csv_col = column_mapping[tsv_col]
                
                # use empty str if no mapping found
                if csv_col is None:
                    tsv_row.append('')
                elif csv_col in csv_col_to_index:
                    csv_idx = csv_col_to_index[csv_col]
                    # if csv row is shorter than expected
                    if csv_idx < len(csv_row):
                        tsv_row.append(csv_row[csv_idx].strip())
                    else:
                        tsv_row.append('')
                else:
                    print(f"Warning: Mapped column '{csv_col}' not found in CSV headers!")
                    tsv_row.append('')
                    
            tsv_data.append(tsv_row)
        
        # write to TSV file
        df = pd.DataFrame(tsv_data, columns=tsv_headers)
        df.to_csv(tsv_file_path, sep="\t", index=False)
        
        # Verify the file was created
        if os.path.exists(tsv_file_path) and os.path.getsize(tsv_file_path) > 0:
            print(f"Success! Transferred {len(tsv_data)} rows to {tsv_file_path}")
            return True
        else:
            raise IOError(f"Failed to create TSV file or file is empty: {tsv_file_path}")
            
    except Exception as e:
        print(f"Error! Failed to transfer data: {e}")
        print("TRACEBACK:")
        print(traceback.format_exc())
        return False


def main():
    """
    Simple test flow: Read CSV -> Clean columns -> Map columns -> Transfer to TSV
    """
    print("=" * 60)
    print("CSV TO TSV CONVERTER - TESTING FLOW")
    print("=" * 60)
    
    # File paths
    csv_file_path = "data/Uncommon_Goods_Student_Demographics.csv"
    tsv_file_path = "data/Uncommon_Good_Student_Demographics.tsv"
    temp_csv_path = csv_file_path.replace('.csv', '_cleaned.csv')
    
    # Step 1: Read CSV
    print("\n[1/4] Reading CSV file...")
    csv_rows = readCSV(csv_file_path)
    if not csv_rows:
        print("✗ Failed to read CSV")
        return
    print(f"✓ Read {len(csv_rows)} rows (including header)")
    
    # Step 2: Clean columns
    print("\n[2/4] Cleaning columns (GENDER_ID, ETHNICITY_ID, ORG_ID)...")
    columns_to_clean = ['GENDER_ID', 'ETHNICITY_ID', 'ORG_ID']
    cleaned_rows = csv_rows
    
    for column_name in columns_to_clean:
        try:
            print(f"  → Cleaning {column_name}...")
            cleaned_rows = clean_column(column_name, cleaned_rows)
            print(f"  ✓ {column_name} cleaned")
        except Exception as e:
            print(f"  ✗ Failed to clean {column_name}: {e}")
    
    # Save cleaned CSV
    with open(temp_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(cleaned_rows)
    print(f"✓ Cleaned data saved to: {temp_csv_path}")
    
    # Step 3: Map columns
    print("\n[3/4] Mapping CSV columns to TSV columns...")
    column_mapping = map_csv_to_tsv_columns(temp_csv_path)
    if not column_mapping:
        print("✗ Failed to map columns")
        return
    
    # Show mapping results
    mapped_count = sum(1 for v in column_mapping.values() if v is not None)
    print(f"✓ Mapped {mapped_count}/{len(column_mapping)} columns")
    for tsv_col, csv_col in column_mapping.items():
        status = f"→ {csv_col}" if csv_col else "✗ NOT FOUND"
        print(f"  {tsv_col:30} {status}")
    
    # Step 4: Transfer to TSV
    print("\n[4/4] Transferring data to TSV...")
    success = transfer_csv_to_tsv_with_mapping(temp_csv_path, tsv_file_path, column_mapping)
    
    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("✓ SUCCESS! All steps completed")
        print(f"Output file: {tsv_file_path}")
    else:
        print("✗ FAILED during transfer step")
    print("=" * 60)

if __name__ == "__main__":
    main()