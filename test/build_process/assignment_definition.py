from cse6040_devkit.assignment import AssignmentBuilder

builder = AssignmentBuilder()

@builder.register_solution('linear_function')
def two_x_plus_three(x: int)->int:
    """This function is an implementation of the linear function $f(x) = 2x + 3$.

Inputs:
    x (int): The variable x in the linear function

Outputs:
    int: value of $2x+3$
    """
    ### BEGIN SOLUTION
    return 2*x+3
    ### END SOLUTION

@builder.register_sampler(ex_name='linear_function',
                          sol_func=two_x_plus_three,
                          n_cases=100,
                          output_names='result')
def random_x():
    from random import randint
    return {'x': randint(-1000, 1000)}

from random import seed
seed('CSE 6040')

builder.build()