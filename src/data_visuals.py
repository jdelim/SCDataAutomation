from connection import find_env_variables, make_connection
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt #FIXME mpl and seaborn not being recognized after moving to src/

def plot_students_per_fiscal_year(conn, query: str, title, xlabel, ylabel):
    """
    Plots total students per fiscal year as a bar chart.
    
    Parameters:
        conn : database connection object
        query : str : SQL query returning FISCAL_YEAR and TOTAL_STUDENTS
        title : str : chart title
        xlabel : str : x-axis label
        ylabel : str : y-axis label
    """
    # Load SQL results
    df = pd.read_sql(query, conn)
    print(df)  # print results to terminal for verification

    fiscal_years = df['FISCAL_YEAR']
    total_students = df['TOTAL_STUDENTS']

    x = range(len(fiscal_years))

    plt.figure(figsize=(14, 7))
    
    # Plot bars
    plt.bar(x, total_students, color='skyblue')

    # Add labels on top of bars
    for i in range(len(fiscal_years)):
        plt.text(x[i], total_students[i] + max(total_students)*0.01, f"{total_students[i]:,}", 
                 ha='center', fontsize=10)

    # Formatting
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(x, fiscal_years, rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def plot_eth_bar_graph(conn, query: str, xCol: str, yCol: str, hueCol: str, title, xlabel, ylabel):
    df = pd.read_sql(query, conn)
    print(df) # print results to terminal
    
    # pivot table
    pivot_df = df.pivot(index=xCol, columns=hueCol, values=yCol)
    
    # add blank row after each fiscal year
    spaced_index = []
    for year in pivot_df.index:
        spaced_index.append(year)
        spaced_index.append("")  # blank label for whitespace
    pivot_df = pivot_df.reindex(spaced_index)
    
    # plot
    ax = pivot_df.plot(kind="bar", figsize=(14,7), width = 2.5)
    
    # add % labels above bars
    for container in ax.containers:
        labels = [f"{h:.1f}%" if h > 0 else "" for h in container.datavalues]
        ax.bar_label(container, labels=labels, fontsize=10, padding=5)
    
    # format
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    
    # legend
    plt.legend(title=hueCol, bbox_to_anchor=(1.02,1), loc = "upper left", fontsize=9, title_fontsize=10)
    plt.tight_layout()
    plt.show()
    
def plot_gender_bar_graph_wide(conn, query: str, title, xlabel, ylabel):
    # Load SQL results
    df = pd.read_sql(query, conn)
    print(df)  # print results to terminal

    # Extract fiscal years and gender percentages
    fiscal_years = df['FISCAL_YEAR']
    male = df['PCT_MALE']
    female = df['PCT_FEMALE']
    other = df['PCT_OTHER']

    # Set positions for grouped bars
    x = range(len(fiscal_years))
    width = 0.25

    # Create figure
    plt.figure(figsize=(14, 7))

    # Plot bars
    plt.bar([p - width for p in x], male, width=width, label='Male')
    plt.bar(x, female, width=width, label='Female')
    plt.bar([p + width for p in x], other, width=width, label='Other')

    # Add % labels above bars
    for i in range(len(fiscal_years)):
        plt.text(x[i] - width, male[i] + 0.5, f"{male[i]:.1f}%", ha='center', fontsize=10)
        plt.text(x[i], female[i] + 0.5, f"{female[i]:.1f}%", ha='center', fontsize=10)
        plt.text(x[i] + width, other[i] + 0.5, f"{other[i]:.1f}%", ha='center', fontsize=10)

    # Formatting
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(x, fiscal_years, rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    plt.ylim(0, 100)
    plt.legend(title='Gender', bbox_to_anchor=(1.02,1), loc='upper left', fontsize=9, title_fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
    


def main():
    conn = make_connection(find_env_variables())
    
    students_per_fiscal_year_query = """
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
    
    ethnicity_percentages_query = """
        WITH esd_with_fy AS (
        SELECT 
            CASE 
                WHEN MONTH(s.session_start_date) >= 7 
                    THEN TO_VARCHAR(YEAR(s.session_start_date)) || '-' || TO_VARCHAR(YEAR(s.session_start_date) + 1)
                ELSE TO_VARCHAR(YEAR(s.session_start_date) - 1) || '-' || TO_VARCHAR(YEAR(s.session_start_date))
            END AS fiscal_year,
            esd.ethnicity_id
        FROM EVENT_STUDENT_DEMOGRAPHIC esd
        JOIN EVENT_SESSION s
            ON esd.event_id = s.event_id
        AND esd.session_id = s.session_id
        WHERE esd.ethnicity_id IS NOT NULL
    ),
    ethnicity_counts AS (
        SELECT 
            fiscal_year,
            ethnicity_id,
            COUNT(*) AS student_count
        FROM esd_with_fy
        GROUP BY fiscal_year, ethnicity_id
    ),
    total_per_year AS (
        SELECT 
            fiscal_year,
            SUM(student_count) AS total_students
        FROM ethnicity_counts
        GROUP BY fiscal_year
    )
    SELECT 
        ec.fiscal_year,
        CASE ec.ethnicity_id
            WHEN 1 THEN 'American Indian or Alaska Native'
            WHEN 2 THEN 'Asian'
            WHEN 3 THEN 'Black or African American'
            WHEN 4 THEN 'Hispanic or Latino'
            WHEN 5 THEN 'White'
            WHEN 6 THEN 'Native Hawaiian and Other Pacific Islander'
            WHEN 7 THEN 'Multiracial'
            WHEN 8 THEN 'Other Race'
            ELSE 'Unknown'
        END AS ethnicity,
        ROUND((ec.student_count / t.total_students) * 100, 2) AS pct_of_year
    FROM ethnicity_counts ec
    JOIN total_per_year t
        ON ec.fiscal_year = t.fiscal_year
    ORDER BY ec.fiscal_year, ethnicity;
    """
    
    gender_percentages_query = """
            SELECT
            CONCAT(
                CASE WHEN MONTH(SES.session_start_date) >= 7 
                    THEN YEAR(SES.session_start_date)
                    ELSE YEAR(SES.session_start_date) - 1
                END,
                '-',
                CASE WHEN MONTH(SES.session_start_date) >= 7
                    THEN YEAR(SES.session_start_date) + 1
                    ELSE YEAR(SES.session_start_date)
                END
            ) AS fiscal_year,
            ROUND(SUM(CASE WHEN DEM.gender_id = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(DEM.gender_id), 2) AS pct_male,
            ROUND(SUM(CASE WHEN DEM.gender_id = 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(DEM.gender_id), 2) AS pct_female,
            ROUND(SUM(CASE WHEN DEM.gender_id = 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(DEM.gender_id), 2) AS pct_other
        FROM
            EVENT_STUDENT_DEMOGRAPHIC AS DEM
        JOIN
            EVENT_SESSION AS SES
            ON DEM.session_id = SES.session_id
        GROUP BY
            CONCAT(
                CASE WHEN MONTH(SES.session_start_date) >= 7 
                    THEN YEAR(SES.session_start_date)
                    ELSE YEAR(SES.session_start_date) - 1
                END,
                '-',
                CASE WHEN MONTH(SES.session_start_date) >= 7
                    THEN YEAR(SES.session_start_date) + 1
                    ELSE YEAR(SES.session_start_date)
                END
            )
        ORDER BY
            fiscal_year;
    """
    
    plot_students_per_fiscal_year(conn, students_per_fiscal_year_query, title="Total Students per Fiscal Year", 
                                  xlabel="Fiscal Year", ylabel="Total Students")

    #plot_gender_bar_graph_wide(conn, gender_percentages_query, title="Gender Distribution per Fiscal Year", xlabel="Fiscal Year", 
                               #ylabel="Percentage")
    #plot_eth_bar_graph(conn, ethnicity_percentages_query, xCol='FISCAL_YEAR', yCol='PCT_OF_YEAR', hueCol='ETHNICITY',
                   #title='Ethnicity Percentages by Fiscal Year', xlabel='Fiscal Year', ylabel='Percentage')
    
    
if __name__ == "__main__":
    main()