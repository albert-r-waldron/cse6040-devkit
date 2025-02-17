# Import whatever is needed as well as these modules from the devkit.
from cse6040_devkit import assignment, utils, plugins
import pandas as pd
import numpy as np
import dill

bp = assignment.AssignmentBlueprint()

# Register an exercise solution
@bp.register_solution(ex_name='fizzbuzz')
def fizzbuzz_soln(x: int):
    """`fizzbuzz_soln` solves the classic "fizzbuzz" problem for a single integer. 

**Inputs**:
- `i` (int): Any integer

**Returns**: one of the following depending on whether 3, 5, both or neither divide evenly into `i`
- `'Fizz'`     if i is divisible by 3                Example: 9
- `'Buzz'`     if i is divisible by 5                Example: 35
- `'FizzBuzz'` if i is divisible by both 3 and 5     Example: 45
- `i`          if i is divisible by neither 3 nor 5  Example: 22
    """
    print('an extra statement')
    ### BEGIN SOLUTION
    return ("Fizz"*x_divides_y(3, x)+"Buzz"*x_divides_y(5, x)) or x
    ### END SOLUTION

# Register an exercise helper function
# Helper function source code is included in the notebook
@bp.register_helper(ex_name='fizzbuzz')
def x_divides_y(x: int, y: int):
    """`x_divides_y` evaluates whether one integer (`x`) divides evenly into another integer (`y`).
    """
    return y%x == 0

# Register an exercise demo
@bp.register_demo(ex_name='fizzbuzz')
def fizzbuzz_demo():
    for x in [12, 10, 15, 16]:
        print(f'fizzbuzz_soln({x}) -> {fizzbuzz_soln(x)}')
fizzbuzz_demo()

# Register a plugin to be used in solution testing
@bp.register_plugin()
def convert_to_str(func):
    from warnings import warn
    def _func(**kwargs):
        result = func(**kwargs)
        try:
            return str(result)
        except:
            warn(f'Unable to convert {func.__name__} output to a string. There is likely an error in its implementation.')
            return result
    return _func

# Register a sampler which will be used to generate test case files during the build
@bp.register_sampler(ex_name='fizzbuzz', 
                     sol_func=fizzbuzz_soln, 
                     n_cases=30,             
                     output_names=('new_output_name',), 
                     plugin='convert_to_str')
def fizzbuzz_sampler(rng:np.random.Generator):
    if rng.integers(1, 6) < 2:
        return {'x': 15*rng.integers(1, 13, dtype=int)}
    return {'x': rng.integers(1,200, dtype=int)}


# Register a utility function to be made available in the notebook
# Utils source code is not included in the notebook
@bp.register_util()
def foo(arg: str) -> str:
    """Wraps the argument string with "foo" at the start and "too" at the end.

    Args:
        arg (str): Any string

    Returns:
        str: "foo" followed by `arg` followed by "too"
    """
    return f'foo {arg} too'

# Registering an exercise with `free` set True makes it a free exercise. 
@bp.register_solution('freebie', free=True)
def freebie():
    ### This will never be tested
    
    ### BEGIN IGNORE
    ### this will never be seen
    ### END IGNORE

    print(free_data)

# Register an object to be loaded prior to an exercise
free_data = [1,2,3,4]
bp.register_preload_object('freebie', free_data, 'free_data')

# Register a string as a SQL query exercise solution
species_count_query = \
    bp.register_sql_query(ex_name='species_count',
                          query='''
                                    select species, count(1) as "count"
                                    from characters
                                    group by species
                                  ''',
                          doc='''
                                  The query should return these columns
                                  - species (string)
                                  - count (int): count of species value in characters
                              ''')

# Register a preload object
with open ('data/char_df', 'rb') as f:
    char_df = dill.load(f)
bp.register_preload_object('species_count',
                           char_df,
                           'char_df')

# Register a sampler
@bp.register_sampler('species_count',
                     species_count_query,
                     10,
                     'result',
                     plugin='sql_executor', # built-in plugin
                     extra_param_names=['conn']) # needed for plugin
def species_count_samp(rng: np.random.Generator):
    m, _ = char_df.shape
    _char_df = char_df.copy()
    _char_df['species'] = rng.choice(char_df['species'].unique(), m, 
                                     replace=True)
    return {'conn': {'characters': _char_df}}, 'conn'

# Register a demo
@bp.register_demo('species_count',
                    return_replacement='display(demo_result_species_count.head())',
                    return_values_transformer=lambda df: df.head().to_markdown())
def species_count_demo():
    from cse6040_devkit.tester_fw.test_utils \
        import dfs_to_conn
    conn = dfs_to_conn({'characters': char_df})
    demo_result_species_count = \
        plugins.sql_executor(species_count_query)(conn)
    return demo_result_species_count

builder = assignment.AssignmentBuilder()
builder.register_blueprint(bp)

builder.build()
