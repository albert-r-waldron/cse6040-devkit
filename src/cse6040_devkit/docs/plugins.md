# Plugins

It some exercises will require students to write solutions which do not meet criteria for testing. In these cases it is necessary to wrap the student's solution in such a way that it does meet the testability criteria. That's where plugins come in.

A plugin is a function which creates another function (`wrapped_func`), which runs additional code before and after calling the original function (`func`). The test cases and tests can use of `wrapped_func` to test `func`.

There are built-in plugins and custom plugins can be defined and registered to the assignment.

Once registered, a plugin can be applied to an exercise by setting parameters in the `register_sampler` decorator.

## Example - solution

```python
@bp.register_solution('lin_printer_fac')
def lin_printer_fac(m, b):
    def f(x):
        y = m*x + b
        print(f'f({x}) = {m}({x}) + {b} = {y}')
        return y
    return f
```

This example solution isn't suitable for testing.

- The output is a function. While it's serializable, we can't directly compare functions in a test.
- The function which is returned prints to stdout. That isn't testable either.

In order to use this in an exercise, a plugin is needed for the testing.

## Example - plugin definition and registration

This plugin fits the need.

The approach is spelled out in the comments, but the idea is to call `lin_printer_fac(m, b)(x)` to get a numeric result. While this is going on stdout is redirected to capture the printed output.

It's registered to a blueprint (`bp`) using the `@bp.register_plugin()` decorator.

```python
@bp.register_plugin()
def print_handler(func, show_printed_output=False):
    def wrapped_func(m, b, x):
        # Temporarily capture `stdout` in buffer
        with io.StringIO() as buffer, redirect_stdout(buffer):
            # call `func(m, b)(x)` 
            # store both the buffer and returned value
            y = func(m, b)(x)
            printed_output = buffer.getvalue()
        # Print the captured output if enabled
        if show_printed_output:
            print(printed_output)
        # Return both the result and the printed output 
        return y, printed_output
    return wrapped_func
```

The plugin must take one positional argument (`func`).

The plugin can take additional _keyword_ arguments. In the example, `show_printed_output` is an additional parameter. These additional arguments allow customizing `wrapped_func`'s behavior without passing additional parameters to `wrapped_func`.

The `wrapped_func` which the plugin returns should take all arguments for `func`. It can take additional arguments. All arguments should be accepted as _keyword_ arguments. These extra test parameters should be used in cases where the solution result needs other context to be tested. 

## Example - demo

Using the wrapped version of a solution in demos gives students better intuition into how the solutions are being tested.

```python
@bp.register_demo('lin_printer_fac')
def lpf_demo():
    wp_lin_printer_fac = plugins.print_handler(lin_printer_fac,
                                               show_printed_output=True)
    ### three examples
    demo_result_lin_printer_fac = [
        wp_lin_printer_fac(m=3, b=3, x=1),
        wp_lin_printer_fac(m=4, b=-0.5, x=8),
        wp_lin_printer_fac(m=9, b=140, x=12)
    ]

    assert demo_result_lin_printer_fac == \
      demo_result_lin_printer_fac_TRUE, 'demo result incorrect' 

    return demo_result_lin_printer_fac
```

To use this plugin for the "print_update" exercise, the sampler would be registered like this:

```python
@bp.register_sampler('lin_printer_fac',
                     lin_printer_fac,
                     20,
                     ('y', 'printed_output'),
                     plugin='print_handler',
                     extra_param_names=['x'],
                     show_printed_output=False)
def print_update_sampler(rng):
    m, x, b = rng.uniform(-5, 5, 3).round(3)
    return {'m':m, 'x': x, 'b':b}
```

The name of the plugin being used is given as `plugin`.

The names of any arguments used by the plugin-wrapped solution but not the solution itself are given in the `list`, `extra_param_names`.
> All parameters (solution and "extra") must be returned by the sampler.

Any additional keyword arguments given to `register_sampler` are passed to the plugin.

The code above resolves the plugin-wrapped solution to the following

- function:
  ```python
  plugins.print_handler(lin_printer_fac,
                        show_printed_output=False)
  ```
- sample parameters:
  ```python
  m, b # from `lin_printer_fac`
  x    # from  `extra_param_names`
  ```
## Built-in plugins

Most common use-cases have a built-in plugin!

### `plugins.postprocess_sort(func, key=None)`
> The function `plugins.postprocess_sort(func, key)(**kwargs)` returns
>- `func(**kwargs)` sorted by `key`

### `plugins.error_handler(func)`
> The function `plugins.error_handler(func)(**kwargs)` returns
> - `bool`: indicating whether an error is raised
> - `any`: result of `func(**kwargs)`

### `sql_executor(query: str|callable)`
> The function `sql_executor(query)(conn, **kwargs)` returns 
> - the result of `pd.read_sql(query(**kwargs), conn)` _if query is **callable**_
> - the result of `pd.read_sql(query, conn)` _if query is a **string**_

### `sqlite_blocker(func)`
> The function `sqlite_blocker(func)(**kwargs)` returns
> - the result of `func(**kwargs)`
> - the function `sqlite3.connect` is disabled during execution of `func`

### `coo_plugin(func)`
> The funciton `coo_plugin(func)(**kwargs)` returns
> - a tuple containing the `shape`, `data`, `row`, and `col` attributes of `func(**kwargs)`