# Assignment Configuration

Assignment configuration is based on a yaml file organized in a heirarchy. Details are read from the configuration file when the assignment's Jupyter notebook is built _and_ as part of its execution.

## Build configuration

When the notebook is built, the configuration file is merged with the definition code to create a build configuration which is aligned to the definition code. The build configuration is saved back to the configuration file after the build.

### Merge details

This logic will determine which values are used in the build logic in this order:

- Assignment level keys
- Exercises
- Exercise test inputs and outputs

||Key IN file|Key NOT IN file|  
|---|---|---|  
|Key Registered|Value from file|Default value|  
|Key NOT Registered|Key not used|Key not used|  

## Assignment Level

The assignment level configuration is the top in the hierarchy. All other levels are descendents of the assignment level. It contains metadata about the overall assignment.

### Assignment Level Metadata

Details related to the assignment title, topics, scoring, and dependencies.

> Aside from dependencies, these are cosmetic only.

#### Keys (assignment level metadata)
 
- assignment_name (string - `"assignment name"`): Name of the assignment
- subtitle (string - `"assignment subtitle"`): Subtitle of the assignment
  > The title will render as "{assignment_name}: {subtitle}"
- version (string - `"0.0.1"`): Track post-release versions
- topics (string - `"this, that, and the other"`): Topics covered by the assignment
  > The template will render like `"This assignment covers {topics}."`
  > - Setting values in style of `"pandas, numpy, and regular expressions"` will render into a nice-looking sentence.
- points_cap(string - "points cap")
- total_points(string - "total points")
  > The `points_cap` and `total_points` only affect the **appearance** of the assignment.
  >
  > The text about the points cap will render like `"There are {total_points} points available. However only {points_cap} points are required for 100%"`
- global_imports(list[mapping] - `null`): list of dependency modules to import
  > - module (string)
  > - submodule (string)
  > - alias (string)
  >
  > The `main.global_imports` cell will contain one line for each mapping under `global_imports` depending on which keys are provided in the mapping. These are the options.
  > > - `import {module}`
  > > - `import {module} as {alias}`
  > > - `from {module} import {submodule}`
  > > - `from {module} import {submodule} as {alias}`
- exercises(mapping - empty mapping): Maps exercise names to the exercise level configuration details.

## Exercise level

Under the assignment level key `exercises`, each exercise name is mapped to its exercise level of configuration.

### Keys (exercise level)

- num (number - sequence registered in definition)
  > This affects the **appearance** only. Cells in the Jupyter notebook associated with the exercise will have **text** reflecting `num`
  >
  > **Note:** this will not update automatically in the configuration file if the ordering is changed in definitiion code files or the Jupyter notebook.
- points (number - 1): Number of points the exercise is worth for grading
- n_visible_trials (number - 100): Number of visible trials run in the exercise test
- n_hidden_trials (number - 1): Number of hidden trials run in the exercise test
- config (mapping): Test configuration for the exercise

## Exercise test configuration level

These details determine the test behavior for the exercise.

### Keys

- case_file (string - `'tc_{ex_name}'`): file name containing test cases
- inputs (mapping): Maps input names to details on how to process them in the test.
  > - dtype (string - `''|'db'|{type hint}`): data type of the input.
  > - check_modified (boolean - `true` unless `dtype` is `'db'`): whether to check input for being modified as side effect in the test.
- outputs (mapping): Maps output names to details on how to process them in the test.
  > - index (number - order of registration): Index of test output to assign this name. (ties resolve to the order appearing in this list)
  > - dtype (str - '')
  > - check_dtype (boolean - True): When set to True, check that the returned object type matches the given `dtype` value. Test will also pass if `''` is given for `dtype`.
  > - float_tolerance (number - 1.0e-06 ): Absolute tolerance for floating point comparisons.
  > - check_col_dtypes: true
  > - check_col_order: true
  > - check_row_order: false
  > - check_column_type: true