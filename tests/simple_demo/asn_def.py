from cse6040_devkit.assignment import AssignmentBlueprint
from cse6040_devkit.assignment import AssignmentBuilder
from textwrap import dedent
from cse6040_devkit import utils, plugins
from contextlib import redirect_stdout
import io

bp = AssignmentBlueprint()


@bp.register_solution('gt_comparison')
def x_gt_y(x, y):
    """Return `True` if `x` is greater than `y`. `False` otherwise.
    """
    return x > y

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

@bp.register_sampler('gt_comparison',
                     x_gt_y, 
                     20, 
                     'out0')
def samp_1(rng):
    x, y = rng.integers(-500, 500, 2)
    return {'x': x, 'y': y}

@bp.register_solution('lin_print_fac')
def lin_printer_fac(m, b):
    def f(x):
        y = m*x + b
        print(f'f({x}) = {m}({x}) + {b} = {y}')
        return y
    return f

@bp.register_plugin()
def print_handler(func, show_printed_output=False):
    def wrapped_func(m, b, x):
        # Temporarily capture `stdout` in buffer
        with io.StringIO() as buffer, redirect_stdout(buffer):
            # call func(m, b) and store buffer
            y = func(m, b)(x)
            printed_output = buffer.getvalue()
        # Print the captured output if enabled
        if show_printed_output:
            print(printed_output)
        # Return both the result and the printed output 
        return y, printed_output
    return wrapped_func

@bp.register_sampler('lin_print_fac',
                     lin_printer_fac,
                     20,
                     ('y', 'printed_output'),
                     plugin='print_handler',
                     extra_param_names=['x'],
                     show_printed_output=False)
def print_update_sampler(rng):
    m, x, b = rng.uniform(-5, 5, 3).round(3)
    return {'m':m, 'x': x, 'b':b}

@bp.register_demo('lin_print_fac')
def lpf_demo():
    wp_lin_printer_fac = plugins.print_handler(lin_printer_fac,
                                               show_printed_output=True)
    ### three examples
    demo_result_lin_printer_fac = [
        wp_lin_printer_fac(m=3, b=3, x=1),
        wp_lin_printer_fac(m=4, b=-0.5, x=8),
        wp_lin_printer_fac(m=9, b=140, x=12)
    ]
    return demo_result_lin_printer_fac


builder = AssignmentBuilder(header=False)
builder.register_blueprint(bp)

# # This won't work anymore
# builder.config['total_points'] = 50

builder.build()
