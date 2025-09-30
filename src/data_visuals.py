from connection import find_env_variables, make_connection
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt #FIXME mpl and seaborn not being recognized after moving to src/

def main():
    conn = make_connection(find_env_variables())
    
    query = """
            WITH esd_counts AS (
        SELECT 
            event_id,
            session_id,
            COUNT(*) AS student_count
        FROM EVENT_STUDENT_DEMOGRAPHIC
        GROUP BY event_id, session_id
    ),
    ea_counts AS (
        SELECT
            event_id,
            session_id,
            COALESCE(actual_attendee_cnt, reserved_attendee_cnt) AS activity_count
        FROM EVENT_ACTIVITY
    ),
    combined AS (
        SELECT
            e.session_start_date,
            COALESCE(esd.student_count, ea.activity_count) AS final_count
        FROM EVENT_SESSION e
        LEFT JOIN esd_counts esd
            ON e.event_id = esd.event_id
        AND e.session_id = esd.session_id
        LEFT JOIN ea_counts ea
            ON e.event_id = ea.event_id
        AND e.session_id = ea.session_id
    )
    SELECT 
        CASE 
            WHEN MONTH(session_start_date) >= 7 
                THEN TO_VARCHAR(YEAR(session_start_date)) || '-' || TO_VARCHAR(YEAR(session_start_date) + 1)
            ELSE TO_VARCHAR(YEAR(session_start_date) - 1) || '-' || TO_VARCHAR(YEAR(session_start_date))
        END AS fiscal_year,
        SUM(final_count) AS total_students
    FROM combined
    GROUP BY fiscal_year
    ORDER BY fiscal_year;
    """
    
    df = pd.read_sql(query, conn)
    print(df)
    
    sns.set_theme(style="whitegrid")

    # plot
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='FISCAL_YEAR', y='TOTAL_STUDENTS', palette='viridis')

    plt.title('Student Count per Fiscal Year')
    plt.xlabel('Fiscal Year')
    plt.ylabel('Number of Students')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
if __name__ == "__main__":
    main()