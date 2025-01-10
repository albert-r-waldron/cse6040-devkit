# Utils

Utility functions are available in the assignment Jupyter notebook as well as the definition code. They exist to simplify trivial and non-trivial tasks and avoid re-inventing the wheel.

## Classes

### QueryString(str)

Extends str by providing additional attributes which makes it parsable as the `sol_func` argument to `@bp.register_sampler`.

#### Constructor params
- `query` - a SQL query
- `ex_name` - an exercise name

Creates `str` equivalent to `query` with  
- `__name__` attribute: `'{ex_name}_query'`
- `__argspec__.annotations` attribute: `{'conn':'db'}`
- `__argspec__.args` attribute: `['conn']`

## Functions

### `dump_object_to_publicdata(obj, name)`

> Serializes `obj` into a file called `name`.

### `load_object_from_publicdata(name)`

> Deserializes the file called `name` into a Python object.

### `add_from_file(name, m):`

> Deserializes the file called `name` into a Python object. 
>
> The object is set as an attribute of module `m` called `name`.

### `is_hashable(variable)`

> `True` if the variable is hashable, `False` otherwise.

### `capture_output(func, return_values_transformer=None)`

> Executes `func`, passing no arguments.
>
> Returns
>
> - Anything `func` printed to stdout
> - The raw result of `func()`
> - The value of the `return_values_transformer` applied to the raw result or `''` if `None` is provided.

### `extract_definition(source)`

> Extracts the top level function definition from a code snippet

### `replace_return(source, new_command=None)`

> Extracts the function body from `source`
>
> Removes one indentation level
>
> Replaces the `return` line with `''` or `new_command`

### `render_md_df_text_wrap(df)`

> Creates markdown text for a table with text-wrapped cells from `df`

### `display_df_text_wrap(df)`

> Displays `df` in a Jupyter notebook with text-wrapped cells