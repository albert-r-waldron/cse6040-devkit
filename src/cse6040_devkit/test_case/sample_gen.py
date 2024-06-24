from .test_case_gen import TestCaseGenerator
from .input_gen_utils import dfs_to_conn
from warnings import warn

class SampleGenerator(TestCaseGenerator):
    def __init__(self, test_func, sampler_func, output_names=None):
        self.test_func = test_func
        self.sampler_func = sampler_func
        self.output_names = output_names
    
    def make_inputs(self):
        sampler_output = self.sampler_func()
        if isinstance(sampler_output, dict):
            self.input_data = sampler_output
            self.db_key = None
        elif isinstance(sampler_output, tuple) \
                and isinstance(sampler_output[0], dict) \
                and (isinstance(sampler_output[1], (str, type(None)))) \
                and (len(sampler_output) == 2):
            self.input_data = sampler_output[0]
            self.db_key = sampler_output[1]

        if (self.db_key is not None) \
            and (self.db_key not in self.input_data.keys()):
            warn('DB connection specified is not a key.')
        return self.input_data

    def make_outputs(self):
        staged_inputs = {}
        for param, val in self.input_data.items():
            if param != self.db_key:
                staged_inputs[param] = val
            elif param == self.db_key:
                staged_inputs[param] = dfs_to_conn(val)
        unnamed_outputs = self.test_func(**staged_inputs)
        if not isinstance(unnamed_outputs, tuple):
            unnamed_outputs = (unnamed_outputs,)
        if self.output_names is None:
            self.output_names = tuple(f'output_{i}' for i in range(len(unnamed_outputs)))
        self.output_data = dict(zip(self.output_names, unnamed_outputs))
        return self.output_data
        

        

        