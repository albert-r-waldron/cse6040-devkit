from cse6040_devkit.assignment import AssignmentBlueprint
from cse6040_devkit import plugins
from solutions import *
import logging
from pprint import pprint
import random
from sqlite3 import connect

logger = logging.getLogger(__name__)
logging.basicConfig(filemode='w',
                    filename='build_log.txt', 
                    level=logging.INFO)

demo_bp = AssignmentBlueprint()


@demo_bp.register_demo('inverted_dictionary')
def inverted_demo():
    """There are 4 possible combinations of having duplicates and being hashable. This means that there are possible states for the data and four possible states for the parameters. We have created a test grid with simple examples of all combinations.  
    """
    # We use an error handler to catch errors raised by your solution
    # 
    wrapped = plugins.error_handler(invert_dict)
    hashable_no_dups = {1:2, 3:4, 5:6}
    unhashable_no_dups = {1:[3,4,5], 2:3, 4:5, 7:[3,4,5]}
    unhashable_with_dups = {1:[3,4,5], 2:3, 4:5}
    hashable_with_dups = {1:2, 3:4, 5:2}
    test_grid = [[True, True], [True, False], [False, True], [False, False]]

    for tgi in test_grid:
        print('tgi = ', dict(zip(['allow_dup_vals', 'allow_unhashable_vals'], tgi)))
        print(f"hashable_no_dups result: {wrapped(hashable_no_dups, *tgi)}")
        print(f"unhashable_no_dups result: {wrapped(unhashable_no_dups, *tgi)}")
        print(f"unhashable_with_dups result: {wrapped(unhashable_with_dups, *tgi)}")
        print(f"hashable_with_dups result: {wrapped(hashable_with_dups, *tgi)}")
        print()

@demo_bp.register_demo('count_articles', return_values_transformer=lambda s:str(s), return_replacement='pprint(demo_result_count_articles)')
def count_articles_demo():
    demo_running_count = Counter({'georgia': 3, 'tech': 5, 'jacket': 15})
    demo_article_words = {'ga', 'tech', 'yellow', 'jacket'}
    demo_result_count_articles = count_articles(demo_running_count, demo_article_words)
    return demo_result_count_articles

article_records = [v for v in pd.read_csv('data/Articles.csv', encoding='Windows-1252').to_dict(orient='index').values()]

@demo_bp.register_demo('extract_article_words')
def extract_article_words_demo():
    demo_record = {'Article': 'This is a "news article". \n\tNum-bers, punctuati0n, and under_scores aren\'t letters, so they cannot be part of a word!',
        'Date': '2/9/2015',
        'Heading': 'hsbc admits swiss bank failings over client tax',
        'NewsType': 'business'}
    demo_result_extract_article_words = extract_article_words(demo_record)
    print(demo_result_extract_article_words)
    return demo_result_extract_article_words

@demo_bp.register_demo('record_examiner')
def record_examiner_demo():
    def insert_in_sorted_list(L, item):
        '''Inserts an item into L such that L remains sorted
        '''
        import bisect
        bisect.insort(L, item)
        return L
    
    demo_input_vars = {
        'some_iter': ['This', 'is', 'An', 'ExAmpL3'],
        'map_func': lambda s: s.lower(),
        'red_func': insert_in_sorted_list,
        'initial': [] 
    }
    demo_original_input_vars = {
        'some_iter': ['This', 'is', 'An', 'ExAmpL3']        
    }
    demo_result_record_examiner = record_examiner(**demo_input_vars)
    print(demo_result_record_examiner)
    return demo_result_record_examiner


@demo_bp.register_demo('concatenate_quotes', return_values_transformer=utils.render_md_df_text_wrap, 
                       return_replacement='utils.display_df_text_wrap(demo_result_concatenate_quotes)')
def concatenate_quotes_demo():
    with connect('resource/asnlib/publicdata/star_wars.db') as demo_conn:
        demo_result_concatenate_quotes = plugins.sql_executor(concatenate_quotes_query)(demo_conn)
    return demo_result_concatenate_quotes

@demo_bp.register_demo('conn_to_df', 
                       return_values_transformer=utils.render_md_df_text_wrap,
                       return_replacement='utils.display_df_text_wrap(demo_result_conn_to_df)')
def conn_to_df_demo():
    with connect('resource/asnlib/publicdata/star_wars.db') as demo_conn:
        demo_result_conn_to_df = concatenate_quotes_conn_to_df(demo_conn)
    return demo_result_conn_to_df

@demo_bp.register_demo('species_count',
                       return_values_transformer=utils.render_md_df_text_wrap,
                       return_replacement='utils.display_df_text_wrap(demo_result_species_count)')
def species_count_demo():
    demo_result_species_count = species_count(char_df, spec_df)
    return demo_result_species_count

@demo_bp.register_demo('count_values')
def count_values_demo():
    demo_s = pd.Series([1,2,3,3,2,2,2,1,1,1,2,3,1,2,3,1,2,3])
    demo_result_count_values = count_values(demo_s)
    print(demo_result_count_values)
    return demo_result_count_values

@demo_bp.register_demo('mat_vec_div')
def mat_vec_div_demo():
    demo_A = np.array([[1,2], [7,4]])
    demo_x = np.array([1,2])

    demo_result_mat_vec_div = mat_vec_div(demo_A, demo_x)
    print(demo_result_mat_vec_div)
    return demo_result_mat_vec_div

@demo_bp.register_demo('df_to_coo')
def df_to_coo_demo():
    demo_shape = (33, 45)
    demo_df = pd.DataFrame({'data': [2,3,4],
                            'row': [2, 20, 10],
                            'col': [4, 1, 30]})
    demo_result_df_to_coo = df_to_coo(demo_df, demo_shape)
    print(demo_result_df_to_coo)
    print(f'{demo_result_df_to_coo.shape=}')
    print(f'{demo_result_df_to_coo.data=}')
    print(f'{demo_result_df_to_coo.row=}')
    print(f'{demo_result_df_to_coo.col=}')
    return demo_result_df_to_coo