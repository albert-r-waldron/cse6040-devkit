# %% [markdown]
# # Configure Exam Settings

# %%
from cse6040_devkit.assignment import AssignmentBlueprint, AssignmentBuilder

# %%
bp = AssignmentBlueprint()
builder = AssignmentBuilder()

# %%
from IPython.display import display, Markdown, Latex
from pprint import pprint, pformat

# %% [markdown]
# # Spotify and Lyrics Dataset

# %%
# %load_ext autoreload
# %autoreload 2

import dill
import re
from pprint import pprint
from cse6040_devkit import plugins

# %%
with open('resource/asnlib/publicdata/spotify_metadata.dill', 'rb') as fp:
    spotify_metadata = dill.load(fp)

print(f"=== Success: Loaded {len(spotify_metadata):,} Spotify song metadata records. ===")
print(f"\nExample: Records 0 and 7:\n")
pprint([spotify_metadata[k] for k in [0, 7]])

# %%
with open('resource/asnlib/publicdata/lyrics.dill', 'rb') as fp:
    raw_lyrics = dill.load(fp)

print(f"=== Success: Loaded song lyrics from {len(raw_lyrics):,} artists. ===")
print(f"=== Success: Loaded {len([song for song_dict in raw_lyrics.values() for song in song_dict]):,} song lyrics total. ===")
print(f"\nExample: Harry Styles - 'As It Was' First 12 Lines:\n")
pprint({'Harry Styles': {'As It Was': raw_lyrics['Harry Styles']['As It Was'][:12]}})

# %% [markdown]
# # Ex. 0 (1 pt): ```spotify_metadata__FREE```

# %%
@bp.register_plugin()
def postprocess_sort_dict(func):
    """Plugin to sort dictionary's list values before comparing to the expected result. This has the effect of allowing students to return a dictionary of lists in any order and still pass the test cell.

    Args:
        func (function): An exercise solution function. This function should output a dictionary of lists.
    
    Returns (function): 
        - same inputs as `func`
        - returns the sorted output of `func` 
    """
    def _func(*_args, **_kwargs):
        result = func(*_args, **_kwargs)
        try:
            result = {k:sorted(v) for (k,v) in result.items()}
        except Exception as e:
            print(f'''There was a problem sorting your result. This likely indicates an implementation issue as the expected result is sortable.''')
            print(e)
        return result
    return _func

@bp.register_plugin()
def rhyming_part(phones):
    phones_list = phones.split()
    for i in range(len(phones_list) - 1, 0, -1):
        if phones_list[i][-1] in '12':
            return ' '.join(phones_list[i:])
    return phones

@bp.register_plugin()
def rhymes(word, lookup, rhyme_lookup):
    from itertools import chain
    phones = lookup.get(word.lower(), [])
    combined_rhymes = []
    if phones:
        for element in phones:
            combined_rhymes.append([w for w in rhyme_lookup.get(rhyming_part(element), []) if w != word])
        combined_rhymes = list(chain.from_iterable(combined_rhymes))
        unique_combined_rhymes = sorted(set(combined_rhymes))
        return unique_combined_rhymes
    else:
        return []

# @bp.register_solution('spotify_metadata__FREE')
def spotify_metadata__FREE():
    """**This is a free exercise!** 

The first dataset we will be working with is the metadata of the most streamed songs on Spotify in 2023:  ```spotify_metadata``` is a list of dictionaries, where each dictionary contains the information for a single song. 

Each dictionary contains the following keys, and all values are of the data type **string**:
- 'acousticness_%'
- 'artist_count'
- 'artist_name'
- 'bpm'
- 'danceability_%'
- 'energy_%'
- 'instrumentalness_%'
- 'key'
- 'liveness_%'
- 'mode'
- 'released_year'
- 'speechiness_%'
- 'streams'
- 'track_name'
- 'valence_%'

**Please run the test cell below to collect your FREE point**
    """
    return 'passed!'

# %% [markdown]
# # Ex. 1 (1 pt): ```compute_song_stats```

