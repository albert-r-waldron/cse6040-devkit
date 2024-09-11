# %%
import re
import dill
import sqlite3
import pandas as pd
from pprint import pprint
from IPython.display import display
from cse6040_devkit.assignment import AssignmentBlueprint, AssignmentBuilder


# %%
bp = AssignmentBlueprint()
builder = AssignmentBuilder(header=False)

# %%
# Path to the SQLite database file; change as needed
db = 'resource/asnlib/publicdata/nyc_jobs.db'

# Database connection
conn = sqlite3.connect(db)

# %%
builder.config['assignment_name'] = 'Notebook 9: Introduction to SQL'
builder.config['subtitle'] = 'Advanced SQL Queries'
builder.config['rng_seed'] = 6040
builder.config['version'] = !git rev-parse --short HEAD
builder.config['version'] = '1.0-' + builder.config['version'][0]
pprint(builder.config)

# %%
@bp.register_plugin()
def sql_validator(query_generator, pattern=None):
    """Plugin to execute a SQL query, with an additional regex check for query validation."""
    def _execute(conn, *args, **kwargs):
        query = query_generator(*args, **kwargs)
        if not re.search(pattern, query, re.IGNORECASE):
            raise ValueError("The query does not match the required pattern.")
        return pd.read_sql(query, conn)
    
    return _execute

# %%
@bp.register_solution('get_database_schema__FREE', free=True)
def get_database_schema__FREE(conn):
    """**This is a free exercise!** 

    **Please run the test cell below to collect your FREE point**
    """
    # Retrieve the list of tables from sqlite_master
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql_query(tables_query, conn)

    # Prepare DataFrames to hold combined results
    schema_info = pd.DataFrame()

    # Loop through tables to get column details and foreign key details
    for table in tables['name']:
        # Get column details
        pragma_table_info = f"PRAGMA table_info('{table}')"
        table_info = pd.read_sql_query(pragma_table_info, conn)
        table_info['table_name'] = table  # Add table name to the DataFrame

        # Get foreign key details
        pragma_fk_info = f"PRAGMA foreign_key_list('{table}')"
        fk_info = pd.read_sql_query(pragma_fk_info, conn)
        fk_info = fk_info[['from', 'table', 'to']]
        fk_info.rename(columns={'from': 'column_name', 'table': 'references_table', 'to': 'references_column'}, inplace=True)

        # Merge foreign key info into table_info on column name
        table_info = table_info.merge(fk_info, how='left', left_on='name', right_on='column_name')
        table_info.drop(columns=['column_name'], inplace=True)  # Remove redundant column

        # Add to main DataFrame
        schema_info = pd.concat([schema_info, table_info], ignore_index=True)

    # Reorder columns for better readability
    schema_info = schema_info[['table_name', 'name', 'type', 'notnull', 'pk', 'references_table', 'references_column']]
    schema_info.columns = ['table', 'column', 'type', 'not_null', 'primary_key', 'references_table', 'references_column']

    return schema_info

# %%
@bp.register_demo('get_database_schema__FREE')
def get_database_schema__FREE_demo():
    df_schema = get_database_schema__FREE(conn)
    display(df_schema)

# %%
@bp.register_solution('parse_classification')
def parse_classification():
    """**Activity**: Extract and Separate Title Classification Code and Description

**Inputs**: None

**Return**: `query`: a Python string containing a SQLite query. It should query the database to create a new DataFrame from the `job_title` table with the following columns:
- `title_classification`: The original `title_classification` column from the `job_title` table.
- `title_classification_desc`: The text portion of the `title_classification` with the final dash and integer removed.
- `title_classification_code`: The integer portion of the `title_classification` after the last dash.

**Requirements/steps**:
- The database table you will need is named `job_title`.
- The column you will work with is `title_classification`.

**Hint**: The following SQLite functions will help: [SUBSTR](https://www.sqlite.org/lang_corefunc.html#substr), [INSTR](https://www.sqlite.org/lang_corefunc.html#instr), and [REPLACE](https://sqlite.org/lang_corefunc.html#replace).
    """
    ### BEGIN SOLUTION
    query = """
    SELECT
        title_classification,
        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(title_classification, '-1', ''), '-2', ''), '-3', ''), '-4', ''), '-5', '') AS title_classification_desc,
        SUBSTR(REPLACE(title_classification, 'Non-', ''), INSTR(REPLACE(title_classification, 'Non-', ''), '-') + 1) AS title_classification_code
    FROM
        job_title;
    """
    return query
    ### END SOLUTION

