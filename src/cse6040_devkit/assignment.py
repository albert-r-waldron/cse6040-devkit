import yaml
import os
import nbformat as nbf
import inspect
from textwrap import dedent
from cse6040_devkit.test_case.sample_gen import SampleGenerator
from jinja2 import Environment, PackageLoader
import cse6040_devkit.plugins 
import cse6040_devkit.utils
import dill
from cryptography.fernet import Fernet

def execute_tests(func,
                  ex_name,
                  key,
                  n_iter,
                  hidden=False):
    from time import time
    ex_start = time()
    from cse6040_devkit.tester_fw.testers import Tester
    from yaml import safe_load
    conf_path ='resource/asnlib/publicdata/assignment_config.yaml'
    path = 'resource/asnlib/publicdata/'
    if hidden: path += 'encrypted/'
    with open(conf_path) as f:
        ex_conf = safe_load(f)['exercises'][ex_name]['config']
    ex_conf['func'] = func
    tester = Tester(ex_conf, key, path)
    for _ in range(n_iter):
        try:
            tester.run_test()
            test_case_vars = tester.get_test_vars()
        except Exception as e:
            test_case_vars = tester.get_test_vars()
            print(f'{ex_name} test ran {n_iter} iterations in {time() - ex_start:.2f} seconds')
            print(str(e))
            return False, test_case_vars
    print(f'{ex_name} test ran {n_iter} iterations in {time() - ex_start:.2f} seconds')
    return True, test_case_vars

