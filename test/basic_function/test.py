#%%
# Import whatever is needed as well as these modules from the devkit.
from cse6040_devkit import assignment, utils, plugins

# Set a seed for usage of RNG in generating test cases
from random import seed
seed(6040)


# Create an instance of AssignmentBlueprint
bp = assignment.AssignmentBlueprint()

# Register an exercise solution
@bp.register_solution(ex_name='fizzbuzz')
def fizzbuzz_soln(i: int):
    """`fizzbuzz_soln` solves the classic "fizzbuzz" problem for a single integer. 

**Inputs**:
- `i` (int): Any integer

**Returns**: one of the following depending on whether 3, 5, both or neither divide evenly into `i`
- `'Fizz'`     if i is divisible by 3                Example: 9
- `'Buzz'`     if i is divisible by 5                Example: 35
- `'FizzBuzz'` if i is divisible by both 3 and 5     Example: 45
- `i`          if i is divisible by neither 3 nor 5  Example: 22
    """
    ### BEGIN SOLUTION
    return ("Fizz"*x_divides_y(3, i)+"Buzz"*x_divides_y(5, i)) or i
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
    """The demo function calls should display this output  

```
fizzbuzz_soln(12) -> Fizz
fizzbuzz_soln(10) -> Buzz
fizzbuzz_soln(15) -> FizzBuzz
fizzbuzz_soln(16) -> 16
```
    """
    for i in [12, 10, 15, 16]:
        print(f'fizzbuzz_soln({i}) -> {fizzbuzz_soln(i)}')

# Register a plugin to be used in solution testing
@bp.register_plugin()
def convert_to_str(func):
    from warnings import warn
    def _func(*args, **kwargs):
        result = func(*args, **kwargs)
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
                     output_names=('fizzbuzz_output',), 
                     plugin='convert_to_str')
def fizzbuzz_sampler():
    from random import randint, seed
    if randint(1,6) < 2:
        return {'i': 15*randint(1, 13)}
    return {'i': randint(1,200)}

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
builder = assignment.AssignmentBuilder(header=False)

# Register blueprint
builder.register_blueprint(bp)
#%%
# Build assignment files
builder.build()
# %%