# %%
@bp.register_solution('compute_song_stats')
def compute_song_stats(spotify_metadata: list) -> tuple:
    """
**Your task:** Define `compute_song_stats` as follows:  Compute the average BPM, danceability, and number of streams for the Spotify Top Songs of 2023.

**Input:** `spotify_metadata`: A list of dictionaries, as described in Exercise 0.

**Return:** A tuple containing the following in order:  (```average_bpm```, ```average_danceability```, ```average_streams```)

**Requirements:**
- Compute the average ```bpm```, average ```danceability```, average ```streams``` for all songs in ```spotify_metadata```
- Round each average to the nearest integer
- Format average ```streams``` to be a string with commas as the thousands separator. For example, the integer 1000 should be represented as '1,000'

**Hint:** This example https://stackoverflow.com/questions/1823058/how-to-print-a-number-using-commas-as-thousands-separators may help with the formatting requirement 
    """
    ### BEGIN SOLUTION    
    bpm = []
    dance = [] 
    streams = []
    
    for song in spotify_metadata:
        bpm.append(int(song['bpm']))
        dance.append(int(song['danceability_%']))
        streams.append(int(song['streams']))
    
    def mean(x):
        return sum(x)/len(x)
        
    def format_streams(x):
        return '{:,}'.format(round(x))
    
    return round(mean(bpm)), round(mean(dance)), format_streams(mean(streams))
    ### END SOLUTION


# %%
song_stats_demo_input = spotify_metadata[:3]
print(f"""
**Example.** A correct implementation should produce, for the demo, the following output:
```python
{pformat(compute_song_stats(song_stats_demo_input))}
```
""")

# %%
@bp.register_demo('compute_song_stats')
def compute_song_stats_demo():
    """**Example**. A correct implementation should produce, for the demo, the following output:
```python
(118, 67, '138,367,321')
```
"""
    song_stats_demo_input = spotify_metadata[:3]
    print(compute_song_stats(song_stats_demo_input))


# %%
@bp.register_sampler('compute_song_stats', compute_song_stats, 200, ('average_bpm','average_danceability','average_streams'))
def song_stats_sampler():
    from  random import sample, randint
    mini_list = sample(spotify_metadata, randint(4, 20)) 
    return {'spotify_metadata':mini_list}



# %% [markdown]
# # Ex. 2 (2 pts): ```find_songs_by_artist```

# %%
@bp.register_solution('find_songs_by_artist')
def find_songs_by_artist(spotify_metadata: list) -> dict:
    """
**Your task:** Define `find_songs_by_artist` as follows:  Reorganize Spotify metadata into a dictionary of lists of tuples, containing the song information for each artist.

**Input:** `spotify_metadata`: A list of dictionaries, as described in Exercise 0.

**Return:** `songs_by_artist`: A dictionary of lists of tuples, where the artist is the key, and the value is a list of tuples of the form: (```track_name```, ```streams```)

**Requirements:** 
- Split the ```artist_name``` field as needed to handle multiple artists. Multiple artists are separated by commas
- Trim off any whitespace from the ```artist_name``` strings
- Convert ```streams``` to an integer, and sort the list of tuples for each artist by the number of streams in descending order

**Note:**  If the same artist is listed multiple times for the same song, that song should appear the same number of times in that artist's list.
    """
    ### BEGIN SOLUTION
    from collections import defaultdict
    songs_by_artist_dict = defaultdict(list)
    
    for i in spotify_metadata:
        for j in i['artist_name'].split(","):
            tup = (i['track_name'], int(i['streams']))
            songs_by_artist_dict[j.strip()].append(tup)
            
    for (artist, tracks) in songs_by_artist_dict.items():
        songs_by_artist_dict[artist] = sorted(tracks, key =lambda x: -x[1])
    return dict(songs_by_artist_dict)
    ### END SOLUTION
    

# %%
songs_by_artist_demo_input = [spotify_metadata[k] for k in [0, 41]]
print(f"""
**Example.** A correct implementation should produce, for the demo, the following output:
```python
{pformat(find_songs_by_artist(song_stats_demo_input))}
```
""")

# %%
@bp.register_demo('find_songs_by_artist')
def find_songs_by_artist_demo():
    """**Example**. A correct implementation should produce, for the demo, the following output:
```python
{'BTS': [('Left and Right', 720434240)],
 'Charlie Puth': [('Left and Right', 720434240)],
 'Jung Kook': [('Left and Right', 720434240), ('Seven', 141381703)],
 'Latto': [('Seven', 141381703)]}
```
"""
    songs_by_artist_demo_input = [spotify_metadata[k] for k in [0, 41]]
    pprint(find_songs_by_artist(songs_by_artist_demo_input))


# %%
@bp.register_sampler('find_songs_by_artist', find_songs_by_artist, 200, ('songs_by_artist',))
def song_stats_sampler():
    from  random import sample, randint
    mini_list = sample(spotify_metadata, randint(4, 18)) 
    return {'spotify_metadata':mini_list}