class AssignmentBlueprint():
    def __init__(self,
                 keys_path='keys.dill'):
        '''AssignmentBlueprints are containers to which assignment components can be registered under an exercise name.
        
        Args:
        - keys_path (str) (optional): Name of the file where encryption keys are stored. Defaults to 'keys.dill'
        '''
        self.core = {}
        self.included = {}
        self.keys_path = keys_path
        if os.path.exists(keys_path):
            with open(keys_path, 'rb') as f:
                self.keys = dill.load(f)
        else:
            self.keys = {
                'visible_key': Fernet.generate_key(),
                'hidden_key': Fernet.generate_key()
            }

    def register_notebook_function(self, ex_name, func_type):
        """Decorator that registers a notebook function to the blueprint.

        Args:
            ex_name (str): Name of the exercise the function applies to.
            func_type (str): Indicates the function type. Must be one of ('solution', 'demo', 'helper')

        Raises:
            ValueError: Raised if func_type us bit valid

        Returns:
            _type_: _description_
        """                
        valid_func_types = ('solution', 'demo', 'helper')
        if func_type not in valid_func_types:
            raise ValueError(f'''func_type must be one of {valid_func_types}''')
        def _register_function(func):
            self.core[ex_name] = self.core.get(ex_name, {})
            self.core[ex_name][func_type] = {
                'name': func.__name__,
                'source': inspect.getsource(func),
                'annotations': {} if func.__annotations__ is None \
                    else{k: str(v).split("'")[1] for k, v in func.__annotations__.items()}
            }
            if func.__doc__:
                self.core[ex_name][func_type]['docstring'] = dedent(func.__doc__)
                self.core[ex_name][func_type]['source'] = self.core[ex_name][func_type]['source']\
                    .replace(f'\n    """{func.__doc__}"""', '')
            return func
        return _register_function
    
    def _register_included_function(self, func_type):
        def _registered_function(func):
            func_name = func.__name__
            self.included[func_type] = self.included.get(func_type, {})
            self.included[func_type][func_name] = func
            setattr(eval(f'cse6040_devkit.{func_type}'), func_name, func)
            # cse6040_devkit.utils.dump_object_to_publicdata(func, func_name)
            return func
        return _registered_function

    def register_plugin(self):
        '''Decorator factory which registers a function as a plugin. The function will be available as `plugins.<function name>` following registration as well as in the target notebook.

        Plugins are decorators intended to wrap solution functions to facilitate testing. 

        **Usage**
        ```
        @bp.register_plugin()
        def foo(func):
            def _func(*args, **kwargs):
                return 'foo' + func(*args, **kwargs)
            return _func
        ```
        This makes `plugins.foo` accessible in both the source files as well as the target notebook. For academia, the plugin prepends the string 'foo' onto whatever is returned by a function call to `func`.
        '''
        return self._register_included_function('plugins')
    
    def register_util(self):
        '''Decorator factory which registers a function as a util. The function will be available as `utils.<function name>` following registration as well as in the target notebook.

        Utils are intended to be used for functions which are called in the notebook code when it is not desired to reveal the function's source code.
        '''
        return self._register_included_function('utils')
    
    def register_solution(self, ex_name: str, free: bool=False):
        '''Decorator factory which registers a function as a solution for the exercise identified by `ex_name`.

        **Effects**:
        - Function definition will be rendered in target notebook solution cell for `ex_name` on build.
            - Use `### BEGIN SOLUTION` and `### END SOLUTION` to mark code which will be removed in the student version.
        - Docstring and type hints will be used to render the prompt and default configuration for `ex_name` on build.
            - Best practice is to use the docstring to provide a brief description of the solution function's inputs, outputs, and behavior
        '''
        self.core[ex_name] = self.core.get(ex_name, {})
        self.core[ex_name]['free'] = free

        return self.register_notebook_function(ex_name, 'solution')
    
    def register_demo(self, ex_name: str):
        '''Decorator factory which registers a function as a demo for the exercise identified by `ex_name`.

        **Effects**:
        - Function body will be rendered in the target notebook at the top indentation level on build
            - The decorated demo function should take no parameters and return no values.
            - The decorated demo function should display the result of calling the solution function on one or more sets of demo inputs using `print`, `display`, etc. 
        - Docstring will be rendered at the top of the "test cell boilerplate" cell for the exercise on build
            - Best practice is to use the docstring to inform students of the expected demo output
        '''
        return self.register_notebook_function(ex_name, 'demo')
    
    def register_helper(self, ex_name):
        '''Decorator factory which registers a function as a helper for the exercise identified by `ex_name`.

        Helper functions are functions provided for the students to use to solve an exercise. The code is rendered in the target notebook. If the code is particularly un-useful to students or they do not need to call the helper function then it may be a better choice to register the function as a util.

        **Effects**:
        - Function definition will be rendered in the target notebook solution cell identified by `ex_name` on build.
        - Docstring will appear in the target notebook prompt cell identified by `ex_name` on build.
            - Best practice is to provide a brief description of how to use the function
            - If no docstring is provided then         
        '''
        return self.register_notebook_function(ex_name, 'helper')
    
    def register_sampler(self, ex_name, sol_func, n_cases, output_names, plugin='', extra_param_names=None, include_hidden=True, **plugin_kwargs):
        '''Decorator factory which registers a function as a sampler for the exercise identified by `ex_name`.
        **Inputs**
        - ex_name (str): identifies the exercise to which the sampler is being registered
        - sol_func (function): the solution to the exercise
        - n_cases (int): number of test cases to generate
        - output_names (tuple|str): Name or names of the outputs of the sol_func
        - plugin (str) (optional): Name of a built-in or registered plugin to use for the test cases. Defaults to an empty string.
        - extra_param_names (list[str]) (optional): List of parameters required by a plugin decorated but not the original solution function. Defaults to None.
        - include_hidden (bool) (optional): Whether to include the hidden test in the notebook. Defaults to True.
        - plugin_kwargs: Additional named arguments are passed as keyword args to the plugin decorator

        **Effects on registration**:
        - Test cases are written to `resource/asnlib/publicdata` and `resource/asnlib/publicdata/encrypted`

        **Effects on build**:
        - Test cells constructed based on registered sampler
        
        '''
        if isinstance(output_names, str):
            output_names = (output_names,)
        def _register_sampler(sampler_func):
            self.core[ex_name] = self.core.get(ex_name, {})
            self.core[ex_name]['test'] = {}
            self.core[ex_name]['test']['visible_path'] = f'resource/asnlib/publicdata/tc_{ex_name}'
            self.core[ex_name]['test']['hidden_path'] = f'resource/asnlib/publicdata/encrypted/tc_{ex_name}'
            self.core[ex_name]['test']['n_cases'] = n_cases
            if plugin:
                if plugin not in dir(cse6040_devkit.plugins):
                    raise ModuleNotFoundError(f'The plugin {plugin} is not defined in the plugins file.')
                plugged_in_name = f'plugins.{plugin}({sol_func.__name__}{", **plugin_kwargs" if plugin_kwargs else ""})'
                self.core[ex_name]['test']['sol_func_name'] = plugged_in_name
                tc_gen = SampleGenerator(getattr(cse6040_devkit.plugins, plugin)(sol_func, **plugin_kwargs), sampler_func, output_names)
            else:
                self.core[ex_name]['test']['sol_func_name'] = sol_func.__name__
                tc_gen = SampleGenerator(sol_func, sampler_func, output_names)
            self.core[ex_name]['test']['tc_gen'] = tc_gen
            self.core[ex_name]['test']['visible_key'] = self.keys['visible_key']
            self.core[ex_name]['test']['hidden_key'] = self.keys['hidden_key']
            self.core[ex_name]['test']['output_names'] = output_names
            self.core[ex_name]['test']['sol_func_argspec'] = inspect.getfullargspec(sol_func)
            if extra_param_names:
                for arg in extra_param_names:
                    self.core[ex_name]['test']['sol_func_argspec'].args.append(arg)
            if plugin_kwargs:
                self.core[ex_name]['test']['plugin_kwargs'] = plugin_kwargs
            return sampler_func
        return _register_sampler
    
    def register_preload_object(self, ex_name: str, obj, obj_name:str):
        """Registers an object to be preloaded before an exercise. Multiple objects _are_ allowed to be registered to the same exercise

        Args:
            ex_name (str): Name of the exercise to register the preload object to
            obj (Any): Object which is serializable with dill
        """
        # cse6040_devkit.utils.dump_object_to_publicdata(obj, obj_name)
        self.core[ex_name] = self.core.get(ex_name, {})
        self.core[ex_name]['preload_objects'] = self.core[ex_name].get('preload_objects', {})
        self.core[ex_name]['preload_objects'][obj_name] = obj

