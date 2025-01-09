from cse6040_devkit.assignment import AssignmentBlueprint
from solutions import *
import numpy as np
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filemode='w',
                    filename='build_log.txt', 
                    level=logging.INFO)

sampler_bp = AssignmentBlueprint()

@sampler_bp.register_sampler('inverted_dictionary',
                            invert_dict,
                            500,
                            ('error_raised', 'inverted_dictionary_output'),
                            plugin='error_handler')
def invert_dict_sampler(rng):
    nums = np.arange(50)
    rng.shuffle(nums)
    add_dups = rng.random() < 0.5
    add_unhash = rng.random() < 0.4
    d = dict(zip(rng.choice(nums, 30, replace=False),
                 rng.choice(nums, 30, replace=add_dups)))
    if add_unhash:
        for k in d:
            unhash_type_rv = rng.random()
            if unhash_type_rv < 0.2:
                d[k] = [d[k]]
            elif unhash_type_rv < 0.4:
                d[k] = set((d[k],))
            elif unhash_type_rv < 0.6:
                d[k] = {'value': d[k]}
            elif unhash_type_rv < 0.62:
                d[k] = {'value': True}
    return {
        'd': d,
        'allow_dup_vals': rng.choice([True, False]),
        'allow_unhashable_vals': rng.choice([True, False])
    }

@sampler_bp.register_sampler('concatenate_quotes',
                          concatenate_quotes_query,
                          10,
                          'result',
                          'sql_executor',
                          extra_param_names=['conn'])
def cq_sampler(rng=None):
    import sqlite3
    import pandas as pd
    from numpy.random import default_rng
    if rng is None:
        print("Alert: No rng provided")
        rng = default_rng()
    with sqlite3.connect('resource/asnlib/publicdata/star_wars.db') as conn:
        quotes_df = pd.read_sql('select * from quotes', conn)
    m = quotes_df.shape[0]
    _m = rng.integers(m-5, m)
    distinct_names = quotes_df['character_name'].unique()
    quotes_df['character_name'] = rng.choice(distinct_names, size=m, replace=True)
    quotes_df = quotes_df.sample(_m, random_state=rng.integers(2**32-1), replace=False)
    return ({'conn': {'quotes': quotes_df}}, 'conn')

def insert_random_underscore(s, rng:np.random.Generator):
    return ''.join(c if rng.random() > 0.002 else '_' for c in s)

article_texts = pd.read_csv('resource/asnlib/publicdata/Articles.csv', encoding='Windows-1252')['Article']
all_article_words = {word for article in article_texts for word in ''.join(c if c.isalpha() else ' ' for c in article.lower()).split()}

@sampler_bp.register_sampler(
    ex_name='extract_article_words',
    n_cases=20,
    sol_func=extract_article_words,
    output_names='result'
)
def extract_article_words_sampler(rng: np.random.Generator):
    num_char = rng.integers(100, 300)
    article = insert_random_underscore(' '.join(a[:num_char] for a in article_texts.sample(3).values), rng)
    return {'record': {'Article': article}}

@sampler_bp.register_sampler('count_articles', count_articles, 20, 'result')
def count_articles_sampler(rng: np.random.Generator):
    core_words = rng.choice(list(all_article_words), size=10, replace=False)
    running_count = Counter({word: rng.integers(1, 30) for word in core_words if rng.random() < 0.8})
    article_words = set(rng.choice(core_words, rng.integers(3,7)))
    if rng.random() < 0.20:
        article_words = set()
    return {'running_count': running_count,
            'article_words': article_words}

def linear_map_factory(m, b):
    def _map(x):
        return m*x + b
    _map.__name__ = f'y = {m}x + {b}'
    return _map

@sampler_bp.register_sampler('record_examiner',
                             record_examiner,
                             20,
                             'result')
def record_examiner_sampler(rng: np.random.Generator):
    def red_fun_add(val, itm):
        return val + itm
    red_fun_add.__name__ = 'val + itm'
    def red_fun_mul(val, itm):
        return val - itm
    red_fun_mul.__name__ = 'val * itm'
    def cast_to_float(*t):
        if rng.random() < 0.10:
            return tuple(float(ti) for ti in t)
        return t

    red_fun = rng.choice([red_fun_add, red_fun_mul])
    ms = [3, -2]
    bs = [5, 12]
    mbs = [cast_to_float(m, b) for m in ms for b in bs]
    m, b = rng.choice(mbs)
    _sample = {'some_iter': list(rng.integers(-10, 10, 15)),
               'red_func': red_fun,
               'map_func': linear_map_factory(m, b),
               'initial': None}
    if rng.random() < 0.20: 
        _sample['initial'] = rng.integers(-5, 5)
    return _sample
    
sampler_bp.register_sampler('conn_to_df',
                          concatenate_quotes_conn_to_df,
                          10,
                          'result')(cq_sampler)

@sampler_bp.register_sampler('species_count',
                             species_count,
                             20,
                             'result')
def species_count_sampler(rng: np.random.Generator):
    species = char_df['species'].unique()
    classifications = spec_df['classification'].unique()
    characters = char_df['name'].unique()

    rng = np.random.default_rng()
    _characters = rng.choice(characters, 25, replace=False)
    _char_df = pd.DataFrame(
        {
            'name': rng.choice(characters, len(_characters), replace=False),
            'species': rng.choice(species, len(_characters), replace=True)
        }
    )
    _spec_df = pd.DataFrame(
        {
            'name': species,
            'classification': rng.choice(classifications, len(species))
        }
    )
    return {'char_df': _char_df,
            'spec_df': _spec_df}

@sampler_bp.register_sampler('count_values',
                             count_values,
                             40,
                             'result')
def count_values_sampler(rng: np.random.Generator):
    core_words = ['one', 'fish', 'two', 'blue',
                  'marvin', 'k', 'mooney', 
                  'grinch',
                  'cat', 'in', 'the', 'hat']
    word_sample = rng.choice(core_words, 7, replace=False)
    weighted = [word for word in word_sample for _ in range(rng.integers(2,7))]
    rng.shuffle(weighted)
    return {'s': pd.Series(weighted)}

@sampler_bp.register_sampler('mat_vec_div',
                             mat_vec_div,
                             20,
                             'result')
def mat_vec_div_sampler(rng: np.random.Generator):
    m, n = rng.integers(3, 10, 2)
    return {
        'A': rng.uniform(-10, 10, (m,n)).round(3),
        'x': rng.uniform(-2, 2, n).round(3)
    }

@sampler_bp.register_sampler('df_to_coo',
                             df_to_coo,
                             15,
                             ('shape', 'data', 'row', 'col'),
                             plugin='coo_plugin')
def df_to_coo_sampler(rng: np.random.Generator):
    m, n = rng.integers(12, 22, 2)
    nnz = rng.integers(10, 15)
    shape = (m, n)
    row = rng.integers(0, m-1, nnz)
    col = rng.integers(0, n-1, nnz)
    data = rng.normal(3, 2, nnz).round(3)
    df = pd.DataFrame({
        'row': row,
        'col': col,
        'data': data
    })
    return {'df': df, 'shape': shape}