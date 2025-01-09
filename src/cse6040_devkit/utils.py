import dill
from collections import namedtuple

def load_object_from_publicdata(name):
    with open(f'resource/asnlib/publicdata/{name}', 'rb') as f:
        obj = dill.load(f)
    print(f'Successfully loaded {name}.')
    return obj

def dump_object_to_publicdata(obj, name):
    with open(f'resource/asnlib/publicdata/{name}', 'wb') as f:
        dill.dump(obj, f, recurse=True)

def add_from_file(name, m):
    print(m.__name__)
    path = f'resource/asnlib/publicdata/{name}'
    with open(path, 'rb') as f:
        func = dill.load(f)
    setattr(m, name, func)

def compare_test_cases(name, other_name, keys, 
                       return_obj=False, 
                       path='resource/asnlib/publicdata/',
                       other_path='resource/asnlib/publicdata/'):
    import dill as pickle
    from cryptography.fernet import Fernet
    from cse6040_devkit.tester_fw.test_utils import compare_copies
    def read_file(fn, key):
        fernet = Fernet(key)
        with open(fn, 'rb') as fin:
            obj = pickle.loads(fernet.decrypt(fin.read()))
        return obj
    enc_path = path + 'encrypted/'
    other_enc_path = other_path + 'encrypted/'
    obj = read_file(path + name, keys['visible_key'])
    old_obj = read_file(other_path + other_name, keys['visible_key'])
    visible_same = compare_copies(obj, old_obj)
    hobj = read_file(enc_path + name, keys['hidden_key'])
    hold_obj = read_file(other_enc_path + other_name, keys['hidden_key'])
    hidden_same = visible_same = compare_copies(hobj, hold_obj)
    if return_obj:
        return visible_same, hidden_same, obj, old_obj, hobj, hold_obj
    return visible_same, hidden_same

def is_hashable(variable):
    """
    Args:
        variable (Any): variable to check for hashability

    Returns:
        bool: True if the variable is hashable and False otherwise.
    """
    try:
        hash(variable)
        return True
    except TypeError:
        return False
    

class QueryString(str):
    def __new__(cls, query, ex_name=None):
        obj = super().__new__(cls, query)
        obj.__name__ = f'{ex_name}_query'
        argspec = namedtuple('ArgSpec', ['annotations', 'args'])
        obj.__argspec__ = argspec({'conn': "'db'"},['conn'])
        return obj
    
def capture_output(func, return_values_transformer=None):
    from contextlib import redirect_stdout
    import io
    with io.StringIO() as buffer, redirect_stdout(buffer):
        raw_return_values = func()
        captured_output = buffer.getvalue()
    displayable_return_values = ''
    if return_values_transformer:
        displayable_return_values = return_values_transformer(raw_return_values)
    return captured_output, raw_return_values, displayable_return_values

def extract_definition(source):
    source_defined = False
    source_lines = []
    for line in source.splitlines():
        if line.startswith('def'):
            source_defined = True
        if source_defined:
            source_lines.append(line)
    return '\n'.join(source_lines)

def replace_return(source, new_command=None):
    from textwrap import dedent
    import re
    # strip out top-level decorator and signature
    source = '\n'.join(extract_definition(source).splitlines()[1:])
    # dedent
    source = dedent(source)
    # replace last line with `new_command` only if it's a return
    source_lines = source.splitlines()
    if new_command is None:
        new_command = ''
    source_lines[-1] = re.sub(r'return .*',
                              dedent(new_command).strip(),
                              source_lines[-1])
    source = '\n'.join(source_lines)
    return source

def render_md_df_text_wrap(df):
    escaped_df = df.applymap(lambda s: s.replace('|', r'\|') if isinstance(s, str) else s)
    escaped_df.style.set_table_styles([{'selector': 'th', 'props': [('text-align', 'left')]}, 
                                       {'selector': 'td', 'props': [('word-wrap', 'break-word')]}])
    return escaped_df.to_markdown()

def display_df_text_wrap(df):
# This code displays your demo result
    styled_df = df.style.set_table_styles([{'selector': 'th', 'props': [('text-align', 'left')]}, 
                                       {'selector': 'td', 'props': [('word-wrap', 'break-word')]}])
    display(styled_df)