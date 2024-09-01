import dill
def load_object_from_publicdata(name):
    with open(f'resource/asnlib/publicdata/{name}', 'rb') as f:
        obj = dill.load(f)
    print(f'Successfully loaded {name}.')
    return obj

def dump_object_to_publicdata(obj, name):
    with open(f'resource/asnlib/publicdata/{name}', 'wb') as f:
        dill.dump(obj, f)

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