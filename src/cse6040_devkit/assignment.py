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
from copy import deepcopy
from cryptography.fernet import Fernet
from random import randint
import logging

logger = logging.getLogger(__name__)

def execute_tests(func,
                  ex_name,
                  key,
                  n_iter,
                  hidden=False,
                  conf_path='resource/asnlib/publicdata/assignment_config.yaml',
                  path = 'resource/asnlib/publicdata/'):
    from time import time
    ex_start = time()
    from cse6040_devkit.tester_fw.testers import Tester
    from yaml import safe_load
    if hidden: path += 'encrypted/'
    with open(conf_path) as f:
        ex_conf = safe_load(f)['exercises'][ex_name]['config']
    ex_conf['func'] = func
    tester = Tester(ex_conf, key, path)
    for i in range(n_iter):
        try:
            tester.run_test()
            test_case_vars = tester.get_test_vars()
        except Exception as e:
            test_case_vars = tester.get_test_vars()
            print(f'{ex_name} test ran {i} iterations in {time() - ex_start:.2f} seconds')
            return False, test_case_vars, e
    print(f'{ex_name} test ran {i} iterations in {time() - ex_start:.2f} seconds')
    return True, test_case_vars, None

class AssignmentBlueprint():
    def __init__(self,
                 keys_path='keys.dill',
                 include_hidden=True):
        '''AssignmentBlueprints are containers to which assignment components can be registered under an exercise name.
        
        Args:
        - keys_path (str) (optional): Name of the file where encryption keys are stored. Defaults to 'keys.dill'
        '''
        logger.info(f'''Constructing AssignmentBlueprint:
        {keys_path=}
        {include_hidden=}''')
        if not os.path.exists('./data'):
            logger.info("Creating directory ./data")
            os.makedirs('./data')
        if not os.path.exists('./resource/asnlib/publicdata'):
            logger.info("Creating directory ./resource/asnlib/publicdata")
            os.makedirs('./resource/asnlib/publicdata')
        if not os.path.exists('./resource/asnlib/publicdata/encrypted'):
            logger.info("Creating directory ./resource/asnlib/publicdata/encrypted")
            os.makedirs('./resource/asnlib/publicdata/encrypted')
        self.publicdata_path = './resource/asnlib/publicdata'
        self.data_path = './data'
        self._copy_to_publicdata()
        self.core = {}
        self.included = {}
        self.keys_path = keys_path
        self.include_hidden = include_hidden
        if os.path.exists(keys_path):
            with open(keys_path, 'rb') as f:
                self.keys = dill.load(f)
            logger.info(f'Reading keys from file')
            logger.info(f'{self.keys=}')
        else:
            self.keys = {
                'visible_key': Fernet.generate_key(),
                'hidden_key': Fernet.generate_key(),
                'rng_seed': randint(1000, 9999)
            }
            with open(self.keys_path, 'wb') as f:
                dill.dump(self.keys, f)
    def _copy_to_publicdata(self):
        import os
        import shutil
        publicdata_files = set(os.listdir(self.publicdata_path))
        data_files = set(os.listdir(self.data_path))
        un_copied_files = data_files - publicdata_files
        for fn in un_copied_files:
            data_fn = f'{self.data_path}/{fn}'
            publicdata_fn = f'{self.publicdata_path}/{fn}'
            shutil.copy(data_fn, publicdata_fn)
    def parse_ignore(self, s):
        kept = []
        ignoring = False
        for line in s.splitlines():
            if '### BEGIN IGNORE' in line:
                ignoring = True
            if not ignoring:
                kept.append(line)
            else:
                logger.info(f"Ignoring line {line}")
            if '### END IGNORE' in line:
                ignoring = False
        return '\n'.join(kept)
    
    def register_notebook_function(self, ex_name, func_type, wrap_solution=False):
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
            logger.error(f'''func_type must be one of {valid_func_types}''')
            raise ValueError(f'''func_type must be one of {valid_func_types}''')
        logger.info(f'''Registering {func_type} function for exercise '{ex_name}'.''')
        def _register_function(func):
            source = self.parse_ignore(inspect.getsource(func))
            source = cse6040_devkit.utils.extract_definition(source)
            self.core[ex_name] = self.core.get(ex_name, {})
            self.core[ex_name][func_type] = {
                'name': func.__name__,
                'source': source,
                'annotations': {} if func.__annotations__ is None \
                    else{k: str(v).split("'")[1] for k, v in func.__annotations__.items()}
            }
            if func.__doc__:
                self.core[ex_name][func_type]['docstring'] = dedent(func.__doc__)
                self.core[ex_name][func_type]['source'] = self.core[ex_name][func_type]['source']\
                    .replace(f'\n    r"""{func.__doc__}"""', '')\
                    .replace(f'\n    """{func.__doc__}"""', '')
            if wrap_solution and \
                '### BEGIN SOLUTION' not in self.core[ex_name][func_type]['source']:
                
                source_lines = self.core[ex_name][func_type]['source'].splitlines()
                definition = source_lines[0]
                body = '\n'.join(source_lines[1:])
                wrapped_source = f'''{definition}
    ### BEGIN SOLUTION
{body}
    ### END SOLUTION'''
                self.core[ex_name][func_type]['source'] = wrapped_source
            logger.info(f'''Finished regestering''')
            logger.debug(f'Set core["{ex_name}"]["{func_type}"] = {self.core[ex_name][func_type]}')
            return func
        return _register_function

    def register_sql_query(self, ex_name, query, doc, include_note=False):
        name = f'{ex_name}_query'
        if include_note:
            note = dedent('''
                            **Note:** the query is read into a Pandas DataFrame for demos and testing.
                          ''').strip()
        else:
            note = ''
        self.core[ex_name] = self.core.get(ex_name, {})
        self.core[ex_name]['solution'] = {
            'name': name,
            'source': dedent(rf"""
                {name} = '''YOUR QUERY HERE'''
                ### BEGIN SOLUTION
                {name} = '''{query}'''
                ### END SOLUTION
                """).rstrip(),
            'annotations': {},
            'docstring': dedent(f'''
                {dedent(doc)}
                
                {note}''').strip()
        }
        return cse6040_devkit.utils.QueryString(query, ex_name)


    def _register_included_function(self, func_type):
        def _registered_function(func):
            func_name = func.__name__
            logger.info(f"Registering {func_type} function {func_name}")
            self.included[func_type] = self.included.get(func_type, {})
            self.included[func_type][func_name] = func
            setattr(eval(f'cse6040_devkit.{func_type}'), func_name, func)
            logger.info(f"Finished registering")
            logger.info(f"Function is callable as cse6040_devkit.{func_type}.{func_name}")
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
    
    def register_solution(self, ex_name: str, free: bool=False, wrap_solution=True):
        '''Decorator factory which registers a function as a solution for the exercise identified by `ex_name`.

        **Effects**:
        - Function definition will be rendered in target notebook solution cell for `ex_name` on build.
            - Use `### BEGIN SOLUTION` and `### END SOLUTION` to mark code which will be removed in the student version.
        - Docstring and type hints will be used to render the prompt and default configuration for `ex_name` on build.
            - Best practice is to use the docstring to provide a brief description of the solution function's inputs, outputs, and behavior
        '''
        self.core[ex_name] = self.core.get(ex_name, {})
        self.core[ex_name]['free'] = free

        return self.register_notebook_function(ex_name, 'solution', (wrap_solution and not free))
    
    def register_demo(self, ex_name: str, return_values_transformer=None, return_replacement=None):
        '''Decorator factory which registers a function as a demo for the exercise identified by `ex_name`.

        **Effects**:
        - Function body will be rendered in the target notebook at the top indentation level on build
            - The decorated demo function should take no parameters and return no values.
            - The decorated demo function should display the result of calling the solution function on one or more sets of demo inputs using `print`, `display`, etc. 
        - Docstring will be rendered at the top of the "test cell boilerplate" cell for the exercise on build
            - Best practice is to use the docstring to inform students of the expected demo output
        '''
        def _register_demo(func):
            captured_output, \
            raw_return_values, \
            displayable_return_values = cse6040_devkit.utils.capture_output(func, return_values_transformer)
            if raw_return_values is not None:
                self.register_preload_object(ex_name, raw_return_values, f'demo_result_{ex_name}_TRUE')
            func_type = 'demo'
            self.core[ex_name] = self.core.get(ex_name, {})
            self.core[ex_name][func_type] = {
                'name': func.__name__,
                'source': self.parse_ignore(inspect.getsource(func)),
                'annotations': {},
                'return_replacement': return_replacement
            }
            if func.__doc__:
                self.core[ex_name][func_type]['docstring'] = dedent(func.__doc__)
                self.core[ex_name][func_type]['source'] = self.core[ex_name][func_type]['source']\
                    .replace(f'\n    r"""{func.__doc__}"""', '')\
                    .replace(f'\n    """{func.__doc__}"""', '')
            else:
                self.core[ex_name][func_type]['docstring'] = ''
            logger.info(f'''Finished regestering''')
            logger.debug(f'Set core["{ex_name}"]["{func_type}"] = {self.core[ex_name][func_type]}')
            captured_output_doc = '' if not captured_output else \
                f'''
**The demo should display this printed output.**
```
{dedent(captured_output).strip()}
```
'''
            rendered_output_doc = '' if not displayable_return_values else \
                f'''
**The demo should display this output.**  

{displayable_return_values.strip()}
'''
            self.core[ex_name][func_type]['docstring'] += f'''
{rendered_output_doc}{captured_output_doc}
'''
            return func
        return _register_demo
    
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
    
    def register_sampler(self, ex_name, sol_func, n_cases, output_names, plugin='', extra_param_names=None, include_hidden=None, **plugin_kwargs):
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
        _sol_func_name = sol_func.__name__
        _argspec = getattr(sol_func, '__argspec__', None)
        if _argspec is None:
            _argspec = inspect.getfullargspec(sol_func)
        def _register_sampler(sampler_func):
            logger.info(f"Registering sampler function {sampler_func.__name__} for exercise {ex_name}")
            self.core[ex_name] = self.core.get(ex_name, {})
            self.core[ex_name]['test'] = {}
            self.core[ex_name]['test']['visible_path'] = f'resource/asnlib/publicdata/tc_{ex_name}'
            self.core[ex_name]['test']['hidden_path'] = f'resource/asnlib/publicdata/encrypted/tc_{ex_name}'
            self.core[ex_name]['test']['n_cases'] = n_cases
            if include_hidden is not None:
                self.core[ex_name]['test']['include_hidden'] = include_hidden
            else:
                self.core[ex_name]['test']['include_hidden'] = self.include_hidden
            seed = self.keys['rng_seed']

            if plugin:
                if plugin not in dir(cse6040_devkit.plugins):
                    raise ModuleNotFoundError(f'The plugin {plugin} is not defined in the plugins file.')
                plugged_in_name = f'plugins.{plugin}({_sol_func_name}{", **plugin_kwargs" if plugin_kwargs else ""})'
                self.core[ex_name]['test']['sol_func_name'] = plugged_in_name
                tc_gen = SampleGenerator(getattr(cse6040_devkit.plugins, plugin)(sol_func, **plugin_kwargs), sampler_func, output_names, seed=seed)
            else:
                self.core[ex_name]['test']['sol_func_name'] = _sol_func_name
                tc_gen = SampleGenerator(sol_func, sampler_func, output_names, seed=seed)
            tc_gen.make_inputs() # needed to set the db_key below
            self.core[ex_name]['test']['db_key'] = tc_gen.db_key
            self.core[ex_name]['test']['tc_gen'] = tc_gen
            self.core[ex_name]['test']['visible_key'] = self.keys['visible_key']
            self.core[ex_name]['test']['hidden_key'] = self.keys['hidden_key']
            self.core[ex_name]['test']['output_names'] = output_names
            self.core[ex_name]['test']['sol_func_argspec'] = _argspec
            if extra_param_names:
                for arg in extra_param_names:
                    self.core[ex_name]['test']['sol_func_argspec'].args.append(arg)
            if plugin_kwargs:
                self.core[ex_name]['test']['plugin_kwargs'] = plugin_kwargs
            logger.info(f"Registration finished")
            logger.info(f"core['{ex_name}']['test] = {self.core[ex_name]['test']}")
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
        logger.info(f'Registered preload object: {obj_name} for exercise {ex_name}')

