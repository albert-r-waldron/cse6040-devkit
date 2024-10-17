# %%
from work import builder
# %%
def get_tc_gen(builder, ex_name):
    try:
        return builder.core[ex_name]['test']['tc_gen']
    except:
        pass

def get_cases(builder, ex_name):
    from cse6040_devkit.test_case.test_case_gen import TestCaseGenerator
    base_dir = 'resource/asnlib/publicdata/'
    path = f'{base_dir}tc_{ex_name}'
    enc_path = f'{base_dir}encrypted/tc_{ex_name}'
    tc_gen = TestCaseGenerator()
    return {'visible': tc_gen.read_cases(path, builder.keys['visible_key']),
            'hidden': tc_gen.read_cases(enc_path, builder.keys['hidden_key'])}

get_cases(builder, 'compute_song_stats')

# %%
song_stat_gen = get_tc_gen(builder, 'compute_song_stats')


# %%
import pandas as pd
cols = ['bpm', 'danceability_%', 'streams']


def assert_col_strint(col):
    for s in col.values:
        assert isinstance(s, str)
        assert s == str(int(s))

def str_col_chars(col):
    from collections import Counter
    c = Counter()
    for s in col:
        c.update(s)
    return c

char_count_data = []
for _ in range (10000):
    case = song_stat_gen.make_case()
    spotify_metadata = case['spotify_metadata']
    df = pd.DataFrame(spotify_metadata)[cols]
    running_char_count = {}
    for col in cols:
        df_col = df[col]
        char_count = str_col_chars(df_col)
        assert_col_strint(df_col)
        running_char_count[f'{col}_char_count'] = char_count
    char_count_data.append(running_char_count)

# %%
master_summary = pd.DataFrame(char_count_data)
for col in master_summary.columns:
    print(f'{col} character NaN%')
    column_summary = pd.DataFrame(master_summary[col].tolist())
    display(column_summary.isna().sum() / column_summary.shape[0])


