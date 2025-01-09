# Assignment notebook

The students interact with the assignment by editing a Jupyter notebook, executing its cells, and submitting it. The submitted notebooks are processed by an autograder, and the student is awarded points based on the results.

## Auto-generated cells

The devkit processes the definition code into notebook cells for different components of the assignment or its exercises. These cells are tagged for identification in the notebook.

## User-generated cells

Any cells which are not generated from the definition code are user-generated.

There's not much to say about user-generated cells, but they are very useful.

## Updating the notebook

The notebook update process can be thought of as stitching together the **existing** notebook with the collection of **auto-generated** cells.

1. Iterating over the **existing** cells in order
    - The **existing** cell is appended to the **new** notebook if it **does not share a tag** with an **auto-generated** cell
    - The **auto-generated** with the **same tag** is **dropped from the collection** and appended to the **new** notebook when a **tag is common** to both **existing and auto-generated** cells.
2. Any remaining **auto-generated** cells are appended to the **new** notebook
3. The **new** notebook overwrites the existing notebook file.

## Details

### Considerations

The update process maintains the order of the existing cells. If it seems like something is not being inserted properly, it may be at the bottom.

> When **renaming an exercise**, the cells tagged under the old `ex_name` will not remain in the notebook unless manually deleted.

### Auto-generated cell tags

#### main.header

> Contains markdown with header information including points total/cap, list of exercises/points, topics covered, etc.

#### main.global_imports

> Contains code to load the **global imports** defined in the config file

#### {ex_name}.preload_objects

> Contains code to load any **preload objects** registered to `ex_name`

#### {ex_name}.prompt

> Contains markdown with a prompt. The prompt will be populated with the docstring to the **solution** and **helper** registered to `ex_name`

#### {ex_name}.solution

> Contains code from **helper**, **solution** and **demo** functions registered to `ex_name`

#### {ex_name}.test_boilerplate

> Contains markdown with the docstring and expected output from the **demo** function registered to `ex_name`

#### {ex_name}.test

> Contains code to deserialize test cases and execute tests registered to `ex_name`