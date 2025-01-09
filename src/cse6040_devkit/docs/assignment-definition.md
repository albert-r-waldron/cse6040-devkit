# Assignment Definition

The Jupyter notebook assignments produced with the `cse6040_devkit` are defined as code using the `assignment` module.

## Blueprints

The assignment framework is centered on `AssignmentBlueprint`s (AKA "blueprints"). A blueprint organizes Python functions and objects associated with the assignment, by registering them as attributes of exercises or attributes of the assignment itself.

### Blueprint attributes

Each exercise _should_ have  

> One _**solution**_, one _**demo**_, and one _**sampler**_

Additionally, each exercise _may_ have  

> One _**helper**_ or many _**preload_objects**_

The assignment itself _may_ have  

> Many custom _**plugins**_ or many custom _**utils**_

### Example

```python
from cse6040_devkit.assignment import AssignmentBlueprint

bp = AssignmentBlueprint()
```

## Builders

An `AssignmentBuilder` (AKA "builder") is an extended blueprint which is used to combine multiple blueprints together and build the assignment.

### Example

```python
from cse6040_devkit.assignment import AssignmentBuilder

builder = AssignmentBuilder(header=False)
```

This code creates a builder.  

As a convenience, when the builder is created, any necessary project files and directories which do not exist are created. Default paths are relative to the current working directory.

## Exercise Attribute - solution (function)

Assignment exercises consist of giving the student a prompt and function signature. Students are required to complete the function definition IAW the prompt. The _**solution**_ attribute of an exercise is the correct implementation of that function.

### Requirements

The `test_case` and `tester_fw` submodules used in the generation and execution of tests in the assignment have limitations on solution functions.


- **Function must be deterministic (same inputs => same outputs)**
- **Function must accept all arguments passed as _keyword arguments_**
- Arguments must be serializable with `dill`, or be a `sqlite3` connection.
- Output values must be serializable.
- Output values must be a supported type.
  - native Python types, `pd.DataFrame`, `pd.Series`, and `np.ndarray` are supported, but types which are comparable _may_ work.
- Function must not modify its arguments.
- Function must not raise an error for any test case.

### Considerations

The `test_case` and `tester_fw` modules **can not** be configured to ignore sort order for any type aside from Pandas DataFrames.

### Example (simple_demo)

```python
@bp.register_solution('gt_comparison')
def x_gt_y(x, y):
    """Return `True` if `x` is greater than `y`. `False` otherwise.
    """
    return x > y
```

This code registers the function `x_gt_y` to `bp` as the _**solution**_ for exercise "gt_comparison". 

The source code, docstring, and type hints (if provided) are incorporated into the assignment.


### Example (basic_test - query string)

```python
concatenate_quotes_query = \
    solutions_bp.register_sql_query(
        'concatenate_quotes',
        query='''
                SELECT 
                    character_name AS name,
                    GROUP_CONCAT(quote, '|') AS quotes,
                    COUNT(*) AS quote_count
                FROM (SELECT * FROM quotes order by quote)
                GROUP BY character_name
                ORDER BY quote_count DESC, name''',
        doc='') # long string omitted for clarity
```

The `register_sql_query` call registers the SQL query given as the `query` parameter as the solution to the exercise "concatenate_quotes" in the `solutions_bp` blueprint.

The text given as the `doc` parameter is incorporated into the assignment the same way as a function docstring is.  

The result of the call should always be stored in a variable following `{ex_name}_query` convention. It is an extension of `str` which stores the additional attributes. A stub for students to define `concatenate_quotes_query` will be incorporated into the assignment.

### Example (basic test - free exercise)

```python
@solutions_bp.register_solution('load_the_data', free=True)
def load_the_data(data):
    do_a_thing()
    utils.do_something()
    print(f'''{str(data)} loaded!''')
```

Setting the `free` parameter to `True` will suppress a test for the "load_the_data" exercise from being inserted into the assignment (even if a sampler is registered for the exercise).

## Exercise Attribute - demo (function)

An exercise should provide students a simple example to "spot-check" against while working on their solution and better understand the requirements. This is accomplished with the _**demo**_ function.

### Requirements

The demo function must meet the following requirements

- Take no arguments
- Call the _**solution**_ with demo arguments
- Store the result in a variable

The stored result can be displayed and/or returned. Any returned values must be serializable with `dill`.

### Considerations

The demo should be digestable by students, with simplified inputs to demonstrate the key requirements of the exercise.

The demo must be executable where it is defined. Any dependencies (like the solution function) should be available in the same namespace.

The demo function body (everything below the line starting with `def`) is incorporated into the assignment in a code cell. It is de-dented so that it is at the top execution level.  

> The comments `### BEGIN IGNORE` and `### END IGNORE` suppress code on the lines between them.

### Example (simple_demo)

```python
@bp.register_demo('gt_comparison')
def demo_1():
    x = 3
    demo_result_x_gt_y = []
    ### BEGIN IGNORE
    # everything in here is not put in the assignment
    ### END IGNORE
    for y in range(2,6):
        result = x_gt_y(x,y)
        print(f'{x=}; {y=}; {result=}')
        demo_result_x_gt_y.append({
            'x': x,
            'y': y, 
            'result': result})
    return demo_result_x_gt_y
```