# %% [markdown]
# # Ex. 3 (1 pt): ```discover_top_artists```

# %%
# Change to regular dictionary (instead of default) for readability?

with open('resource/asnlib/publicdata/top_songs.dill', 'rb') as fp:
    songs_by_artist = dill.load(fp)

print(f"=== Success: Loaded stats from {len(songs_by_artist):,} artists. ===")

# %%
@bp.register_solution('discover_top_artists')
def discover_top_artists(songs_by_artist: dict, X: int) -> list:
    """
**Your task:** Define `discover_top_artists` as follows:  Given the result of Exercise 2, return a list of the top X artists with the most songs in the Spotify metadata.

**Input:** 
- `songs_by_artist`: A dictionary of lists of tuples, where the artist is the key, and the value is a list of tuples of the form: (```track_name```, ```streams```)
- `X`: An integer representing the maximum number of tuples to return.

**Return:** `top_artists`: A list of X tuples of the form: (artist name, number of songs, number of total streams)

**Requirements:**
- Count the number of songs for each artist
- Sum the total number of streams for each artist
- Create list of tuples where each tuple corresponds to one artist: (artist name, number of songs, number of total streams)
- Sort this list in descending order by song count. If the song counts are the same, sort by total streams in descending order
- Return at most X tuples 
    """
    ### BEGIN SOLUTION
    counts = []
    for (artist, tracks) in songs_by_artist.items():
        total_streams = sum([i[1] for i in tracks])
        counts.append((artist, len(tracks), total_streams))
    full_sorted = sorted(counts, key =lambda x: (-x[1], -x[2]))
    truncated = full_sorted[:X]
    
    return truncated
    ### END SOLUTION


# %%
top_artists_demo_input = {k: songs_by_artist[k] for k in ['Latto', 'Jung Kook', 'Myke Towers']}
print(f"""
**Example.** A correct implementation should produce, for the demo, the following output:
```python
{pformat(discover_top_artists(top_artists_demo_input, 2))}
```
""")

# %%
@bp.register_demo('discover_top_artists')
def discover_top_artists_demo():
    """**Example**. A correct implementation should produce, for the demo, the following output:
```python
[('Jung Kook', 5, 1469963422), ('Latto', 1, 141381703)]
```
"""
    top_artists_demo_input = {k: songs_by_artist[k] for k in ['Latto', 'Jung Kook', 'Myke Towers']}
    print(discover_top_artists(top_artists_demo_input, 2))
    

# %%
@bp.register_sampler('discover_top_artists', discover_top_artists, 200, ('top_artists',))
def song_stats_sampler():
    from  random import sample, randint
    sample_keys = sample(list(songs_by_artist.keys()), randint(3, 12)) 
    sample_dic = {i:songs_by_artist[i] for i in sample_keys}
    return {'songs_by_artist':sample_dic,
            'X':randint(1,10)}

# %% [markdown]
# # Ex. 4 (3 pts): ```cleanse_lyrics```

# %%
@bp.register_solution('cleanse_lyrics')
def cleanse_lyrics(lyrics_list: list) -> list:
    """
**Your task:** Define `cleanse_lyrics` as follows:  Given a list of lyrics for a single song, cleanse the text of each line, and return the cleansed list.

**Input:** `lyrics_list`: A list of lyrics for one song, where each element of the list corresponds to one line of lyrics in that song.

**Return:** `cleansed_lyrics_list`: A list of song lyrics, where the raw text is cleansed as outlined in the rules below.

**Recommended Steps:**
1. Combine the lyrics into one string, separated by newline characters **"\n"**
2. Make all characters lowercase
3. Replace any hyphens **"-"** with a single space **" "**
4. Remove any **non-alphabetic** characters, with the exception of any whitespace characters, single quote characters **"'"**, and parentheses **"()"**
5. Remove background vocals (any words inside of parentheses and the parentheses themselves). You may assume that any open parenthesis will eventually be followed by a closed parenthesis, though a backup vocal may span multiple lines. You may also assume there will be no nested parentheses.
6. Split combined string with newline characters **"\n"** as the delimiter
7. Trim off any whitespace characters from the beginning and end of each line
8. Remove any empty lines


    """
    ### BEGIN SOLUTION
    import re
    cleansed_list = []

    lyrics = ('\n').join(lyrics_list).lower()
    
    lyrics_no_hyphens = re.sub(r'\-',' ', lyrics)
    pattern = re.compile(r'([a-zA-Z\'\s\)\(]*)')
    matches_list = pattern.findall(lyrics_no_hyphens)
    ##rejoin
    new_line = ''.join(matches_list)

    new_line = re.sub(r'\([a-zA-Z\'\s]*\)','', new_line)
    
    for i in new_line.split('\n'):
        if i.strip() != '':
            cleansed_list.append(i.strip())
            
    return cleansed_list
    ### END SOLUTION



