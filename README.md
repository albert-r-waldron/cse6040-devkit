# 6040 Devkit

## Simplify Assignment Development

This package simplifies the assignment development process by separating the functional parts of the assignment from configuration details and both of those from any additional content.  

The functional parts are defined in Python using `AssignmentBuilder` objects, and flexibility to define the assignment across multiple Python files or in a Jupyter notebook. It's also straightforward to add a bit of code to an existing analysis project and adapt it into an assignment.  

Configuration is defined in `assignment_configuration.yaml`. Assignment metadata, exercise point values, and test settings are stored in a common format. These can be quickly and easily updated with manual edits.

The functional parts and configuration are parsed and built into a Jupyter notebook `main.ipynb` using a templating engine. Cells can be added to those that were built. The new cells are preserved on subsequent builds. The sequence of cells is maintained as well. This allows for content beyond what is defined in the templates.

## Installation

You can download one of the releases and use `pip` to install the wheel in your Python environment.  

```bash
pip install --force-reinstall /path/to/wheel.whl
```

## Documentation

[API](docs/api.md)  
[Tutorial](docs/tutorial/tutorial.md)

## Python example

```python
# Import whatever is needed as well as these modules from the devkit.
from cse6040_devkit import assignment, utils, plugins

# Create an instance of AssignmentBlueprint
bp = assignment.AssignmentBlueprint()

# Register an exercise solution
@bp.register_solution(ex_name='fizzbuzz')
def fizzbuzz_soln(i: int):...

# Register an exercise helper function
# Helper function source code is included in the notebook
@bp.register_helper(ex_name='fizzbuzz')
def x_divides_y(x: int, y: int):...

# Register an exercise demo
@bp.register_demo(ex_name='fizzbuzz')
def fizzbuzz_demo():...

# Register a plugin to be used in solution testing
@bp.register_plugin()
def convert_to_str(func):...

# Register a sampler which will be used to generate test case files during the build
@bp.register_sampler(ex_name='fizzbuzz', 
                     sol_func=fizzbuzz_soln, 
                     n_cases=30,             
                     output_names=('fizzbuzz_output',), 
                     plugin='convert_to_str')
def fizzbuzz_sampler():...

# Register a utility function to be made available in the notebook
# Utils source code is not included in the notebook
@bp.register_util()
def foo(arg: str) -> str:...

# Registering a demo for an exercise that does not have a solution
# creates a free exercise. 
@bp.register_demo('freebie')
def freebie():
    ### It doesn't matter what you put here the prompt won't generate unless a solution is registered
    print('Hurray! Free points!')


# Register an object to be loaded prior to an exercise
free_data = [1,2,3,4]
bp.register_preload_object('freebie', free_data, 'free_data')

# Create an instance of AssignmentBuilder
builder = assignment.AssignmentBuilder()

# Register blueprint
builder.register_blueprint(bp)

# Set a seed for usage of RNG in generating test cases
from random import seed
seed(6040)

# Build assignment files
builder.build()
```
## YAML example

```yaml
assignment_name: assignment name      # name of the assignment - i.e. Midterm 1
subtitle: assignment subtitle         # subtitle indicating the theme of the assignment - i.e. Association Rule Mining
version: 0.0.1                        # Version
topics: this, that, and the other     # String indicating which topics are covered in the exam, should be a comma separated list
points_cap: points cap                # Maximum number of points for the assignment
total_points: total points            # Total points available
global_imports: null                  # Modules to include in global imports
exercises:                            
  fizzbuzz:                           # Each exercise name is a key in 'exercises'
    num: 0                            # Which number in sequence 
    points: 1                         # How many points is the exercise worth
    n_visible_trials: 100             # How many visible trials in the test
    n_hidden_trials: 1                # How many hidden trials in the test
    config:
      case_file: tc_fizzbuzz          # Name of the test case file (you won't need to touch this)
      inputs:             
        i:                            # Each input name is a key in 'inputs'
          dtype: int                  # Data type
          check_modified: true        # Whether to check if the input is modified
      outputs:
        fizzbuzz_output:              # Each output name is a key in 'outputs'
          index: 0                    # Position in sequence if there are multiple outputs
          dtype: ''                   # Data type for output, can be left blank
          check_dtype: true           # Whether to check that the output matches the expected type
          check_col_dtypes: true      # Whether to check column dtypes in DataFrames
          check_col_order: true       # Whether to check column order in DataFrames
          check_row_order: true       # Whether to check row order in DataFrames
          check_column_type: true     # Whether to check column dtypes in DataFrames
          float_tolerance: 1.0e-06    # Absolute tolerance for floating point values
  
  freebie:                            # This free exercise doesn't have a 'config' object
    num: 1
    points: 1
    n_visible_trials: 100
    n_hidden_trials: 1
```