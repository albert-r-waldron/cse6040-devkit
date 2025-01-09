# Assignment project

The devkit uses code files to define an assignment and build it. The project setup is largely automated. Simply install the package and run this code.

```python
### asn_def.py

from cse6040_devkit.assignment import AssignmentBuilder

builder = AssignmentBuilder()
builder.build()
```

## Project structure

Running `asn_def.py` will initialize a project in the current directory.

These files will be generated with this structure. 

```bash
.
├── asn_def.py
├── assignment_config.yaml (link)
├── data/
├── keys.dill
├── main.ipynb
└── resource
    └── asnlib
        └── publicdata/
            ├── assignment_config.yaml
            ├── encrypted/
            └── execute_tests
```

## Discription

### `*.py` files

> **Purpose**: Assignment definition code.

There is flexibility to define the assignment attributes in one or many code files grouped by exercise, by attribute type, or any other logical way. It is even possible (not recommended) to use a Jupyter notebook.

### `assignment_config.yaml`

> **Purpose**: Assignment configuration file for assignment metadata and test details
>
> This is actually a link to `resource/asnlib/publicdata/assignment_config.yaml`.

This file will generate and be populated with default values derived from the code in many cases. This is detailed in the configuration documentation.

### `data/`
> **Purpose**: Static source data files.

A copy of each file in this directory will be made in `resource/asnlib/publicdata/` **unless a file of the same name already exists**.

This directory will be cretated if it does not exist.


### `keys.dill`

> **Purpose**: Persist RNG intialization and local encryption keys for repeatable builds.

A new file with random values will be created if one does not exist.

### `main.ipynb`
> **Purpose**: a Jupyter notebook assignment

In this context there are two types of cells

- **Auto-generated** - these are generated based on the definition code at every build. This overwrites any manual changes cell's source. However, the cells can be moved around with the new position sticking.
- **User-generated** - these cells are created by the user. They will remain in place and unmodified unless manually changed or moved.

Whenever a notebook is built a **new** notebook is created, replacing the **existing** notebook.

1. A stack of **auto-generated** cells is created from the definition code. Each cell is tagged.
2. Each cell in the **existing** notebook is examined
    - If the **existing** cell has a tag that's in the **auto-generated** stack, the same-tagged cell is removed from the **auto-generated** stack and appended to the **new** notebook.
    - Otherwise the **existing** cell is **user-generated** and is appended to the **new** notebook.
3. If there are any remaining **auto-generated** cells after the **existing** cells are exhausted, the remaining **auto-generated** cells are appended to the **new** notebook.
> To insert new **auto-generated** cells in a specific spot, a cell can be added to the notebook with the appropriate metadata tag. It will get picked up by this logic on the next build.

### `resource/asnlib/publicdata/`
> **Purpose**: contains all student-accessible data files for the assignment

#### Required files

These files are automatically generated if they do not exist.

- `execute_tests` - serialized wrapper for executing iterative tests in the Jupyter notebook.
- `assignment_config.yaml` - configuration file discussed above.
- `encrypted/` - contains hidden test case files

#### Dynamic files

- Copies of all files in the static source data directory.
- `tc_*` or `encrypted/tc_*` - serialized test cases.
- `*_TRUE` - correct demo result
- Other file names may be found for other functions or serialized objects.