# %%
cleanse_lyrics_demo_input = raw_lyrics['Doja Cat']['Say So'][-27:-19] + raw_lyrics['Doja Cat']['Say So'][-7:]
print(cleanse_lyrics_demo_input)
print(f"""
**Example.** A correct implementation should produce, for the demo, the following output:
```python
{pformat(cleanse_lyrics(cleanse_lyrics_demo_input))}
```
""")

# %%
@bp.register_demo('cleanse_lyrics')
def cleanse_lyrics_demo():
    """**Example.** A correct implementation should produce, for the demo, the following output:
```python
['tell me what must i do',
 "'cause luckily i'm good at reading",
 "i wouldn't tell him but he won't stop cheesin'",
 'and we can dance all day around it',
 "if you frontin' i'll be bouncing",
 'if you know it scream it shout it babe',
 'before i leave you dry',
 "didn't like to know it keep with me in the moment",
 "i'd say it had i known it why don't you say so",
 "didn't even notice no punches left to roll with",
 'you got to keep me focused you know it say so',
 'you might also like',
 'ooh ah ha ah ah ha ah ha ah ha',
 'ooh ah ha ah ah ha ah ha ah ha']
```
    """
    cleanse_lyrics_demo_input = raw_lyrics['Doja Cat']['Say So'][-27:-19] + raw_lyrics['Doja Cat']['Say So'][-7:]
    pprint(cleanse_lyrics(cleanse_lyrics_demo_input))


# %%
@bp.register_sampler('cleanse_lyrics', cleanse_lyrics, 150, ('cleansed_lyrics_list',))
def cleanse_lyrics_sampler():
    # Reduced to 150 test cases and reduced size of sample
    from random import sample
    sample_key = sample(list(raw_lyrics.keys()), 1)[0] 

    sample_song = sample(list(raw_lyrics[sample_key].keys()), 1)[0]
    return {'lyrics_list':raw_lyrics[sample_key][sample_song]}

# %% [markdown]
# # Ex. 5 (2 pts): ```vibe_check```

# %%
with open('resource/asnlib/publicdata/all_cleansed_lyrics.dill', 'rb') as fp:
    all_cleansed_lyrics = dill.load(fp)

print(f"=== Success: Loaded cleansed lyrics from {len(all_cleansed_lyrics):,} artists. ===")

# %%
# Stop Words Package:
# from stop_words import get_stop_words
# stop_words = get_stop_words('en')

# %%
with open('resource/asnlib/publicdata/stopwords.dill', 'rb') as fp:
    STOP_WORDS = dill.load(fp)

print(f"=== Success: Loaded {len(STOP_WORDS):,} stop words. ===")

# %%
@bp.register_solution('vibe_check')
def vibe_check(cleansed_lyrics_list: list, X: int) -> set:
    """
**Your task:** Define `vibe_check` as follows: Given a list of cleansed lyrics, identify which words appear most frequently in a song, so that we can determine the "vibe" of the song.

To do this effectively, we should first remove any stop words from the lyrics before counting the occurrences of each word. Stop words are a set of words that are so commonly used in the English language that they carry little useful information to our analysis.

**Input:**
- `cleansed_lyrics_list`: A list of cleansed lyrics from a single song.
- `X`: An integer representing the maximum number of words to return.

**Return:** `top_vibes`: A set of up to the top X most common words found in the lyrics.

**Requirements:**
- Remove stopwords using the global variable `STOP_WORDS`
- Count occurrences of each word
- Return a set containing at most X common words. If the counts of two words are the same, sort by length of the word in descending order. If two words share the same count and length, then sort by the order words are encountered in the input.

**Hint:**
Remember that sets in Python are unordered. Your result must contain the same words as the expected result, but the order may differ!
    """
    ### BEGIN SOLUTION
    from collections import Counter
    
    ## Combine all lines
    full_lyrics  = ' '.join(cleansed_lyrics_list)
    
    words_list = full_lyrics.split()
            
    ## Remove stopwords
    words_list_no_stopwords = [i for i in words_list if i not in STOP_WORDS]
    
    ## Create counter and store
    counts_dict = Counter(words_list_no_stopwords)

    ## Sort items in Counter dictionary by count descending, then by length of the word itself in descending order
    sorted_tuple_list = sorted(counts_dict.items(), key = lambda x: (-x[1], -len(x[0])))

    ## Grab 0th element of tuple for first X tuples, convert to set and return
    return set([word[0] for word in sorted_tuple_list[:X]])
    ### END SOLUTION
   

