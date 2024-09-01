from .test_case_gen import TestCaseGenerator
from .input_gen_utils import dfs_to_conn
from warnings import warn
from numpy.random import default_rng
from inspect import signature

class SampleGenerator(TestCaseGenerator):
    def __init__(self, test_func, sampler_func, output_names=None, seed=None):
        self.test_func = test_func
        n_params = len(signature(sampler_func).parameters)
        if n_params == 1:
            rng = default_rng(seed=seed)
            self.sampler_func = lambda: sampler_func(rng)
        elif n_params == 0:
            self.sampler_func = sampler_func
        else:
            raise ValueError(f'A sampler function must take 0 arguments or take one rng argument. The sampler passed takes {n_params} arguments.')
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
        

class RandomSampleGenerator(SampleGenerator):
    def __init__(self, test_func, sampler_func, output_names=None):
        super().__init__(test_func, sampler_func, output_names)
        


        