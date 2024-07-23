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