# %%
vibe_check_demo_input = all_cleansed_lyrics['Taylor Swift']['Cruel Summer']

print(f"""
**Example.** A correct implementation should produce, for the demo, the following output:
```python
{pformat(vibe_check(vibe_check_demo_input, 3))}
```
""")

# %%
@bp.register_demo('vibe_check')
def vibe_check_demo():
    """**Example.** A correct implementation should produce, for the demo, the following output:
```python
{'oh', 'summer', 'cruel'}
```
"""
    vibe_check_demo_input = all_cleansed_lyrics['Taylor Swift']['Cruel Summer']
    print(vibe_check(vibe_check_demo_input, 3))


# %%
@bp.register_sampler('vibe_check', vibe_check, 200, ('top_vibes',))
def vibe_check_sampler():
    from  random import sample, randint
    one_artist = sample(all_cleansed_lyrics.keys(), 1)
    one_song_name = sample(all_cleansed_lyrics[one_artist[0]].keys(), 1)
    one_song_lyrics = all_cleansed_lyrics[one_artist[0]][one_song_name[0]]
    return {'cleansed_lyrics_list':one_song_lyrics,
           'X':randint(1,10)}


# %% [markdown]
# # Ex. 6 (2 pts): ```generate_bigrams```

# %%
@bp.register_solution('generate_bigrams')
def generate_bigrams(cleansed_lyrics_list: list) -> dict:
    """
**Your task:** Define `generate_bigrams` as follows: Given a list of the cleansed lyrics, find the count of all word bigrams.

What is a bigram? A bigram is a pair of consecutive written units. In our exercise, we want to find the counts of pairs of consecutive **words** in **each line of lyrics**.

**Input:**
`cleansed_lyrics_list`: A list of cleansed lyrics from a single song.

**Return:**
`bigrams_dict`: A dictionary in which the key is a tuple (first_word, second_word), and the value is the count of the number of times that bigram appears in the lyrics.

**Requirements:**
- For each line of lyrics, find the count of all word bigrams
- Generate a dictionary where the key is a tuple of the bigram, and its value is the count of the number of times that bigram appeared in the lyrics

**Example:**
For the line 'you might also like', the bigrams would be ('you', 'might'), ('might', 'also'), and ('also', 'like').
    """
    ### BEGIN SOLUTION
    from collections import Counter

    # Create empty counter dict to hold running total bigram count
    total_bigrams_count = Counter()
    
    # Iterate over each line in lyrics list
    for line in cleansed_lyrics_list:
        # Split string of words into list using default whitespace delimiter
        list_of_words_in_line = line.split()
        # Zip together the list of words with the next words. Count and add to total Counter
        total_bigrams_count += Counter(zip(list_of_words_in_line,list_of_words_in_line[1:]))
        
    return dict(total_bigrams_count)
    ### END SOLUTION


# %%
bigrams_demo_input = all_cleansed_lyrics['Doja Cat']['Say So'][-3:]

print(f"""
**Example.** A correct implementation should produce, for the demo, the following output:
```python
{pformat(generate_bigrams(bigrams_demo_input))}
```
""")

# %%
@bp.register_demo('generate_bigrams')
def generate_bigrams_demo():
    """**Example.** A correct implementation should produce, for the demo, the following output:
```python
{('ah', 'ah'): 2,
 ('ah', 'ha'): 8,
 ('also', 'like'): 1,
 ('ha', 'ah'): 6,
 ('might', 'also'): 1,
 ('ooh', 'ah'): 2,
 ('you', 'might'): 1}
```
"""
    bigrams_demo_input = all_cleansed_lyrics['Doja Cat']['Say So'][-3:]
    pprint(generate_bigrams(bigrams_demo_input))
    

# %%
@bp.register_sampler('generate_bigrams', generate_bigrams, 200, ('bigrams_dict',))
def generate_bigrams_sampler():
    from  random import sample, randint
    one_artist = sample(all_cleansed_lyrics.keys(), 1)
    one_song_name = sample(all_cleansed_lyrics[one_artist[0]].keys(), 1)
    one_song_lyrics = all_cleansed_lyrics[one_artist[0]][one_song_name[0]]
    return {'cleansed_lyrics_list':one_song_lyrics}

