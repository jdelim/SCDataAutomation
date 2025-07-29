import csv

def readCSV(csv_file_path):
    try:
        with open(csv_file_path, mode='r', newline='') as file:
            csv_reader = csv.reader(file)
            rows = [row for row in csv_reader]
            return rows
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found!")
    except Exception as e:
        print(f"An error has occurred: {e}")

def main():
    print(readCSV('C:/Users/Admin/Documents/SCDataAutomation/data/Uncommon_Goods_Student_Demographics.csv'))


if __name__ == "__main__":
    main()