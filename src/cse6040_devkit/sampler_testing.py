import pandas as pd
import dill
from warnings import warn
from cse6040_devkit.tester_fw.testers import get_tester
from cse6040_devkit.assignment import execute_tests

def assert_list_sortable_by_key(sortable_candidate, sort_key=lambda x:x):
    """Assert that every `sort_key(item)` result is distinct for all `item` values in the list-like `sortable_candidate`. 

    If the assertion fails, the offending items and associated `sort_key(item)` results are shown
    
    Args:
        sortable_candidate (list-like): List to run the test on
        sort_key (function): Sort key 

    Raises:
        AssertionError: raised when the `sortable_candidate` is not deterministically sortable with the `sort_key`
    """
    from collections import defaultdict
    sort_key_mapping = defaultdict(list)
    for item in sortable_candidate:
        # print(item)
        new_sort_key_value = sort_key(item)
        sort_key_mapping[new_sort_key_value].append(item)
    # print(sort_key_mapping)
    duplicates = {k:v for k,v in sort_key_mapping.items() if len(v) > 1}
    if duplicates:
        err_str = '\n'+'\n'.join(f'key function returns {k} for these items: {v}' for k, v in duplicates.items())
        raise AssertionError(err_str)
    
def assert_frame_sortable(df:pd.DataFrame, by:list=None):
    """Assert there are no duplicate rows in `df[by]`

    If the assertion fails the offending rows are shown.

    Args:
        df (pd.DataFrame)
        by (list|None, optional): Columns to sort `df` by. Defaults to None, which sorts by all columns.

    Raises:
        AssertionError: if there are any duplicates.
    """
    if by is None:
        by = df.columns
    if isinstance(by, str):
        by = [by]
    dup_mask = df.duplicated(subset=by, keep=False)
    dups = df.loc[dup_mask, by]
    err_str = '\n'+'\n'.join(str(row) for row in dups.itertuples())
    if dup_mask.any():
        raise AssertionError(f"Duplicate rows found{err_str}")

def load_test_cases_from_file(ex_name, builder=None, keys=None):
    """Loads the test cases for exercise `ex_name` from its file

    Decryption keys are obtained from the `builder` or `keys` arguments. If both are provided, the `keys` parameter takes precidence.

    Args:
        ex_name (str): name of exercise
        builder (AssignmentBuilder, optional): AssignmentBuilder used to create the cases being loaded. Defaults to None.
        keys (dict, optional): Dictionary mapping `'visible_key'` and `'hidden_key'` to decryption keys. Defaults to None.

    Raises:
        ValueError: if neither `builder` or `keys` is given

    Returns:
        list[dict]: The visible cases
        list[dict]: The hidden cases
    """
    neither = (builder is None) and (keys is None)
    if builder and keys:
        warn("Both `builder` and `keys` params were passed. Decryption keys are taken from `keys` and the `builder` is ignored.")
    if neither:
        raise ValueError("At least one of `builder` or `keys` should be set.")
    if not keys:
        keys = builder.keys
    from cse6040_devkit.test_case.test_case_gen import TestCaseGenerator
    tc_reader = TestCaseGenerator()
    path = 'resource/asnlib/publicdata/'
    hidden_path = f'{path}/encrypted/'
    return tc_reader.read_cases(f'{path}{ex_name}', keys['visible_key']), \
           tc_reader.read_cases(f'{hidden_path}{ex_name}', keys['hidden_key'])

def map_param(cases, param_name, *args, func=lambda x:x, **kwargs):
    for case in cases:
        param = case[param_name]
        yield func(param, *args, **kwargs)

def dict_has_unhashable_values(d):
    all_hashable = True
    for v in d.values():
        if isinstance(v, (set, list, dict)):
            all_hashable = False
    return not all_hashable

def dict_has_duplicate_values(d, prefilter=lambda d: d):
    _d = prefilter(d)
    d_val_strs = {str(v) for v in _d.values()}
    return len(d_val_strs) != len(_d)

def distinct_type(col):
    return str({type(v) for v in col})

def assert_df_full(df):
    assert not df.isna().any(axis=None), \
        f"{df[df.isna().any(axis=1)]=}"

class CaseManager():
    def __init__(self,
                 keys_path='keys.dill'):
        with open(keys_path, 'rb') as f:
            self.keys = dill.load(f)

    def load_cases(self, ex_name):
        return load_test_cases_from_file(
            f'tc_{ex_name}',
            keys=self.keys
        )
    
    def load_cases_into_df(self, ex_name):
        visible, hidden = self.load_cases(ex_name)
        all_cases = [*visible, *hidden]
        return pd.DataFrame(all_cases)
    
    def test_alternate_function(self,
                                func,
                                ex_name,
                                n_iter=100,
                                raise_errors=True):
        visible_result = execute_tests(func,
                                       ex_name,
                                       key=self.keys['visible_key'],
                                       n_iter=n_iter)
        hidden_result = execute_tests(func,
                                       ex_name,
                                       key=self.keys['hidden_key'],
                                       n_iter=n_iter,
                                       hidden=True)
        if raise_errors:
            v_passed, _, v_e = visible_result
            h_passed, _, h_e = hidden_result
            if v_e: 
                print('visible test raised error')
                raise v_e
            assert v_passed, 'visible test did not pass'
            print('visible tests pass')
            if h_e: 
                print('hidden test raised error')
                raise h_e
            assert h_passed, 'hidden_test did not pass'
            print('hidden tests pass')

        return visible_result, hidden_result
    
    def map_param(self,
                  cases, param_name, *args,
                  func=lambda x: x,
                  **kwargs):
        return list(map_param(cases, param_name,
                              *args, func=func,
                              **kwargs))
            