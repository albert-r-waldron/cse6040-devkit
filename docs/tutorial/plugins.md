# Plugins

Plugins are functions which are used to decorate student solutions for testing. The plugin should take a function as an argument (it may take additional arguments). It should return a callable function. This output function is what is used behind the scenes to generate the test cases and insert the necessary code into the assignment.

## What does a plugin look like?

```python
def example_plugin(func, **plugin_kwargs):
    def output_function(**kwargs):
        # use `func` here. You can include pre or post execution code as well.
    return output_function
```

## Usage

Plugin usage is specified as part of registering the sampler for an exercise. The following parameters can be set.  
- `plugin` (str): The name of the plugin to use.
- `extra_param_names` (list[str]): names of any parameters used in `output_function` which are not used in `func`.
  - Note: the associated sampler function output should have these names as keys.
- `**plugin_kwargs` (any): Additional named parameters given in the `register_sampler` invocation will be passed as named parameters to the plugin.

## Built-in plugins

Several plugins for common use-cases are built in. See `cse6040_devkit.plugins` for details on what's available.

## Roll your own plugins

There are many one-off instances where a plugin is desired but there is not a generic use-case for creating a built-in. In that case we can register a plugin using the `register_plugin` decorator. 

```python
@bp.register_plugin()
def foo(func):
    def _func(*args, **kwargs):
        return 'foo' + func(*args, **kwargs)
    return _func
```
