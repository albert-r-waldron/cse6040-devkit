import yaml
import os
import nbformat as nbf
import inspect
from textwrap import dedent
from cse6040_devkit.test_case.sample_gen import SampleGenerator
from jinja2 import Environment, PackageLoader
import cse6040_devkit.plugins 
import dill

class AssignmentBlueprint():
    def __init__(self):
        self.core = {}
        self.plugins = {}
        if not os.path.exists('./resource/asnlib/publicdata'):
            os.makedirs('./resource/asnlib/publicdata')
        if not os.path.exists('./resource/asnlib/publicdata/encrypted'):
            os.makedirs('./resource/asnlib/publicdata/encrypted')

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
    
    def register_plugin(self):
        def _register_plugin(func):
            plugin_name = func.__name__
            plugin_path = f'resource/asnlib/publicdata/plugin.{plugin_name}.dill'
            self.plugins[plugin_name] = plugin_path
            # set the attribute locally in case it's needed in the source files
            setattr(cse6040_devkit.plugins, plugin_name, func)
            # dump it to a file
            with open(plugin_path, 'wb') as f:
                dill.dump(func, f)
            return func
        return _register_plugin
    
    def register_solution(self, ex_name):
        return self.register_notebook_function(ex_name, 'solution')
    
    def register_demo(self, ex_name):
        return self.register_notebook_function(ex_name, 'demo')
    
    def register_helper(self, ex_name):
        return self.register_notebook_function(ex_name, 'helper')
    
    def register_sampler(self, ex_name, sol_func, n_cases, output_names, plugin='', extra_param_names=None, **plugin_kwargs):
        def _register_sampler(sampler_func):
            self.core[ex_name] = self.core.get(ex_name, {})
            self.core[ex_name]['test'] = {}
            visible_path = f'resource/asnlib/publicdata/tc_{ex_name}'
            hidden_path = f'resource/asnlib/publicdata/encrypted/tc_{ex_name}'
            if plugin:
                if plugin not in dir(cse6040_devkit.plugins):
                    raise ModuleNotFoundError(f'The plugin {plugin} is not defined in the plugins file.')
                plugged_in_name = f'plugins.{plugin}({sol_func.__name__}{", **plugin_kwargs" if plugin_kwargs else ""})'
                self.core[ex_name]['test']['sol_func_name'] = plugged_in_name
                tc_gen = SampleGenerator(getattr(cse6040_devkit.plugins, plugin)(sol_func, **plugin_kwargs), sampler_func, output_names)
            else:
                self.core[ex_name]['test']['sol_func_name'] = sol_func.__name__
                tc_gen = SampleGenerator(sol_func, sampler_func, output_names)
            self.core[ex_name]['test']['visible_key'] = tc_gen.write_cases(visible_path, n_cases, key=None)
            self.core[ex_name]['test']['hidden_key'] = tc_gen.write_cases(hidden_path, n_cases, key=None)
            self.core[ex_name]['test']['output_names'] = output_names
            self.core[ex_name]['test']['sol_func_argspec'] = inspect.getfullargspec(sol_func)
            if extra_param_names:
                for arg in extra_param_names:
                    self.core[ex_name]['test']['sol_func_argspec'].args.append(arg)
            if plugin_kwargs:
                self.core[ex_name]['test']['plugin_kwargs'] = plugin_kwargs
            return sampler_func
        return _register_sampler

class AssignmentBuilder(AssignmentBlueprint):
    def __init__(self, 
                 config_path='resource/asnlib/publicdata/assignment_config.yaml', 
                 notebook_path='main.ipynb',
                 template_dir='templates'):
        self.config_path = config_path
        self.notebook_path = notebook_path
        self.core = {}
        self.plugins = {}
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
        self.plugins.update(other.plugins)

    def register_blueprints(self, others):
        for other in others:
            self.register_blueprint(other)

    def _write_nb(self):
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
                       'topics': ['topic', '...'],
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

    def build_core_cells(self):
        from copy import deepcopy
        exercises_core_config = {k:{**self.config['exercises'][k], **self.core.get(k, {})} for k in self.config['exercises']}
        core_cells = {}
        # update header
        core_cells['main.header'] = self._create_markdown_cell(ex_name='main',
                                                          tag='header',
                                                          source=self._render_template('header.jinja', **self.config))
        # update global imports
        imports = self.config.get('global_imports')
        core_cells['main.global_imports'] = self._create_code_cell(ex_name='main',
                                                                   tag='global_imports',
                                                                   source = self._render_template('global_imports.jinja',
                                                                                            imports=imports,
                                                                                            plugins=self.plugins))
        # update exercises
        for ex_num, (ex_name, ex) in enumerate(exercises_core_config.items()):
            # print(ex)
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
            test_cell =  \
                self._create_code_cell(ex_name=ex_name,
                                       tag='test',
                                       source=self._render_template('test.jinja',
                                                                    ex=ex,
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
        self._update_config_from_core()
        core_cells = self.build_core_cells()
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
