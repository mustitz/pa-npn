from itertools import permutations, product
from argparse import ArgumentParser
import sys
import numpy as np


def ncm(x): # pylint: disable=invalid-name
    """
    Generate the next combination mask (NCM) for an integer.
    This is Gosper's hack to get the next integer with the same ones count.
    """
    a = x & -x
    b = x + a
    c = b ^ x
    c >>= 1 + a.bit_length()
    return b | c


class BitsInNumpy: # pylint: disable=too-few-public-methods
    """
    A numpy array for an int set implementation based on bitmasks.
    """
    def __init__(self, sz, dtype=np.uint64):
        self.dtype = dtype
        self.elem_bits = 8 * np.dtype(dtype).itemsize
        data_len = sz // self.elem_bits + (sz % self.elem_bits != 0)
        self.data = np.zeros(data_len, dtype=self.dtype)

    def append(self, value):
        """
        Append a number to the bit set. Returns true if the number is already in the set.
        """
        index = value // self.elem_bits
        offset = value % self.elem_bits
        mask = self.dtype(1 << offset)
        result = (self.data[index] & mask) == 0
        if result:
            self.data[index] |= mask
        return result


def build_npn_transforms(qargs):
    """
    Generate all argument symmetries for a given count.
    """
    transforms = []
    args = list(range(qargs))
    for perm in permutations(args):
        for inverses in product({0, 1}, repeat=qargs):
            transforms.append((perm, inverses))
    return transforms


def get_npn_class(qvalues, func, transforms, bits):
    """
    Form NPN class with a given function.
    """
    npn_class_len = 0
    for perm, inverses in transforms:
        cofunc1, cofunc2 = 0, 0
        for arg in range(qvalues):
            coarg = 0
            for i, j in enumerate(perm):
                arg_ith = 1 if arg & (1 << i) else 0
                if arg_ith ^ inverses[i]:
                    coarg |= 1 << j
            if func & (1 << arg):
                cofunc1 |= 1 << coarg
            else:
                cofunc2 |= 1 << coarg

        npn_class_len += bits.append(cofunc1)
        npn_class_len += bits.append(cofunc2)

    return npn_class_len


def build_npn_classes(qargs, qones_range=None, **kwargs):
    """
    Build all NPN classes in an optimal way for a given argument count.
    """
    transforms = build_npn_transforms(qargs)
    qvalues = 2 ** qargs
    qfunctions = 2 ** qvalues

    if isinstance(qones_range, int):
        qones_list = [int(qones_range)]
    elif qones_range is None:
        qones_list = list(range(qvalues//2 + 1))
    else:
        qones_list = list(qones_range)

    num = 0
    bits = BitsInNumpy(qfunctions)
    for qones in qones_list:
        func = 2 ** qones - 1
        func_last = 2 ** (qvalues-1)
        while func < func_last:
            if bits.append(func):
                npn_class_len = 1 + get_npn_class(qvalues, func, transforms, bits)
                num += 1
                func_str = f"{func:b}".zfill(qvalues)
                print(f"{num:6d} {func_str} {npn_class_len:4d}", flush=True, **kwargs)
                if func == 0:
                    break
            func = ncm(func)


def make_todo(arg): # pylint: disable=too-many-return-statements
    """
    Parse command line argument and returns it in a parsed form.
    The string is returned if error.
    """
    if arg.isdigit():
        return int(arg), None
    if ':' not in arg:
        return f"Invalid argument count number “{arg}”."
    qargs, bits = arg.split(':', maxsplit=1)
    if not qargs.isdigit():
        return f"Invalid argument count number “{qargs}”."

    qones_range = []
    for item in bits.split(','):
        if item.isdigit():
            qones_range.append(int(item))
            continue
        if '-' not in item:
            return f"Invalid range “{item}”."
        start, end = item.split('-', maxsplit=1)
        if not start.isdigit():
            return f"Invalid start range “{start}”."
        if not end.isdigit():
            return f"Invalid end range “{end}”."
        qones_range += list(range(int(start), int(end)+1))

    return int(qargs), sorted(set(qones_range))


def main():
    """
    An entry point.
    """

    cmdline_arguments = {
        'args': {
            'nargs': '+',
            'metavar': 'arg',
            'help': 'Argument counts for boolean functions with optional one bits. ' +
                    'Examples: 5 or 5:3 or 5:3-6 or 5:3,6 or 5:3,6-8.'
        },
        ('--output', '-o'): {
            'nargs': 1,
            'help': 'Set output file',
        },
    }

    parser = ArgumentParser(description='Generate NPN classes of boolean functions.')
    for args, kwargs in cmdline_arguments.items():
        if isinstance(args, str):
            args = (args,)
        parser.add_argument(*args, **kwargs)
    args = parser.parse_args()

    todo = [ make_todo(arg) for arg in args.args ]
    errors = [ msg for msg in todo if isinstance(msg, str) ]
    if errors:
        print('Some error(s) in argument counts has been found:', file=sys.stderr)
        for msg in errors:
            print(' ', msg, file=sys.stderr)
        parser.print_usage()
        sys.exit(1)

    kwargs = dict()
    try:
        if args.output:
            fn = args.output[0]
            kwargs['file'] = open(fn, 'w') # pylint: disable=consider-using-with

        for qargs, qones_range in todo:
            build_npn_classes(qargs, qones_range, **kwargs)

    finally:
        outf = kwargs.get('file')
        if outf is not None:
            outf.close()


if __name__ == '__main__':
    main()