# %%
@bp.register_demo('parse_classification')
def parse_classification_demo():
    """**Example**. A correct implementation should produce, for the demo, the following output:
    
| title_classification   | title_classification_desc   |   title_classification_code |
|:-----------------------|:----------------------------|----------------------------:|
| Competitive-1          | Competitive                 |                           1 |
| Non-Competitive-5      | Non-Competitive             |                           5 |
| Non-Competitive-5      | Non-Competitive             |                           5 |
| Competitive-1          | Competitive                 |                           1 |
| Competitive-1          | Competitive                 |                           1 |

"""
    parse_classification_query = parse_classification()
    parse_classification_df = pd.read_sql_query(parse_classification_query, conn)
    display(parse_classification_df.head())

# %%
@bp.register_sampler(ex_name='parse_classification', sol_func=parse_classification, n_cases=10, output_names=('parse_classification_df',),plugin='sql_executor', extra_param_names=['conn'])
def parse_classification_sampler():
    query = '''
            SELECT *
            FROM job_title
            ORDER BY random()
            LIMIT ABS(random() % 150) + 200
    '''
    test_data = pd.read_sql(query, conn)
    sampler_output = ({
        'conn': {
            'job_title': test_data
        }
    }, 'conn')
    return sampler_output

# %%
@bp.register_solution('convert_post_until')
def convert_post_until():
    """**Activity**: Convert Date Strings in the `post_until` Column to Standardized Date Format

**Inputs**: None

**Return**: `query`: a Python string containing a SQLite query. It should query the database to create a new DataFrame from the `job_post` table with the following columns:
- `post_until`: The original `post_until` column from the `job_post` table.
- `post_until_converted`: A new column where the date strings in `post_until` have been converted to the standardized `YYYY-MM-DD` format.

**Requirements/steps**:
- The database table you will need is named `job_post`.
- The column you will work with is `post_until`.
- Convert date strings in the format `DD-MMM-YYYY` (e.g., `24-AUG-2024`) to `YYYY-MM-DD` (e.g., `2024-08-24`).

**Hint**: The following SQLite functions will help: [PRINTF](https://www.sqlite.org/printf.html) and [STRFTIME](https://www.sqlite.org/lang_datefunc.html#strftime).
    """
    ### BEGIN SOLUTION
    query = """
    SELECT
        post_until,
        strftime('%Y-%m-%d',
                 printf('%s-%02d-%02d',
                        SUBSTR(post_until, -4),
                        CASE SUBSTR(post_until, 4, 3)
                            WHEN 'JAN' THEN 1
                            WHEN 'FEB' THEN 2
                            WHEN 'MAR' THEN 3
                            WHEN 'APR' THEN 4
                            WHEN 'MAY' THEN 5
                            WHEN 'JUN' THEN 6
                            WHEN 'JUL' THEN 7
                            WHEN 'AUG' THEN 8
                            WHEN 'SEP' THEN 9
                            WHEN 'OCT' THEN 10
                            WHEN 'NOV' THEN 11
                            WHEN 'DEC' THEN 12
                        END,
                        CAST(SUBSTR(post_until, 1, 2) AS INTEGER)
                       )
                ) AS post_until_converted
    FROM
        job_posting;
    """
    return query
    ### END SOLUTION

# %%
@bp.register_demo('convert_post_until')
def convert_post_until_demo():
    """**Example**. A correct implementation should produce, for the demo, the following output:
    
| post_until   | post_until_converted   |
|:-------------|:-----------------------|
| 25-AUG-2024  | 2024-08-25             |
| 24-AUG-2024  | 2024-08-24             |
| 12-JUN-2025  | 2025-06-12             |
| 05-SEP-2024  | 2024-09-05             |
| 25-SEP-2024  | 2024-09-25             |
"""
    convert_post_until_query = convert_post_until()
    convert_post_until_df = pd.read_sql_query(convert_post_until_query, conn)
    display(convert_post_until_df[convert_post_until_df['post_until'].notnull()].head())

# %%
@bp.register_sampler(ex_name='convert_post_until', sol_func=convert_post_until, n_cases=10, output_names=('convert_post_until_df',),plugin='sql_executor', extra_param_names=['conn'])
def convert_post_until_sampler():
    query = '''
            SELECT *
            FROM job_posting
            WHERE post_until IS NOT NULL
            ORDER BY random()
            LIMIT ABS(random() % 150) + 200
    '''
    test_data = pd.read_sql(query, conn)
    sampler_output = ({
        'conn': {
            'job_posting': test_data
        }
    }, 'conn')
    return sampler_output

