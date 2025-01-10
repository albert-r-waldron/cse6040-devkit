from cse6040_devkit.assignment import AssignmentBlueprint, AssignmentBuilder
from cse6040_devkit import utils, plugins

import numpy as np
import pandas as pd
import sqlite3

bp = AssignmentBlueprint()

# Register things to bp

@bp.register_solution(ex_name='plus_ab', free=True)
def plus_ab(a, b):
    """
    Returns a plus b

    args:
    - a, b (int): two numbers to add

    returns:
    - int: sum of a and b
    """
    return a + b

@bp.register_sampler(ex_name='plus_ab',
                     sol_func=plus_ab,
                     n_cases=10,
                     output_names='result')
def ab_sampler(rng: np.random.Generator):
    a, b = rng.integers(-10, 10, 2)
    return {'a': a, 'b': b}

@bp.register_demo('plus_ab',
                  return_replacement='demo_result_plus_ab',
                  return_values_transformer=str)
def plus_ab_demo():
    demo_result_plus_ab = plus_ab(3, 5)
    return demo_result_plus_ab

sel_star_query = bp.register_sql_query(ex_name='sel_star',
                      query='''select * from characters''',
                      doc='Select all records from the characters table')

@bp.register_demo('sel_star',
                  return_values_transformer=utils.render_md_df_text_wrap,
                  return_replacement='utils.display_df_text_wrap(demo_result_sel_star)')
def sel_star_demo():
    with sqlite3.connect('data/star_wars.db') as conn:
        demo_result_sel_star = pd.read_sql(sel_star_query, conn)
    return demo_result_sel_star

char_df = sel_star_demo()

@bp.register_sampler('sel_star', sel_star_query,
                     n_cases=10,
                     output_names='result',
                     plugin='sql_executor',
                     extra_param_names=['conn'])
def sel_star_sampler(rng):
    df = char_df.sample(15, random_state=rng)
    return {'conn': {'characters': df}}, 'conn'

builder = AssignmentBuilder()
builder.register_blueprint(bp)

builder.build()