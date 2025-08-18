from connection import find_env_variables, make_connection
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt #FIXME mpl and seaborn not being recognized after moving to src/

def main():
    conn = make_connection(find_env_variables())
    
    query = """
        SELECT 
            YEAR(es.session_start_date) AS year,
            COUNT(*) AS student_count
        FROM EVENT_STUDENT_DEMOGRAPHIC AS esd
        INNER JOIN EVENT_SESSION AS es
            ON esd.EVENT_ID = es.EVENT_ID
        AND esd.SESSION_ID = es.SESSION_ID
        GROUP BY YEAR(es.session_start_date)
        ORDER BY year;
    """
    
    df = pd.read_sql(query, conn)
    print(df)
    
    sns.set_theme(style="whitegrid")

    # plot
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='YEAR', y='STUDENT_COUNT', palette='viridis')

    plt.title('Student Count per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Students')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
if __name__ == "__main__":
    main()