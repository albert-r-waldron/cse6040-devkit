# 6040 Assignment Framework

## Concept

Conceptually we divide the assignment into three parts: the core, the configuration and the notebook layout.  
- **The core** is the backbone code and its description. 
    - **solution** function - Our correct solution to the problem
    - **demo** function - Function which calls the solution function and displays the printed result
    - **helper** function - Function which either the solution or the test depends on
    - **sampler** function - Function which generates a random set of inputs for the solution function
- **The config** is metadata on the assignment and its exercises
    - assignment:  name, subtitle, topics, points cap, and total points
    - exercise:  number, points, test trials, and test configuration
- **The notebook** is the visual arrangement of the assignment. It a Jupyter notebook made up of core cells and auxiliary cells ("aux cells" for short)
    - **Core cells** - header, footer, global_imports, and exercise prompts/demos/tests.
        - These are defined by the core/config
    - **Aux cells** - Any additional cells included for things like graphic display, additional descriptions, data profiling, etc.
        - These are defined only in the layout

From a birds eye view developers will define the core in Python files and set the configuration in a YAML file. Then the framework builds a Jupyter notebook with the core cells populated. Then **aux cells** can be added to the notebook and the cells can be re-positioning. Subsequent builds will only affect the content of the core cells. The cell positions and aux cell content will remain unchanged.

## Blueprints and registering core functions

#### The framework uses instances of the `AssignmentBlueprint` class is used to organize core functions by exercise and type of function.  

```
from cse6040_devkit.assignment import AssignmentBlueprint

bp = AssignmentBlueprint()
```

#### Functions are added or "registered" to `bp` by annotating their definitions with `bp` decorators. For *solution, demo, and helper* functions, only the exercise name is required by the decorator. Registering these types of core functions stores the source code, docstring, and type hints in the blueprint under the exercise name.

<sub>Type hints and docstrings are optional but highly encouraged. The framework uses them to generate the core markdown cells. Here they are left out to focus on the decorators.</sub>  

```
@bp.register_solution(ex_name='fizzbuzz')
def fizzbuzz_soln(i):
    return ("Fizz"*(i%3==0)+"Buzz"*(i%5==0)) or i

@bp.register_demo(ex_name='fizzbuzz')
def fizzbuzz_demo():
    for i in [12, 10, 15, 16]:
        print(f'fizzbuzz_soln({i}) -> {fizzbuzz_soln(i)}')

@bp.register_helper(ex_name='fizzbuzz')
def fizzbuzz_printer(n):
    for i in range(n):
        print(fizzbuzz_soln(i+1))
```  
* Solution functions should return values which can be pickled.
* Demo functions should take no arguments and return no values. Rather they should display an example of input/output for the solution function.
* There aren't restrictions on helper functions.


#### Registering sampler functions is different because of how they are used. Rather than having their source code inserted into the notebook, the sampler is used to generate a number of random sets of inputs/outputs for the solution function. These are written to encrypted files and metadata is stored in the blueprint.  

```  
@bp.register_sampler(ex_name='fizzbuzz', 
                     sol_func=fizzbuzz_soln, # function to be tested
                     n_cases=30,             # number of test cases to generate
                     output_names=('fizzbuzz_output',)) # optional **tuple** of names for outputs.
def fizzbuzz_sampler():
    from random import randint
    return {'i': randint(1,200)}
```  
* The sampler function should be a valid `sampler_func` which will work with the Test Case framework ([docs](test_case/README.md)).  
* When the sampler is registered the framework will **execute both the sampler _and_ the solution function** to generate test case files.

## Assignment Builder
An `AssignmentBuilder` instance is used to collect blueprints and configuration details and build the notebook.

### Registering blueprints to a builder

```

```