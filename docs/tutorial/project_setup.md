# Project setup

- Create a directory for the project
- Initialize a git repository in the new directory (This is technically optional, but you want to do this)
- Create an empty python script. In this example it's named `assignment_definition.py` but the name doesn't matter. And... that's it!

We will add code to this file and run it to build out the rest of the project.  

```python
from cse6040_devkit.assignment import AssignmentBuilder

builder = AssignmentBuilder()

builder.build()
```

We have created an AssignmentBuilder object and executed its build method. This creates/updates the necessary project file structure.

```bash
.
├── assignment_definition.py
├── keys.dill
├── main.ipynb
└── resource
    └── asnlib
        └── publicdata
            ├── assignment_config.yaml
            └── encrypted

4 directories, 4 files
```

- `main.ipynb`: Jupyter notebook to be deployed on Vocareum.  
  - There's not much in this file now. Just a template generated header and a code cell importing some libraries.
- `resource/asnlib/publicdata`: data directory accessible to students.  
  - All data files required for `main.ipynb` should be stored here.
- `keys.dill`: stored for consistent encryption.  
- `assignment_config.yaml`: Configuration file used to generate `main.ipynb`.  