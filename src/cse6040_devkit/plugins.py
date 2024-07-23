import dill
###
### Define plugins in this file
###

def postprocess_sort(func, key=None):
    """Plugin to sort list output types before comparing to the expected result. This has the effect of allowing students to return a list in any order and still pass the test cell.

    Args:
        func (function): An exercise solution function. This function should output a list.
        key (function, optional): The key function for sorting. The sort key should be sufficient to correctly sort any expected output into a deterministic order. Defaults to None.
    
    Returns (function): 
        - same inputs as `func`
        - returns the sorted output of `func` called on the inputs based on the optional key 
    """
    def _func(*_args, **_kwargs):
        result = func(*_args, **_kwargs)
        try:
            result = sorted(result, key=key)
        except Exception as e:
            print(f'''There was a problem sorting your result. This likely indicates an implementation issue as the expected result is sortable.''')
            print(e)
        return result
    return _func

def error_handler(func):
    """Plugin to handle exercises where students are required to raise errors in the solution. This has the effect of capturing whether the students solutions raise an error when the correct conditions are met without halting execution.

    Args:
        func (function): An exercise solution function

    Returns (function): 
        - same inputs as `func`
        - returns a tuple
            - first element is True/False indicating if an error was raised
            - second element is the output of `func` called on its inputs. In the case where an error is raised None will be returned as the second element
    """
    def _func(*args, **kwargs):
        result = None
        error_raised = False
        try:
            result = func(*args, **kwargs)
        except:
            error_raised = True
        return error_raised, result
    return _func

def sql_executor(query_generator):
    """Plugin to execute a SQL query. This has the effect of requiring students to construct a SQL query to answer a tabular data exercise 

    Args:
        query_generator (function): A function which returns a SQL query as a string. 

    Returns (function):
        - Takes an input `conn` which is a SQL connection as well as all other arguments to `query_generator`.
        - Returns a Pandas DataFrame containing the result of running the query generated against the connection.
    """
    import pandas as pd
    def _execute(conn, *args, **kwargs):
        query = query_generator(*args, **kwargs)
        return pd.read_sql(query, conn)
    return _execute

def sqlite_blocker(func):
    """Plugin to disable sqlite3.connect. This has the effect of preventing students

    Args:
        func (function): A Python function

    Returns (function): The input function with sqlite3.connect disabled at runtime and re-enabled after execution.
    """
    def replacement(*args, **kwargs):
        raise
    def _func(*args, **kwargs):
        import sqlite3
        placeholder = sqlite3.connect
        sqlite3.connect = replacement
        result = None
        try:
            result = func(*args, **kwargs)
        except RuntimeError:
            raise RuntimeError('SQLite connections are not permitted')
        finally:
            sqlite3.connect = placeholder
        return result
    return _func
