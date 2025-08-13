from connection import find_env_variables, make_connection
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    conn = make_connection(find_env_variables())
    
if __name__ == "__main__":
    main()