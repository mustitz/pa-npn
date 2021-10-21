# Generator of Boolean functions NPN-equivalence classes.

Here is a generator of NPN-equivalence classes. It would be useful for testing
some algorithms. It is written in Python. Number of NPN-equivalence classes
is a sequence [A000370](https://oeis.org/A000370) from OEIS.

## Usage

Before run the python requirement packages must be installed from the file
[requirements.txt](requirements.txt). To display usage information run
`python npn.py --help`.  Only a few words about `--with-set-bits` and
`--with-numpy-bits` are needed.  We need to check that a function has been
already processed. The python sets or bitmasks (from numpy) may be used for
this purpose. Numpy bitmasks are not fit in memory for argument count 6 and
more. So I introduced a python set method for partial NPN-classes generation
with a given amount of ones. Using python sets is slightly faster for
argument count from 0 to 4, but it does not matter, and using the python
sets is not enough to fully process 5 arguments.

TODO: we can use a combinatorial number system to enumerate all functions with
N ones. In this case we can use numpy bitmasks for all cases.

## Already generated NPN classes

Full NPN classes for argument count up to 5 inclusive were placed in [generated](generated)
directory.
