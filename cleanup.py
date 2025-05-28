import pandas as pd
import re

# Load CSV
students_df = pd.read_csv("Uncommon_Goods_Student_Demographics.csv")

# Identify rows that contain errors (later have automated fixes?) then manually change
errors = []

def valid_name(name):
    # check if string, can contain special characters
    return isinstance(name, str) and name.isalpha()