# %% [markdown]
# # Ex. 7 (2 pts): ```rhyme_time```

# %%
from itertools import chain
with open('resource/asnlib/publicdata/rhyming_dict.dill', 'rb') as fp:
    rhyme_lookup = dill.load(fp)
with open('resource/asnlib/publicdata/lookup.dill', 'rb') as fp:
    lookup = dill.load(fp)

# %%
@bp.register_solution('rhyme_time')
def rhyme_time(cleansed_lyrics_list: list) -> dict:
    """
**Your task:** Define `rhyme_time` as follows:  Given a list of cleansed lyrics, generate a rhyming dictionary using the last word in each line of lyrics.

**Input:**
`cleansed_lyrics_list`: A list of cleansed lyrics from a single song.

**Return:**
`rhyming_dict`: A dictionary in which the key is the last word of a lyric line, and its value is a set of all of the last words found in `cleansed_lyrics_list` that rhyme with the key. 

**Requirements:**
- Check if any of the last words in the list of lyrics rhyme with each other. Use only the provided helper function `rhyme_checker` to determine if two words rhyme.
- If any words rhyme, add the rhyming words to the dictionary symmetrically for each word. For example, in the demo below, note that both `'are': {'car'}` and `'car': {'are'}` appear.
    """
    ### BEGIN SOLUTION
    from collections import defaultdict
    
    rhyming_dict = defaultdict(set)
    last_words = []
    for line in cleansed_lyrics_list: 
        ## extract last word in every line
        last_words.append(line.split()[-1])
    for i in last_words:
        for j in last_words:
            if rhyme_checker(i,j):
                rhyming_dict[i].add(j) 
                rhyming_dict[j].add(i) 
  
    return dict(rhyming_dict)
    ### END SOLUTION


# %%
@bp.register_helper('rhyme_time')
def rhyme_checker(word1, word2):
    return word1 in plugins.rhymes(word2, lookup, rhyme_lookup)

# %%
rhyming_demo_input = all_cleansed_lyrics['Taylor Swift']['Cruel Summer']

print(f"""
**Example.** A correct implementation should produce, for the demo, the following output:
```python
{pformat(rhyme_time(rhyming_demo_input))}
```
""")

# %%
@bp.register_demo('rhyme_time')
def rhyme_time_demo():
    """**Example.** A correct implementation should produce, for the demo, the following output:
```python
{'are': {'car'},
 'below': {'oh'},
 'car': {'are'},
 'fate': {'gate'},
 'gate': {'fate'},
 'lying': {'trying'},
 'oh': {'below'},
 'true': {'you'},
 'trying': {'lying'},
 'you': {'true'}}
```
"""
    rhyming_demo_input = all_cleansed_lyrics['Taylor Swift']['Cruel Summer']
    pprint(rhyme_time(rhyming_demo_input))

# %%
@bp.register_sampler('rhyme_time', rhyme_time, 200, ('rhyming_dict',))
def rhyme_time_sampler():
    from  random import sample, randint
    one_artist = sample(all_cleansed_lyrics.keys(), 1)
    one_song_name = sample(all_cleansed_lyrics[one_artist[0]].keys(), 1)
    one_song_lyrics = all_cleansed_lyrics[one_artist[0]][one_song_name[0]]
    return {'cleansed_lyrics_list':one_song_lyrics}

# %% [markdown]
# # Ex. 8 (3 pts): ```count_syllables```

