from typing import List
from itertools import permutations, product
import sys


class BitArray:
    """
    A class to represent a fixed length array of bits.
    """

    value: int = 0
    line: str = ''
    table: List[int] = []

    def _set(self, value, line, table):
        self.value = value
        self.line = line
        self.table = table

    def _init_from_int(self, value, size):
        line = f"{value:b}".zfill(size)
        assert len(line) == size

        table = [ int(ch) for ch in line ]
        table.reverse()

        self._set(value, line, table)

    def _init_from_list(self, table):
        line = ''.join(map(str, reversed(table)))
        value = eval('0b' + line) # pylint: disable=eval-used
        self._set(value, line, table)

    def __init__(self, *args):
        if len(args) == 1:
            self._init_from_list(*args)
        else:
            self._init_from_int(*args)

    def __getitem__(self, index):
        return self.table[index]

    def __str__(self):
        return self.line


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


def get_npn_class(qargs, qvalues, func, transforms):
    """
    Form NPN class with a given function.
    """
    npn_class = []
    for perm, inverses in transforms:
        cofunc1, cofunc2 = 0, 0
        for iarg in range(qvalues):
            arg = BitArray(iarg, qargs)
            coarg = 0
            for i, j in enumerate(perm):
                if arg[i] ^ inverses[i]:
                    coarg |= 1 << j
            if func[arg.value]:
                cofunc1 |= 1 << coarg
            else:
                cofunc2 |= 1 << coarg

        npn_class.append(cofunc1)
        npn_class.append(cofunc2)

    return set(npn_class)


def robust_build_npn_classes(qargs):
    """
    Build all NPN classes in a robust way for a given argument count.
    """
    transforms = build_npn_transforms(qargs)
    qvalues = 2 ** qargs
    qfunctions = 2 ** qvalues

    npn_classes = dict()
    for ifunc in range(qfunctions):
        func = BitArray(ifunc, qvalues)
        npn_class = get_npn_class(qargs, qvalues, func, transforms)
        min_ifunc = min(npn_class)
        assert min_ifunc <= ifunc
        if min_ifunc == ifunc:
            npn_classes[ifunc] = npn_class
            npn_class_len, num = len(npn_class), len(npn_classes)
            print(f"{num:3d} {func} {npn_class_len:3d}", flush=True)
        else:
            assert npn_classes[min_ifunc] == npn_class

    total = sum(len(npn_class) for npn_class in npn_classes.values())
    assert total == qfunctions


def build_npn_classes(qargs, qones_range=None):
    """
    Build all NPN classes in an optimal way for a given argument count.
    """
    transforms = build_npn_transforms(qargs)
    qvalues = 2 ** qargs

    if isinstance(qones_range, int):
        qones_list = [int(qones_range)]
    elif qones_range is None:
        qones_list = list(range(qvalues//2 + 1))
    else:
        qones_list = list(qones_range)

    num = 0
    for qones in qones_list:
        ifunc = 2 ** qones - 1
        ifunc_last = 2 ** (qvalues-1)
        processed = set()
        while ifunc < ifunc_last:
            if ifunc not in processed:
                func = BitArray(ifunc, qvalues)
                npn_class = get_npn_class(qargs, qvalues, func, transforms)
                npn_class_len = len(npn_class)
                processed.update(npn_class)
                num += 1
                print(f"{num:6d} {func} {npn_class_len:4d}", flush=True)
                if ifunc == 0:
                    break
            ifunc = ncm(ifunc)


def main():
    """
    An entry point.
    """
    for qargs in sys.argv[1:]:
        build_npn_classes(int(qargs))


if __name__ == '__main__':
    main()
