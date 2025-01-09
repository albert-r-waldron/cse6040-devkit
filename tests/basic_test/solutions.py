from cse6040_devkit.assignment import AssignmentBlueprint
from cse6040_devkit import utils
import logging
from collections import Counter
import pandas as pd
import sqlite3
import numpy as np
from scipy.sparse import coo_matrix

logger = logging.getLogger(__name__)
logging.basicConfig(filemode='w',
                    filename='build_log.txt', 
                    level=logging.INFO)

solutions_bp = AssignmentBlueprint()

# Nested data
@solutions_bp.register_solution(ex_name='inverted_dictionary')
def invert_dict(d: dict, allow_dup_vals: bool, allow_unhashable_vals: bool) -> dict:
    r"""Use input to create a new dictionary with keys and values swapped

There are configuration options to determine behavior when there is not a one-to-one mapping of keys to distinct, hashable values.

Args:
- d (dict): dictionary to invert
- allow_dup_vals (bool): 
    - When set to `True` the result will map any duplicated, hashable value in `d` to the `set` of its keys.
    - When set to `False` a `ValueError` is raised if there are any duplicate, hashable values in `d`.
- allow_unhashable_vals (bool): 
    -When set to `True` any unhashable values in `d` are not included in the result.  
    -When set to `False` a `ValueError` is raised if there are any unhashable values in `d`.

Raises:
- ValueError: if there are duplicate values in `d` and `allow_dup_vals` is `False`.
- ValueError: if there are unhashable values in `d` and `allow_unhashable_vals` is `False`.

Returns:
- dict: A new dictionary mapping the values of `d` to their associated keys.  
    """
    d_out = {}
    for v, k in d.items():
        if not utils.is_hashable(k):
            if allow_unhashable_vals:
                continue
            else:
                raise ValueError
        if k in d_out:
            if allow_dup_vals:
                if isinstance(d_out[k], set):
                    d_out[k].add(v)
                else:
                    d_out[k] = {d_out[k], v}
                pass
            else:
                raise ValueError
        else:
            d_out[k] = v
    return d_out

# String parsing
@solutions_bp.register_solution('extract_article_words')
def extract_article_words(record: dict) -> set:
    import re
    return set(re.sub('[^\w\s]|[\d_]', ' ', record['Article'].lower()).split())

# Counter
@solutions_bp.register_solution('count_articles')
def count_articles(running_count: Counter, article_words):
    """Update a running count by one for each distinct word in an article.  

Args:  
- running_count (Counter): Maps words to the number of articles they have appeared in.  
- article_words (set): The distinct words appearing in a single article.  

Returns:  
- Counter: Updated running total.
"""
    return running_count + Counter(article_words)

# Funcs as args
@solutions_bp.register_solution('record_examiner')
def record_examiner(some_iter, map_func, red_func, initial=None):
    """Applies the `map_func` to each item in `some_iter` combines the results with `red_func`.

Args:
- some_iter (iterable): An iterable object.  
- map_func (function): A function that takes a single input and returns a single output.  
- red_func (function): A function which takes two inputs (`value` and `item`). It returns the result of "combining" `item` with `value`.
- initial (any, optional): The initial `value` used in `red_func`. Defaults to None, which will not use an initial value.

Returns:
    any: The result of applying `map_func` to each item in `some_iter` and then combining them with `red_func`.
    """
    from functools import reduce
    if initial is not None:
        return reduce(red_func, map(map_func, some_iter), initial)
    else:
        return reduce(red_func, map(map_func, some_iter))

# SQLite queries
concatenate_quotes_query = solutions_bp.register_sql_query('concatenate_quotes',
                                query='''
                                        SELECT 
                                            character_name AS name,
                                            GROUP_CONCAT(quote, '|') AS quotes,
                                            COUNT(*) AS quote_count
                                        FROM (SELECT * FROM quotes order by quote)
                                        GROUP BY character_name
                                        ORDER BY quote_count DESC, name''',
                                doc='''
                                        Re-organize the data in the `quotes` table such that all `quote` values associated with a particular `character_name` are in a single row.  

                                        Result columns:  
                                        - `name` - The name of a character
                                        - `quotes` - All quote values associated with the character, concatenated together.
                                            - Quotes should be ordered alphabetically.
                                            - Quotes should be separated by the "pipe" character `'|'`.
                                        - `quote_count` - The number of quotes associated with the character.                                   
                                    ''')