class AssignmentBuilder(AssignmentBlueprint):
    def __init__(self, 
                 config_path='resource/asnlib/publicdata/assignment_config.yaml', 
                 notebook_path='main.ipynb',
                 keys_path='keys.dill',
                 header=True,
                 include_hidden=True,
                 data_path='data',
                 publicdata_path='resource/asnlib/publicdata',
                 kernelspec={'kernelspec': {"display_name": "Python 3.8",
                                            "language": "python",
                                            "name": "python38"}}):
        """Assignment Builders are an extension of blueprints. In addition to being able to register components, AssignmentBuilders can register other blueprints and build all of the components into a Jupyter notebook.

        Args:
            config_path (str, optional): Path to the configuration file. Defaults to 'resource/asnlib/publicdata/assignment_config.yaml'.
            notebook_path (str, optional): Path to the target notebook. Defaults to 'main.ipynb'.
            keys_path (str, optional): Name of the file where encryption keys are stored. Defaults to 'keys.dill'.
        """

        logger.info(f'''Constructing AssignmentBuilder''')
        super().__init__(keys_path=keys_path, include_hidden=include_hidden)
        self.config_path = config_path
        self.notebook_path = notebook_path
        self.header = header
        self.kernelspec = kernelspec
        logger.info(f'\n{config_path=}\n{notebook_path=}\n{header=}\n{include_hidden=}\n{kernelspec}')
        if os.path.exists(notebook_path):
            logger.info(f'Loading notebook from file')
            with open(notebook_path) as f:
                self.nb = nbf.read(f, as_version=4)
        else:
            logger.info('Notebook file not found')
            self.nb = nbf.v4.new_notebook()
            logger.info('Notebook initialized')
        self.env = Environment(loader=PackageLoader('cse6040_devkit'))
        self.data_path = data_path
        self.publicdata_path = publicdata_path

    def _load_config_from_file(self):
        if os.path.exists(self.config_path):
            logger.info('Loading config from file')
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f)
            logger.info('Config loaded')
        else:
            logger.info('Config file not found')
            self.config = {}
            logger.info('Config initialized')

    def register_blueprint(self, other):
        """Registers a blueprint to the AssignmentBuilder

        Registering a blueprint adds all attributes for each function type (solution, helper, demo, sampler) and exercise name from the blueprint to the builder. 

        Args:
            other (AssignmentBlueprint): The AssignmentBlueprint being registered

        Raises:
            ValueError: When attempting to register an exercise name/function type which already exists.
        """
        logger.info(f'Registering blueprint to the builder')
        for ex_name in other.core:
            logger.info(f'Registering data for {ex_name}')
            if ex_name in self.core:
                logger.info(f'{ex_name} already exists in the builder. Registering functions one at a time.')
                for func_type, attributes in other.core[ex_name].items():
                    logger.info(f'Registering {func_type} function for exercise {ex_name}')
                    if func_type in self.core[ex_name]:
                        if func_type == 'preload_objects':
                            self.core[ex_name][func_type].update(attributes)
                        else:
                            # function type already registered - ERROR condition
                            logger.error(f'''Can not register duplicates of the same function type and exercise. The name {ex_name}.{func_type} already exists.''')
                            raise ValueError(f'''Can not register duplicates. The name {ex_name}.{func_type} already exists.''')
                    else:
                        # function type not already registered
                        self.core[ex_name][func_type] = attributes
                        logger.info('Registered.')
            else:
                # new exercise in the other core
                logger.info(f'{ex_name} not found in the builder. Registering entire exercise.')
                self.core[ex_name] = other.core[ex_name]
                logger.info(f'Registered.')
        self.included.update(other.included)
        logger.debug(f'{self.core=}')

    def register_blueprints(self, others):
        """Registers a collection of blueprints to the builder

        Performs a series of calls to `register_blueprint`

        Args:
            others (list[AssignmentBlueprint]): _description_
        """
        for other in others:
            self.register_blueprint(other)

    def get_tc_gen(self, ex_name):
        return self.core.get(ex_name, {}).get('test', {}).get('tc_gen')
    
    def _write_nb(self):
        logger.info(f'Writing notebook to {self.notebook_path}')
        self.nb.metadata = self.kernelspec
        for idx, cell in enumerate(self.nb.cells):
            cell.id = f'{idx}'
            if cell.cell_type == 'code':
                cell.outputs = []
                cell.execution_count = None
        with open(self.notebook_path, 'w') as f:
            nbf.write(self.nb, f)
        logger.info('Notebook written.')

    def _create_markdown_cell(self, ex_name, tag, source):
        full_tag = f'{ex_name}.{tag}'
        logger.info(f"Creating markdown cell with metadata tag {full_tag}")
        cell = nbf.v4.new_markdown_cell(source=source)
        cell.metadata.tags = [full_tag]
        logger.info(f"Cell successfully created; {full_tag=}")
        return cell

    def _create_code_cell(self, ex_name, tag, source):
        full_tag = f'{ex_name}.{tag}'
        logger.info(f"Creating code cell with metadata tag {full_tag}")
        cell = nbf.v4.new_code_cell(source=source)
        cell.metadata.tags = [full_tag]
        logger.info(f"Cell successfully created; {full_tag=}")
        return cell
    
    def _render_template(self, t_name:str, **kwargs):
        logger.info(f"Rendering template {t_name}")
        t = self.env.get_template(t_name)
        logger.info(f"Template {t_name} rendered")
        return t.render(**kwargs)

    def _update_config_from_core(self):
        logger.info(f"Updating the configuration based on core registry")
        logger.info("Setting default top level values")
        temp_config = {'assignment_name': 'assignment name',
                       'subtitle': 'assignment subtitle',
                       'version': '0.0.1',
                       'topics': 'this, that, and the other',
                       'points_cap': 'points cap',
                       'total_points': 'total points',
                       'global_imports': [{'module': 're'},
                                          {'module': 'pandas', 'alias': 'pd'}],
                       'exercises': {}}
        logger.info(f"Updating default values with config read from file.")
        temp_config.update(self.config)
        ###
        temp_config['exercises'] = {k:v for k, v in temp_config['exercises'].items() if k in self.core}
        ###
        self.config = temp_config
        logger.info(f"Top level config set. Updating exercise configurations.")
        for ex_num, (ex_name, ex) in enumerate(self.core.items()):
            logger.info(f"Setting default values for exercise {ex_name}")
            ex_test = ex.get('test')
            temp_exercise = {
                'num': ex_num,
                'points': 1,
                'n_visible_trials': 100,
                'n_hidden_trials': 1}
            if ex_test:
                logger.info(f"Test is defined for exercise {ex_name}")
                annotations = {k: str(v).split("'")[1] for k,v in ex_test['sol_func_argspec'].annotations.items()}
                args = ex_test['sol_func_argspec'].args
                db_key = ex_test.get('db_key', '')
                if db_key:
                    logger.info(f'Database connection registered as argument `{db_key}` for exercise {ex_name}')
                else:
                    logger.info(f'No database connection registered for exercise {ex_name}')
                logger.info(f"Setting default test configuration values for exercise {ex_name}")
                inputs = {var_name: {
                    'dtype': annotations.get(var_name, 'db' if var_name == db_key else ''),
                    'check_modified': False if var_name == db_key else True} for var_name in args}
                outputs = {var_name:{
                        'index': i,
                        'dtype': '',
                        'check_dtype': True,
                        'check_col_dtypes': True,
                        'check_col_order': True,
                        'check_row_order': False,
                        'float_tolerance': 0.000001
                    }
                for i, var_name in enumerate(ex_test['output_names'])}
                temp_exercise['config'] = {
                    'case_file': f'tc_{ex_name}',
                    'inputs': inputs,
                    'outputs': outputs
                    }
                logger.info(f"Default test configuration values for exercise {ex_name} set")
                plugin_kwargs = ex_test.get('plugin_kwargs')
                if plugin_kwargs:
                    logger.info(f"Serializing plugin kwarg mapping")
                    with open(f'resource/asnlib/publicdata/{ex_name}_plugin_kwargs', 'wb') as f:
                        dill.dump(plugin_kwargs, f)
                    logger.info(f"Plugin kwarg mapping persisted")
                logger.info(f"Updating exercise {ex_name} with values from file.")
            temp_exercise.update(self.config['exercises'].get(ex_name, {}))
            ###
            existing_config = deepcopy(self.config['exercises'].get(ex_name, {}).get('config'))
            if existing_config:
                existing_inputs = existing_config['inputs']
                existing_outputs = existing_config['outputs']
                temp_exercise['config']['inputs'] = {k: existing_inputs.get(k, v) for k, v in inputs.items()}
                temp_exercise['config']['outputs'] = {k: existing_outputs.get(k, v) for k, v in outputs.items()}
                temp_exercise['config']['case_file'] = f'tc_{ex_name}'
            ###
            self.config['exercises'][ex_name] = temp_exercise
            logger.info(f"Completed update of exercise {ex_name} configuration.")
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(self.config, f, sort_keys=False)
        logger.info(f"Config persisted in {self.config_path}")
        try:
            logger.info("Creating symlink to config file in working directory")
            os.symlink(self.config_path, 'assignment_config.yaml')
        except:
            logger.warning("Unable to create symlink. It may already exist.")

    def _build_core_cells(self):
        logger.info("Building core notebook cells.")
        from copy import deepcopy
        logger.info("Merging core and config")
        exercises_core_config = {k:{**self.config['exercises'][k], **self.core.get(k, {})} for k in self.config['exercises']}
        self.core_cells = {}
        # update header
        if self.header:
            logger.info("Building header cell")
            self.core_cells['main.header'] = self._create_markdown_cell(ex_name='main',
                                                            tag='header',
                                                            source=self._render_template('header.jinja', **self.config))
        else:
            logger.info("Header cell is suppressed.")
        # update global imports
        logger.info(f"Building global imports cell")
        imports = self.config.get('global_imports')
        self.core_cells['main.global_imports'] = self._create_code_cell(ex_name='main',
                                                                   tag='global_imports',
                                                                   source = self._render_template('global_imports.jinja',
                                                                                            imports=imports,
                                                                                            plugins=self.included.get('plugins'),
                                                                                            utils=self.included.get('utils')))
        # update exercises
        logger.info(f"Building exercise cell groups")
        for ex_num, (ex_name, ex) in enumerate(exercises_core_config.items()):
            ex_str = f'for exercise {ex_name}'
            preload_objects = ex.get('preload_objects')
            if preload_objects:
                logger.info(f"Building preload objects cell {ex_str}")
                self.core_cells[f'{ex_name}.preload_objects'] = \
                    self._create_code_cell(ex_name=ex_name,
                                        tag='preload_objects',
                                        source=self._render_template('preload_from_file.jinja',
                                                                        preload_objects=preload_objects))
            else:
                logger.info(f"No preload objects registered {ex_str}")
            logger.info(f"Building exercise {ex_name}")
            self.core_cells[f'{ex_name}.prompt'] = \
                self._create_markdown_cell(ex_name=ex_name,
                                           tag='prompt',
                                           source=self._render_template('prompt.jinja', 
                                                                        ex=ex, 
                                                                        ex_num=ex_num, 
                                                                        ex_name=ex_name,
                                                                        **self.config))
            # update solution
            logger.info(f"Building solution cell {ex_str}")
            helper_source = ex.get('helper', {}).get('source')
            if helper_source:
                logger.info("Adding helper function")
                # helper_source = '\n'.join(helper_source.splitlines()[1:])
            ex_demo = ex.get('demo', {})
            demo_source = ex_demo.get('source')
            demo_return_replacement = ex_demo.get('return_replacement', '')
            if demo_source:
                logger.info("Adding demo")
                demo_source = cse6040_devkit.utils.replace_return(demo_source, demo_return_replacement)
            cleaned_solution_code = ex.get('solution', {}).get('source')
            if cleaned_solution_code:
                logger.info(f"Solution code is registered {ex_str}.")
                # cleaned_solution_code = '\n'.join(cleaned_solution_code.splitlines()[1:])
                self.core_cells[f'{ex_name}.solution'] = \
                    self._create_code_cell(ex_name=ex_name,
                                           tag='solution',
                                           source=self._render_template('solution.jinja',
                                                                        ex=ex,
                                                                        cleaned_soln_code=cleaned_solution_code,
                                                                        demo_source=demo_source,
                                                                        helper_source=helper_source))
                # update test boilerplate
                if ex.get('demo', {}).get('docstring'):
                    logger.info(f"Adding demo docstring to test boilerplate {ex_str} ")
                self.core_cells[f'{ex_name}.test_boilerplate'] = \
                    self._create_markdown_cell(ex_name=ex_name,
                                               tag='test_boilerplate',
                                               source=self._render_template('test_boilerplate.jinja',
                                                                            ex_name=ex_name,
                                                                            ex_num=ex_num,
                                                                            ex=ex))
            else:
                logger.info(f"No solution found {ex_str}. Skipping building solution and test boilerplate cells.")
            # update test
            if ex.get('free'):
                logger.info(f"Exercise {ex_name} is designated as free. Rendering empty test.")
                _ex = deepcopy(ex)
                _ex['config'] = {}
            else:
                _ex = ex
                logger.info(f"Building test {ex_str}")
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
            self.core_cells[f'{ex_name}.test'] = test_cell
        return deepcopy(self.core_cells)
    
    def _write_artifact_files(self):
        logger.info(f"Writing artifact files")
        for ex_name, ex in self.core.items():
            test = ex.get('test')
            if test and (not ex.get('free', False)):
                logger.info(f"Writing test case files for {ex_name}")
                tc_gen = test['tc_gen']
                tc_gen.write_cases(test['visible_path'], test['n_cases'], key=self.keys['visible_key'])
                tc_gen.write_cases(test['hidden_path'], test['n_cases'], key=self.keys['hidden_key'])
            else:
                logger.info(f"No test cases to write for {ex_name}")
            preload_objects = ex.get('preload_objects')
            if preload_objects:
                for obj_name, obj in preload_objects.items():
                    logger.info(f"Writing preload object file {obj_name} for {ex_name}")
                    cse6040_devkit.utils.dump_object_to_publicdata(obj, obj_name)
        logger.info("Writing 'execute_tests' file.")
        cse6040_devkit.utils.dump_object_to_publicdata(execute_tests, 'execute_tests')
        for _, funcs in self.included.items():
            for func_name, func in funcs.items():
                new_func = deepcopy(func)
                new_func.__module__ = '__main__'
                logger.info(f"Writing '{func_name}' file.")
                cse6040_devkit.utils.dump_object_to_publicdata(new_func, func_name)
        logger.info("Artifact files successfully written.")
                

    def build(self):
        """Builds an assignment based on the components registered to the builder. The target notebook will be cleared of output, execution count, and environment metadata.

        These steps are executed upon build
        - Any configuration details not present in the config file are populated with default values
        - The config file is updated
        - The target notebook is updated
            - Any core cells are updated in place
            - Any non-core cells are maintained as-is
            - The current sequence of cells is maintained as-is
            - Any new core cells are appended to the end of the target notebook
        """
        self._load_config_from_file()
        self._update_config_from_core()
        self._write_artifact_files()
        core_cells = self._build_core_cells()
        final_nb = nbf.v4.new_notebook()
        logger.info(f"Iterating over cells in {self.notebook_path}")
        for cell in self.nb.cells:
            tags = cell.metadata.get('tags')
            tag_match_core_cell = False
            if tags:
                tag_match_core_cell = (tags[0] in core_cells)
                logger.info(f"Found tags {tags} in existing notebook")
            else:
                logger.info(f"Cell is untagged")
            
            if tags and tag_match_core_cell:
                logger.info(f"Core cell with tag {tags[0]} found. Updating from this AssignmentBuilder")
                final_nb.cells.append(core_cells.pop(tags[0]))
            else:
                logger.info("No core cell with matching tag exists. Leaving unchanged.")
                final_nb.cells.append(cell)
        logger.info("Finished with existing notebook cells. Appending remaining core cells.")
        for cell_tag, cell in core_cells.items():
            logger.info(f"Appending core cell with tags {cell_tag}")
            final_nb.cells.append(cell)
        self.nb = final_nb
        self._write_nb()
