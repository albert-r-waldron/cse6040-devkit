class TestCaseGenerator():
    def __init__(self):
        print(f'initializing {__class__}')
        self.input_data = None
        self.output_data = None

    def make_case(self):
        self.input_data = self.make_inputs()
        self.output_data = self.make_outputs()
        arg_names = set(self.input_data.keys()) | set(self.output_data.keys())
        return {name:self.output_data.get(name, self.input_data.get(name)) for name in arg_names}

    def write_cases(self, path, n_cases=100, key=b'sIRWMgIhwENImJyOel3HWJDMr0VbXzfbq-uwgd09VFs='):
        import dill as pickle
        from cryptography.fernet import Fernet
        if key is None:
            key = Fernet.generate_key()
        fernet = Fernet(key)
        cases = [self.make_case() for _ in range(n_cases)]
        with open(path, 'wb') as f_out:
            f_out.write(fernet.encrypt(pickle.dumps(cases)))
        return key
    
    def read_cases(self, path, key=b'sIRWMgIhwENImJyOel3HWJDMr0VbXzfbq-uwgd09VFs='):
        import dill as pickle
        from cryptography.fernet import Fernet
        fernet = Fernet(key)
        with open(path, 'rb') as fin:
            self.cases = pickle.loads(fernet.decrypt(fin.read()))
        return self.cases
        
    def make_inputs(self):
        # Make randomly generated inputs to your function
        # The self.input_data field should be returned as a dictionary. 
            # keys - input argument name
            # values - input argument values
        raise NotImplementedError

    def make_outputs(self):
        # call function being tested and return outputs.
        # returns a dictionary
            # keys - meaningful name for output (just "output" is fine for only one)
        raise NotImplementedError