# conn -> df
@solutions_bp.register_solution('conn_to_df')
def concatenate_quotes_conn_to_df(conn):
    """Re-organize the data in the `quotes` table such that all `quote` values associated with a particular `character_name` are in a single row.  

Args:

- conn (sqlite3 connection): Connection with table called `quotes`.
    - `quotes` will have `character_name` and `quote` columns attributing a film quote to a character. Each record is one film quote.

Returns:
- DataFrame: contains the following columns:
    - `name` - The name of a character
    - `quotes` - All quote values associated with the character, concatenated together.
        - Quotes should be ordered alphabetically.
        - Quotes should be separated by the "pipe" character `'|'`.
    - `quote_count` - The number of quotes associated with the character. 
"""
    df = pd.read_sql('''
                        SELECT 
                            character_name AS name,
                            GROUP_CONCAT(quote, '|') AS quotes,
                            COUNT(*) AS quote_count
                        FROM (SELECT * FROM quotes order by quote)
                        GROUP BY character_name
                        ORDER BY quote_count DESC, name''',
                    conn)
    df = df.astype({'name': str,
               'quotes': str,
               'quote_count': int})
    return df


with sqlite3.connect('resource/asnlib/publicdata/star_wars.db') as conn:
    char_df = pd.read_sql('select * from characters', conn)
    spec_df = pd.read_sql('select * from species', conn)

solutions_bp.register_preload_object('species_count', char_df, 'char_df')
solutions_bp.register_preload_object('species_count', spec_df, 'spec_df')

# DataFrame
@solutions_bp.register_solution('species_count')
def species_count(char_df, spec_df):
    """Determine the count of characters in `char_df` belonging to each `classification` in `spec_df`.

Args:
- `char_df` (pd.DataFrame): contains character data including the 'name' and 'species' columns.
- `spec_df` (pd.DataFrame): contains species data including the 'name' and 'classification' columns. The values in `spec_df['name']` refer to the same data as `char_df['species']`.

Returns:
- pd.DataFrame: contains the following columns:
    - `classification` (str): species classification. Each row should have a distinct value in this column.
    - `count` (int): count indicating how many characters from the `char_df` are members of a species with the `classification`.
    """
    ### BEGIN SOLUTION
    merged = char_df.merge(spec_df, left_on='species', right_on='name')
    return merged['classification'].value_counts().reset_index().set_axis(['classification', 'count'], axis=1)
    ### END SOLUTION
    
# Series
@solutions_bp.register_solution('count_values')
def count_values(s):
    """Get the count of each distinct value in a Pandas Series  

Args:  

- s (pd.Series): Any Pandas Series

Return:  

- pd.Series: The index of the result series is all distinct values from the input Series, `s`. The values of the result series are the occurrance counts of the index within the input Series, `s`.
    """
    return s.value_counts()

# Numpy array
@solutions_bp.register_solution('mat_vec_div')
def mat_vec_div(A, x):
    r"""Compute matrix-vector product of $Ax^{-1}$  

Args:

- A (np.ndarray): A 2-D numeric array
- x (np.ndarray): A 1-D numeric array

Returns:

- np.ndarray: The matrix-vector product of `A` and _the inverse of_ `x`.
    """
    x_inv = x / x.dot(x.T)
    return A.dot(x_inv).round(3)

@solutions_bp.register_solution('df_to_coo')
def df_to_coo(df, shape):
    """
    Create a COO matrix based off of a DataFrame

    Args:
    - df (DataFrame): A DataFrame representing a data matrix.
        - `data` is the value at position (`row`, `col) in the matrix.
    - shape (tuple): Shape of the data matrix

    Returns:
    - scipy.sparse.coo_matrix: The matrix given by `df`.
    """
    return coo_matrix((df['data'], (df['row'], df['col'])), shape)

@solutions_bp.register_helper('load_the_data')
def do_a_thing():
    print('I did a thing!')

@solutions_bp.register_util()
def do_something():
    print('I did something cool!')

@solutions_bp.register_solution('load_the_data', free=True)
def load_the_data(data):
    do_a_thing()
    utils.do_something()
    print(f'''{str(data)} loaded!''')