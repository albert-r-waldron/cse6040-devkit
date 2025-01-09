# Sampler testing

## CaseManager

The `CaseManager` exists to simplify operations with the test case files.

### Constructor params

#### `keys_path` (str, Default: `'keys.dill'`):

> Path to key file for assignment.

```python
from cse6040_devkit.sampler_testing import CaseManager

cm = CaseManager()
```

### Methods

#### `load_cases(ex_name: str)`

> Returns two lists of dictionaries, one for visible and one for hidden test cases of exercise `ex_name`.

```python
visible, hidden = cm.load_cases('some_exercise_name')
```

#### `load_cases_into_df(ex_name: str)`

> Returns a DataFrame containing both hidden and visible test cases.
>
> **Note:** some data values which can be found in test case files are not able to be crammed into a DataFrame.

```python
cases_df = cm.load_cases_into_df(ex_name)
```

#### `test_alternative_function(func: function, ex_name: str, n_iter=100, raise_errors=True)`

> Runs the visible and hidden test for `func` as the solution to `ex_name` for `n_iter` iterations. If `raise_errors` is enabled, execution errors are raised.

#### `map_param(cases: list[dict], param_name: str, *args, func=lambda x:x,**kwargs)`

> Returns a list containing the result of `func(case[param_name], *args, **kwargs)` for each `case` in `cases`

## Functions

Aside from the CaseManager, the functions are utilities to extract information about a single variable. These would then be used with `map_param` or `pd.Series.apply` to extract the information for all test cases.

### `assert_list_sortable(sortable_candidate: list, sort_key: function=lambda x: x)`

> Raises an `AssertionError` if `sort_key` is not sufficient to sort `sortable_candidate`

### `assert_frame_sortable(df: pd.DataFrame, by: list|None=None)`

> Raises an `AssertionError` if `df` is not sortable by the columns given in `by`. All columns are used if `by` is not given.

### `load_test_cases_from_file(ex_name, builder, keys)`

> Deprecated. Use a CaseManager to load test cases

### `map_param(cases, param_name, *args, func, **kwargs)`

> Returns a `generator` that iterates over `cases` and yeilding `func(cases[param_name], *args, **kwargs)` for each `case` in `cases`

### `dict_has_unhashable_values(d)`

> Returns `True` if `d` contains unhashable values

### `dict_has_duplicate_values(d, prefilter: function=lambda d: d)`

> Returns `True` if `prefilter(d)` contains any duplicate values.

### `distinct_type(col: iterable)`

> Returns a set containing distinct results of `type(x)` called on each `x` in `col`

### `assert_df_full(df)`

> Raises an `AssertionError` if `df` contains any missing values