# %%
@bp.register_solution('max_salary_by_category_inline')
def max_salary_by_category_inline():
    """**Activity**: Identify the Maximum Salary for Each Job Category Using an Inline Subquery

**Inputs**: None

**Return**: `query`: A Python string containing a SQLite query. It should query the database to create a new DataFrame from the `salary`, `job_posting`, and `job_title` tables with the following columns:
- `job_category`: The job category from the `job_title` table.
- `salary_range_to`: The maximum salary range for each job category.

**Requirements/steps**:
- Use an inline subquery to determine the maximum salary (`salary_range_to`) for each job category.
- The query should join the `salary`, `job_posting`, and `job_title` tables to correctly match the job categories and their corresponding salaries.
- The query should use the `DISTINCT` keyword to ensure that each job category is only listed once, with its corresponding maximum salary.
- Return the job categories and the maximum salary found in each category.
- The results should be ordered by `salary_range_to` in descending order.

**Hint**: The following SQLite functions and concepts will help: [JOIN](https://www.sqlite.org/syntax/join-operator.html), [MAX](https://www.sqlite.org/lang_aggfunc.html#max), and [SUBQUERY](https://www.sqlite.org/lang_expr.html#subqueries).
    """
    ### BEGIN SOLUTION
    query = """
    SELECT DISTINCT jt.job_category, s.salary_range_to
    FROM salary s
    JOIN job_posting jp ON s.job_posting_id = jp.id
    JOIN job_title jt ON jp.title_id = jt.id
    WHERE s.salary_range_to = (
        SELECT MAX(sub.salary_range_to)
        FROM salary sub
        JOIN job_posting sub_jp ON sub.job_posting_id = sub_jp.id
        JOIN job_title sub_jt ON sub_jp.title_id = sub_jt.id
        WHERE sub_jt.job_category = jt.job_category
    )
    ORDER BY s.salary_range_to DESC;
    """
    return query
    ### END SOLUTION

# %%
@bp.register_demo('max_salary_by_category_inline')
def max_salary_by_category_inline_demo():
    """**Example**. A correct implementation should produce, for the demo, the following output:
    
| job_category                                      |   salary_range_to |
|:--------------------------------------------------|------------------:|
| Administration & Human Resources Social Services  |             99694 |
| Administration & Human Resources                  |             99190 |
| Health                                            |             99190 |
| Social Services                                   |             99113 |
| Technology, Data & Innovation Policy, Research... |             98907 |
"""
    max_salary_by_category_inline_query = max_salary_by_category_inline()
    max_salary_by_category_inline_df = pd.read_sql_query(max_salary_by_category_inline_query, conn)
    display(max_salary_by_category_inline_df.head())

# %%
inline_query_regex = r"(?i)WHERE\s+\S+\s*[=<>]\s*\("

@builder.register_sampler(
    ex_name='max_salary_by_category_inline', 
    sol_func=max_salary_by_category_inline, 
    n_cases=10, 
    output_names=('max_salary_by_category_inline_df',), 
    plugin='sql_validator', 
    extra_param_names=['conn'],
    pattern=inline_query_regex
)
def max_salary_by_category_inline_sampler():
    query = '''
            SELECT *
            FROM salary
            LIMIT ABS(random() % 100) + 600
    '''
    test_salary = pd.read_sql(query, conn)
    query = '''
            SELECT *
            FROM job_posting
            LIMIT ABS(random() % 100) + 600
    '''
    test_job_posting = pd.read_sql(query, conn)
    query = '''
            SELECT *
            FROM job_title
            LIMIT ABS(random() % 100) + 600
    '''
    test_job_title = pd.read_sql(query, conn)
    sampler_output = ({
        'conn': {
            'salary': test_salary,
            'job_posting': test_job_posting,
            'job_title': test_job_title
        }
    }, 'conn')
    return sampler_output

# %%
builder.register_blueprint(bp)

# %%
builder.build()

# %%
builder.config['exercises']['get_database_schema__FREE']['num'] = 0
builder.config['exercises']['get_database_schema__FREE']['points'] = 1
builder.config['exercises']['parse_classification']['num'] = 1
# builder.config['exercises']['parse_classification']['points'] = 1
builder.config['exercises']['convert_post_until']['num'] = 2
# builder.config['exercises']['convert_post_until']['points'] = 1
builder.config['exercises']['max_salary_by_category_inline']['num'] = 3
# builder.config['exercises']['max_salary_by_category_inline']['points'] = 1