class AssignmentBuilder(AssignmentBlueprint):
    def __init__(self, 
                 config_path='resource/asnlib/publicdata/assignment_config.yaml', 
                 notebook_path='main.ipynb',
                 keys_path='keys.dill',
                 header=True):
        """Assignment Builders are an extension of blueprints. In addition to being able to register components, AssignmentBuilders can register other blueprints and build all of the components into a Jupyter notebook.

        Args:
            config_path (str, optional): Path to the configuration file. Defaults to 'resource/asnlib/publicdata/assignment_config.yaml'.
            notebook_path (str, optional): Path to the target notebook. Defaults to 'main.ipynb'.
            keys_path (str, optional): Name of the file where encryption keys are stored. Defaults to 'keys.dill'.
        """
        super().__init__(keys_path)
        self.config_path = config_path
        self.notebook_path = notebook_path
        self.header = header
        if os.path.exists(config_path):
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}
        if os.path.exists(notebook_path):
            with open(notebook_path) as f:
                self.nb = nbf.read(f, as_version=4)
        else:
            self.nb = nbf.v4.new_notebook()
        self.env = Environment(loader=PackageLoader('cse6040_devkit'))

    def register_blueprint(self, other):
        """Registers a blueprint to the AssignmentBuilder

        Registering a blueprint adds all attributes for each function type (solution, helper, demo, sampler) and exercise name from the blueprint to the builder. 

        Args:
            other (AssignmentBlueprint): The AssignmentBlueprint being registered

        Raises:
            ValueError: When attempting to register an exercise name/function type which already exists.
        """
        for ex_name in other.core:
            if ex_name in self.core:
                # exercise exists in core
                for func_type, attributes in other.core[ex_name].items():
                    if func_type in self.core[ex_name]:
                        # function type already registered - ERROR condition
                        raise ValueError(f'''Can not register duplicates. The name {ex_name}.{func_type} found in {other.__name__} already exists in {self.__name__}''')
                    else:
                        # function type not already registered
                        self.core[ex_name][func_type] = attributes
            else:
                # new exercise in the other core
                self.core[ex_name] = other.core[ex_name]
        self.included.update(other.included)

    def register_blueprints(self, others):
        """Registers a collection of blueprints to the builder

        Performs a series of calls to `register_blueprint`

        Args:
            others (list[AssignmentBlueprint]): _description_
        """
        for other in others:
            self.register_blueprint(other)

    def _write_nb(self):
        self.nb.metadata = {}
        for idx, cell in enumerate(self.nb.cells):
            cell.id = f'{idx}'
            if cell.cell_type == 'code':
                cell.outputs = []
                cell.execution_count = None
        with open(self.notebook_path, 'w') as f:
            nbf.write(self.nb, f)

    def _create_markdown_cell(self, ex_name, tag, source):
        cell = nbf.v4.new_markdown_cell(source=source)
        cell.metadata.tags = [f'{ex_name}.{tag}']
        return cell

    def _create_code_cell(self, ex_name, tag, source):
        cell = nbf.v4.new_code_cell(source=source)
        cell.metadata.tags = [f'{ex_name}.{tag}']
        return cell
    
    def _render_template(self, t_name:str, **kwargs):
        t = self.env.get_template(t_name)
        return t.render(**kwargs)

    def _update_config_from_core(self):
        temp_config = {'assignment_name': 'assignment name',
                       'subtitle': 'assignment subtitle',
                       'version': '0.0.1',
                       'topics': 'this, that, and the other',
                       'points_cap': 'points cap',
                       'total_points': 'total points',
                       'global_imports': None,
                       'exercises': {}}
        temp_config.update(self.config)
        self.config = temp_config
        for ex_num, (ex_name, ex) in enumerate(self.core.items()):
            ex_test = ex.get('test')
            temp_exercise = {
                'num': ex_num,
                'points': 1,
                'n_visible_trials': 100,
                'n_hidden_trials': 1}
            if ex_test:
                annotations = {k: str(v).split("'")[1] for k,v in ex_test['sol_func_argspec'].annotations.items()}
                args = ex_test['sol_func_argspec'].args
                inputs = {var_name: {
                    'dtype': annotations.get(var_name, ''),
                    'check_modified': True} for var_name in args}
                outputs = {var_name:{
                        'index': i,
                        'dtype': '',
                        'check_dtype': True,
                        'check_col_dtypes': True,
                        'check_col_order': True,
                        'check_row_order': True,
                        'check_column_type': True,
                        'float_tolerance': 0.000001
                    }
                for i, var_name in enumerate(ex_test['output_names'])}
                temp_exercise['config'] = {
                    'case_file': f'tc_{ex_name}',
                    'inputs': inputs,
                    'outputs': outputs
                    }
                plugin_kwargs = ex_test.get('plugin_kwargs')
                if plugin_kwargs:
                    with open(f'resource/asnlib/publicdata/{ex_name}_plugin_kwargs', 'wb') as f:
                        dill.dump(plugin_kwargs, f)
            temp_exercise.update(self.config['exercises'].get(ex_name, {}))
            self.config['exercises'][ex_name] = temp_exercise
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(self.config, f, sort_keys=False)

    def _build_core_cells(self):
        from copy import deepcopy
        exercises_core_config = {k:{**self.config['exercises'][k], **self.core.get(k, {})} for k in self.config['exercises']}
        core_cells = {}
        # update header
        if self.header:
            core_cells['main.header'] = self._create_markdown_cell(ex_name='main',
                                                            tag='header',
                                                            source=self._render_template('header.jinja', **self.config))
        # update global imports
        imports = self.config.get('global_imports')
        core_cells['main.global_imports'] = self._create_code_cell(ex_name='main',
                                                                   tag='global_imports',
                                                                   source = self._render_template('global_imports.jinja',
                                                                                            imports=imports,
                                                                                            plugins=self.included.get('plugins'),
                                                                                            utils=self.included.get('utils')))
        # update exercises
        for ex_num, (ex_name, ex) in enumerate(exercises_core_config.items()):
            preload_objects = ex.get('preload_objects')
            if preload_objects:
                core_cells[f'{ex_name}.preload_objects'] = \
                    self._create_code_cell(ex_name=ex_name,
                                        tag='preload_objects',
                                        source=self._render_template('preload_from_file.jinja',
                                                                        preload_objects=preload_objects))
            core_cells[f'{ex_name}.prompt'] = \
                self._create_markdown_cell(ex_name=ex_name,
                                           tag='prompt',
                                           source=self._render_template('prompt.jinja', 
                                                                        ex=ex, 
                                                                        ex_num=ex_num, 
                                                                        ex_name=ex_name,
                                                                        **self.config))
            # update solution
            helper_source = ex.get('helper', {}).get('source')
            if helper_source:
                helper_source = '\n'.join(helper_source.splitlines()[1:])
            demo_source = ex.get('demo', {}).get('source')
            if demo_source:
                demo_source = '\n'.join(demo_source.splitlines()[2:])
                demo_source = dedent(demo_source)
            cleaned_solution_code = ex.get('solution', {}).get('source')
            if cleaned_solution_code:
                cleaned_solution_code = '\n'.join(cleaned_solution_code.splitlines()[1:])
                core_cells[f'{ex_name}.solution'] = \
                    self._create_code_cell(ex_name=ex_name,
                                           tag='solution',
                                           source=self._render_template('solution.jinja',
                                                                        ex=ex,
                                                                        cleaned_soln_code=cleaned_solution_code,
                                                                        demo_source=demo_source,
                                                                        helper_source=helper_source))
                # update test boilerplate
                core_cells[f'{ex_name}.test_boilerplate'] = \
                    self._create_markdown_cell(ex_name=ex_name,
                                               tag='test_boilerplate',
                                               source=self._render_template('test_boilerplate.jinja',
                                                                            ex_name=ex_name,
                                                                            ex_num=ex_num,
                                                                            ex=ex))
            # update test
            _ex = deepcopy(ex)
            if ex.get('free'):
                _ex['config'] = {}
            test_cell =  \
                self._create_code_cell(ex_name=ex_name,
                                       tag='test',
                                       source=self._render_template('test.jinja',
                                                                    ex=_ex,
                                                                    ex_name=ex_name,
                                                                    conf_path=self.config_path))
            test_cell.metadata.update( {
                "nbgrader": {
                "grade": True,
                "grade_id": f"ex_{ex_num}",
                "locked": True,
                "points": ex['points'],
                "solution": False
                }})
            core_cells[f'{ex_name}.test'] = test_cell
        return deepcopy(core_cells)
    
    def build(self):
        """Builds an assignment based on the components registered to the builder. The target notebook will be cleared of output, execution count, and environment metadata.

        These steps are executed upon build
        - Any configuration details not present in the config file are populated with default values
        - The config file is updated
        - The target notebook is updated
            - Any core cells are updated in place
            - Any non-core cells are maintained as-is
            - The current sequence of cells is maintained as-is
            - Any new non-core cells are appended to the end of the target notebook
        """
        if not os.path.exists('./resource/asnlib/publicdata'):
            os.makedirs('./resource/asnlib/publicdata')
        if not os.path.exists('./resource/asnlib/publicdata/encrypted'):
            os.makedirs('./resource/asnlib/publicdata/encrypted')
        with open(self.keys_path, 'wb') as f:
            dill.dump(self.keys, f)
        self._update_config_from_core()
        for ex in self.core.values():
            test = ex.get('test')
            if test and (not ex.get('free', False)):
                tc_gen = test['tc_gen']
                tc_gen.write_cases(test['visible_path'], test['n_cases'], key=self.keys['visible_key'])
                tc_gen.write_cases(test['hidden_path'], test['n_cases'], key=self.keys['hidden_key'])
            preload_objects = ex.get('preload_objects')
            if preload_objects:
                for obj_name, obj in preload_objects.items():
                    cse6040_devkit.utils.dump_object_to_publicdata(obj, obj_name)
        cse6040_devkit.utils.dump_object_to_publicdata(execute_tests, 'execute_tests')
        for func_type, funcs in self.included.items():
            for func_name, func in funcs.items():
                cse6040_devkit.utils.dump_object_to_publicdata(func, func_name)
        core_cells = self._build_core_cells()
        final_nb = nbf.v4.new_notebook()
        for cell in self.nb.cells:
            tags = cell.metadata.get('tags')
            if tags and (tags[0] in core_cells):
                final_nb.cells.append(core_cells.pop(tags[0]))
            else:
                final_nb.cells.append(cell)
        for cell in core_cells.values():
            final_nb.cells.append(cell)
        self.nb = final_nb
        self._write_nb()