This registers `demo_1` as the _**demo**_ for exercise "gt_comparison".

The output from the `print` statements is captured and given to the students as part of the exercise text.

The return value is captured and serialized to be loaded in the assignment as the variable `demo_result_gt_comparison_TRUE`.

### Example (basic_test - conn_to_df)

```python
@demo_bp.register_demo(
    'conn_to_df', 
    return_values_transformer = utils.render_md_df_text_wrap,
    return_replacement = 'utils.display_df_text_wrap(demo_result_conn_to_df)')
def conn_to_df_demo():
    conn_str = 'resource/asnlib/publicdata/star_wars.db'
    with connect(conn_str) as demo_conn:
        demo_result_conn_to_df = \
            concatenate_quotes_conn_to_df(demo_conn)

    return demo_result_conn_to_df
```

This demo creates a `DataFrame`, which doesn't print nicely.

Instead of printing the `DataFrame` and capturing the output, the (string) output of `utils.render_md_df_text_wrap(demo_result_conn_to_df)` is captured and incorporated into the assignment.
> **Note:** printed output is still captured. This example just doesn't produce any.
>
> **Note:** this `utils` function mentioned renders a DataFrame as a markdown text with text-wrapping in the table cells.

Instead of omitting the `return` line in the assignment code cell, it is replaced with `utils.display_df_text_wrap(demo_result_conn_to_df)`, which will execute when the code cell runs.
> **Note:** this `utils` function displays a DataFrame with text-wrapping in the table cells.

## Exercise attribute - sampler (function)

Student solutions are evaluated by running the student's version of the function with pre-defined inputs and comparing the result to pre-computed results. These test cases are defined by the _**sampler**_ function.

### Requirements

A sampler function meets the following requirements:

- Takes one argument, `rng`, a `numpy.random.Generator`
- Uses `rng` to create a single set of parameter values for the function being tested
- Returns a parameter dictionary, mapping the parameter names to values
  > To create a `sqlite3` connection parameter:
  > - In the parameter dict, map the connection name to a dictionary (which maps table names to DataFrames)
  > - Return both the parameter dict and the connection name

### Example (simple_demo)

```python
@bp.register_sampler('gt_comparison',
                     x_gt_y, 
                     20, 
                     'result', # use tuple here if the function has many outputs
                     include_hidden=True)
def samp_1(rng):
    x, y = rng.integers(-500, 500, 2)
    return {'x': x, 'y': y}
```

This code registers `samp_1` as the _**sampler**_ for `gt_comparison`.

20 visible and 20 hidden test cases will be generated and serialized.

- Each test case consists of:
  ```python
  inputs = samp_1(framework_provided_rng)
  outputs = x_gt_y(**inputs)
  
  test_case = {**inputs, **outputs}
  ```

Code to deserialize and test the student solution will be incorporated into the assignment.

### Example (basic_test - query string)

```python
@sampler_bp.register_sampler(ex_name='concatenate_quotes',
                          sol_func=concatenate_quotes_query,
                          n_cases=10,
                          output_names='result',
                          plugin='sql_executor',
                          extra_param_names=['conn'])
def cq_sampler(rng):
    with sqlite3.connect('resource/asnlib/publicdata/star_wars.db') as conn:
        quotes_df = pd.read_sql('select * from quotes', conn)
    ###
    ### Use `rng` to randomize `quotes_df`
    ### Code omitted for clarity
    ###
    return ({'conn': {'quotes': quotes_df}}, 'conn')
```

In cases where the `sol_func` for an exercise can not comply with the requirements, a plugin is needed to force it into compliance.
> In a snippet above `concatenate_quotes_query` was defined by registering a SQL query. The object is a `QueryString` (an extension of `str` which has some additional attributes). It isn't an acceptable solution function because it isn't even a function!

Plugins are discussed in detail on their own documentation page.

## Exercise attribute - helper (function)

It is useful to define functions in the startercode for student use. This is accomplished with _**helpers**_.

### Requirements

There are no real restrictions on helper functions.

### Example (basic_test)

```python
@solutions_bp.register_helper('load_the_data')
def do_a_thing():
    print('I did a thing!')
```

This code registers `do_a_thing` as the _**helper**_ for exercise "load_the_data". The source code, and docstring (if provided) are incorporated into the assignment.

## Assignment attribute - utils (function)

It is useful to define functions outside of the assignment but use them in the assignment. Utility functions, or _**utils**_ fill this need. The `cse6040_devikit.utils` module has several built in, but custom utils can be defined as part of assignment definition as well.

### Requirements

There are no real restrictions on utility functions.

### Example (basic_test - free)

```python
@solutions_bp.register_util()
def do_something():
    print('I did something cool!')
```

This code registers `do_something` as a `util`. It will be callable as `utils.do_something()` in the assignment and in the rest of the assignment definition.

## Building

To build the assignment from the definition files, register all blueprints to the builder and run its `build` method. The Jupyter notebook and accompanying files will be produced and updated.

```python
builder.register_blueprint(bp)
builder.build()
```

The `build` method sets actions into motion that generate a lot of files and update the Jupyter notebook. Everything which was registered is ultimately serialized into artifacts or directly in the notebook.