# %%
@bp.register_solution('count_syllables')
def count_syllables(set_of_words: set) -> dict:
    """
**Your task:** Define `count_syllables` as follows:  Given a set of words, find the number of syllables in each word.

**Input:**
`set_of_words`: A set of words, such as {'are', 'car', 'trying'}

**Return:**
`syllable_dict`: A dictionary in which the keys are the words found in `set_of_words`, and the value is the number of syllables in that word.

**Requirements:**
To determine the number of syllables in a word:
1. If the first letter of the word is a letter within `vowels_no_y`, add 1
2. If there is a letter within `consonants` followed immediately by a letter within `vowels`, add 1 for each occurrence
3. If there are **3 or more** of any of the letters within `vowels` consecutively, add 1 for each occurrence. For instance, 'uoyy' would be considered a valid match
4. Now check to see if the word ends with an `'e'`. If so, subtract 1, unless the word ends with `'le'` and the preceding letter is a letter within `consonants`, then do nothing
5. Every word should have at least 1 syllable. If it has 0 syllables, add a syllable

Create a dictionary containing the word as a key and the number of syllables in that word as its value.

**Hint:** While not required, [Regular Expressions](https://www.w3schools.com/python/python_regex.asp) might be helpful to use for Steps 1-4! 

**Examples:** 
- The word 'quiet' contains 2 syllables, as 'qu' adds 1 syllable in Step 2, and 'uie' adds 1 syllable in Step 3. 
- The word 'the' contains 1 syllable, as 'he' adds 1 syllable in Step 2.
- The word 'you' contains 1 syllable, as 'you' adds 1 syllable in Step 3.
- The word 'trouble' contains 2 syllables, as 'ro' adds 1 syllable in Step 2, 'le' adds 1 syllable in Step 2, and because it ends in 'le' and 'b' is a consonant we do not subtract 1.
- The word 'stale' contains 1 syllable, as 'ta' adds 1 syllable in Step 2, 'le' adds 1 syllable in Step 2, but you subtract 1 syllable in Step 4 because the word ends in 'le' and is not preceded by a consonant.
- The word 'irritate' contains 3 syllables, as 'i' adds 1 syllable in Step 1, 'ri' adds 1 syllable in Step 2, 'ta' adds 1 syllable in Step 2, 'te' adds 1 syllable in Step 2, and 'e' subtracts 1 syllable from our count in Step 4.
    """
    vowels_no_y = 'aeiou'
    vowels = 'aeiouy'
    consonants = 'bcdfghjklmnpqrstvwxz'
    
    ### BEGIN SOLUTION
    syllable_dict = {}

    # Iterate over words in set_of_words
    for word in set_of_words:
        
        # Initialize syllable count for each word to be 0
        word_syllable_count = 0
            
        # Step 1: Check if first letter is vowel_no_y, if so, increase word_syllable_count by 1
        starting_vowel = re.findall('^[aeiou]', word)
        word_syllable_count += len(starting_vowel)

        # Step 2: Check if consonant followed by vowel, if so, increase word_syllable_count by 1 for each occurrence
        vowel_after_consonant = re.findall('[bcdfghjklmnpqrstvwxz][aeiouy]', word)
        word_syllable_count += len(vowel_after_consonant)

        # Step 3: Check if there are 3 or more vowels in a row, if so, increase word_syllable_count by 1 for each occurrence
        three_vowels = re.findall('[aeiouy]{3,}', word)
        word_syllable_count += len(three_vowels)

        # Step 4: If last letter in word is an e, decrease syllable count by 1, unless ends in consonant + le
        ending_le = re.findall('[bcdfghjklmnpqrstvwxz]le$', word)
        if len(ending_le) == 0 and word[-1] == 'e':
            word_syllable_count -= 1
                
        # Step 5: Syllable count for a word must be at least 1
        if word_syllable_count <= 0: 
            word_syllable_count = 1

        syllable_dict[word] = word_syllable_count 
                
    return syllable_dict
    ### END SOLUTION


# %%
syllables_demo_input = set(all_cleansed_lyrics['Taylor Swift']['Cruel Summer'][22].split())
#print(syllables_demo_input)

syllables_demo_input2 = {'queue', 'luckily', 'quiet', 'the', 'you', 'a', 'trouble', 'irritate', 'stale'}

print(f"""
**Example.** A correct implementation should produce, for the demo, the following output:
```python
{pformat(count_syllables(syllables_demo_input2))}
```
""")

# %%
@bp.register_demo('count_syllables')
def count_syllables_demo():
    """**Example.** A correct implementation should produce, for the demo, the following output:
```python
{'a': 1,
 'irritate': 3,
 'luckily': 3,
 'queue': 1,
 'quiet': 2,
 'stale': 1,
 'the': 1,
 'trouble': 2,
 'you': 1}
```
"""
    syllables_demo_input = {'queue', 'luckily', 'quiet', 'the', 'a', 'you', 'trouble', 'irritate', 'stale'}
    pprint(count_syllables(syllables_demo_input))

