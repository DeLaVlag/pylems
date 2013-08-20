# PyLEMS - A [LEMS](http://neuroml.org/lems/)/[NeuroML2](http://neuroml.org/neuroml2.php) simulator written in Python

##
*Note: PyLEMS is currently in the process of major refactoring.*

## Installation
Check the code out of github.

    % git@github.com:LEMS/pylems.git

This will create a directory named pylems. Add this directory to your PATH and PYTHONPATH variables.

## Usage
pylems [\<options\>] \<LEMS/NeuroML file\>

### Options
- -I/-include \<path\> - Adds a directory to the model file include search path
- -XI/-xsl-include \<path\> - Adds a directory to the XSL preprocessor include path

## Tasks
- Implement flattening
- Decouple events from runnables
- Perform dimension-checking on expressions.
- Simple LEMS API for creating, reading and writing LEMS model files.
- Implement LEMS API over lems.model.* (NeuroML API?)
  - Interface with libNeuroML and Pyramidal to export Neuron MOD files
  - Export C files (Interface? Steve Marsh’s project?)
- Assertions.
- XPath implementation.
- Implement Runnables from Component types instead of expanded typeless Components (Required for efficient C/C++ code generation)



## Examples

### NeuroML examples
- Example 0 -- Working
- Example 1 -- Not working (Working on this)
- Example 2 -- Not tested
- Example 3 -- Not tested
- Example 4 -- Not tested
- Example 5 -- Not tested
- Example 6 -- Not tested
- Example 7 -- Not tested
- Example 8 -- Not tested
- Example 9 -- Not tested
- Example 10 -- Not tested
- Example 11 -- Not tested
- Example 12 -- Not tested
- Example 13 -- Not tested
- Example 14 -- Not tested
- Example 15 -- Not tested
      
## LEMS elements that do not work
- XPath based parameters - DerivedParameter, PathParameter
- Assertions
