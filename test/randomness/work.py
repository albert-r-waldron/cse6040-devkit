# %%
# Create two builders
# Second writes notebook/config to different files. Encryption keys are the same.
from cse6040_devkit.assignment import AssignmentBuilder
builder = AssignmentBuilder()
second_builder = AssignmentBuilder(config_path='resource/asnlib/publicdata/asn_config.yaml',
                                   notebook_path='second_nb.ipynb')
# %%
# Create a solution and sampler for the first builder
def create_x():
    return {'x': rng.choice(10_000, (1,))}

@builder.register_solution('ex_0')
def two_x_plus_three(x):
    return 2*x + 3

@builder.register_sampler('ex_0',
                          two_x_plus_three,
                          100,
                          'out',
                          plugin='postprocess_sort')
def sam1():
    return create_x()

# Set the rng seed and build the first builder
import numpy as np
rng = np.random.default_rng(6040)
builder.build()
# %%
# Register the "same" sampler to the second builder
@second_builder.register_sampler('ex_0_',
                          two_x_plus_three,
                          100,
                          'out')
def sam2():
    return create_x()
# Set the rng seed and build the second builder
# This will write a second set of test cases using the same logic and a rng with the same seed -- The expectation is that the objects in `tc_ex_0` match the objects in `tc_ex_0_`
rng = np.random.default_rng(6040)
second_builder.build()
# %%
# Compares two pickled objects using the tester_fw compare_copies function
# Maybe add this as a util???
def compare_pickled_objects(name, other_name, return_obj=False):
    import dill as pickle
    from cryptography.fernet import Fernet
    from cse6040_devkit.tester_fw.test_utils import compare_copies
    def read_file(fn, key):
        fernet = Fernet(key)
        with open(fn, 'rb') as fin:
            obj = pickle.loads(fernet.decrypt(fin.read()))
        return obj
    path = 'resource/asnlib/publicdata/'
    enc_path = path + 'encrypted/'
    obj = read_file(path + name, builder.keys['visible_key'])
    old_obj = read_file(path + other_name, builder.keys['visible_key'])
    visible_same = compare_copies(obj, old_obj)
    hobj = read_file(enc_path + name, builder.keys['hidden_key'])
    hold_obj = read_file(enc_path + other_name, builder.keys['hidden_key'])
    hidden_same = visible_same = compare_copies(hobj, hold_obj)
    if return_obj:
        return visible_same, hidden_same, obj, old_obj, hobj, hold_obj
    return visible_same, hidden_same
# If the files contain the same objects then the first two outputs in the tuple should be `True`
compare_pickled_objects('tc_ex_0', 'tc_ex_0_', True)

