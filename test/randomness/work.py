# %%
# Create two builders
# Second writes notebook/config to different files. Encryption keys are the same.
from cse6040_devkit.assignment import AssignmentBuilder
from cse6040_devkit.utils import compare_test_cases
builder = AssignmentBuilder()
second_builder = AssignmentBuilder(config_path='resource/asnlib/publicdata/asn_config.yaml',
                                   notebook_path='second_nb.ipynb')
# %%
# Create a solution and sampler for the first builder
def create_x(rng):
    return {'x': rng.choice(10, (1,))}

@builder.register_solution('ex_0')
def two_x_plus_three(x):
    return 2*x + 3

@builder.register_sampler('ex_0',
                          two_x_plus_three,
                          100,
                          'out')
def sam1(rng):
    return create_x(rng)

builder.build()
# %%
# Register the "same" sampler to the second builder
@second_builder.register_sampler('ex_0_',
                          two_x_plus_three,
                          100,
                          'out')
def sam2(rng):
    return create_x(rng)

second_builder.build()
# %%
# If the files contain the same objects then the first two outputs in the tuple should be `True`
compare_test_cases('tc_ex_0', 'tc_ex_0_', builder.keys, return_obj=True)

