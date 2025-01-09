# cse6040_devkit - Overview

## Purpose

This collection of tools exists to simplify and standardize the development of nbgrader assignments. Specifically, those hosted on the Vocareum platform for the Georgia Tech course CSE 6040.

## Components

### _assignment_
> Framework to register Python functions and objects as components within one or more _blueprints_ and _build_ the _blueprint_ into an Jupyter notebook assignment, complete with accompanying data files.

### _plugins_
> Function decorators used to wrap solutions for pre-processing the inputs and outputs prior to testing.

### _utils_
> Utility functions to simplify common operations.

### _test_case_
> Framework for creating, serializing, and storing test cases for exercises.

### _tester_fw_
> Framework for de-serializing test cases, testing student-written solutions, and providing actionable feedback.

### _sampler_testing_
> Utility for de-serializing test cases and performing quantitative and qualitative tests.