# %%
# Get a big list of words to sample from (containing no apostrophes):
# from  random import sample, randint
# one_artist = sample(all_cleansed_lyrics.keys(), 1)
# one_song_name = sample(all_cleansed_lyrics[one_artist[0]].keys(), 1)
# one_song_lyrics = all_cleansed_lyrics[one_artist[0]][one_song_name[0]]
# one_lyrics_combined = ' '.join(one_song_lyrics)
# word_list = one_lyrics_combined.split()
# all_words_set = set([x.strip() for x in word_list if "'" not in x])
# word_set = sample(all_words_set, randint(5, min(15,len(all_words_set))))
# print(word_set)
            

# %%
@bp.register_sampler('count_syllables', count_syllables, 200, ('syllable_dict',))
def count_syllables_sampler():
    from  random import sample, randint
    one_artist = sample(all_cleansed_lyrics.keys(), 1)
    one_song_name = sample(all_cleansed_lyrics[one_artist[0]].keys(), 1)
    one_song_lyrics = all_cleansed_lyrics[one_artist[0]][one_song_name[0]]
    one_lyrics_combined = ' '.join(one_song_lyrics)
    word_list = one_lyrics_combined.split()
    all_words_set = {x.strip() for x in word_list if "'" not in x}
    word_set = sample(all_words_set, randint(5, min(15,len(all_words_set))))
    return {'set_of_words':word_set}

# %% [markdown]
# # Ex. 9 (1 pt): ```build_markov_process```

# %%
# from collections import Counter
# all_bigrams_counter = Counter()

# for artist, song_dict in all_cleansed_lyrics.items():
#     for song_title, list_of_lyrics in song_dict.items():
#         all_bigrams_counter += generate_bigrams(list_of_lyrics)
# all_bigrams = dict(all_bigrams_counter)

# %%
with open('resource/asnlib/publicdata/all_bigrams.dill', 'rb') as fp:
    bigrams_dict = dill.load(fp)

print(f"=== Success: Loaded {len(bigrams_dict):,} bigrams. ===")

# %%
@bp.register_solution('build_markov_process')
def build_markov_process(bigrams_dict: dict) -> dict:
    """
**Your task:** Define `build_markov_process` as follows:  Using the result from Exercise 6, generate a Markov process so our lyric generator can select the next word in a lyric with probabilities matching those found in our lyric dataset.

**Input:**
`bigrams_dict`: A dictionary containing bigram keys that are tuples (first_word, second_word), with values that are the count of the number of times that bigram appears in the lyrics.

**Return:**
`markov_dict`: A dictionary of lists, in which the key is the first word, and the value is a list containing all potential second words.

**Requirements:**
- Create `markov_dict` in which the keys are the first words from `bigrams_dict`, and the values are a list of the second words in that bigram duplicated the number of times specified by the count for that bigram

**Example:**
For input `{('first', 'second'): 2, ('first', 'other'): 1}`, your result would be: `{'first': ['second', 'second', 'other']}`
    """
    ### BEGIN SOLUTION
    from collections import defaultdict

    final_dict = defaultdict(list)
    
    for bigram_tuple, count in bigrams_dict.items():
        initial_word = bigram_tuple[0]
        next_word = bigram_tuple[1]
        next_word_count_list = [next_word] * count
        final_dict[initial_word].extend(next_word_count_list)
    return dict(final_dict)
    ### END SOLUTION
    

# %%
markov_demo_input = {k: bigrams_dict[k] for k in [('like', 'ah'), ('like', 'what'), ('ah', 'he'), ('he', 'got')]}

print(f"""
**Example.** A correct implementation should produce, for the demo, the following output:
```python
{pformat(build_markov_process(markov_demo_input))}
```
""")

# %%
@bp.register_demo('build_markov_process')
def build_markov_process_demo():
    """**Example.** A correct implementation should produce, for the demo, the following output:
```python
{'ah': ['he'], 'he': ['got', 'got', 'got'], 'like': ['ah', 'ah', 'ah', 'ah', 'what', 'what', 'what', 'what']}
```
"""
    markov_demo_input = {k: bigrams_dict[k] for k in [('like', 'ah'), ('like', 'what'), ('ah', 'he'), ('he', 'got')]}
    pprint(build_markov_process(markov_demo_input))

# %%
@bp.register_sampler('build_markov_process', build_markov_process, 200, ('markov_dict',), plugin='postprocess_sort_dict')
def build_markov_process_sampler():
    from  random import sample, randint
    sample_keys = sample(list(bigrams_dict.keys()), randint(2, 100)) 
    sample_dic = {i:bigrams_dict[i] for i in sample_keys}
    return {'bigrams_dict':sample_dic}

# %%
builder.register_blueprint(bp)

# %%
if __name__ == '__main__':
    builder.build()

# %%



