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
        cofunc1 = [None] * qvalues
        cofunc2 = [None] * qvalues
        for iarg in range(qvalues):
            arg = BitArray(iarg, qargs)
            coarg = [None] * qargs
            for i, j in enumerate(perm):
                coarg[j] = arg[i] ^ inverses[i]
            coarg = BitArray(coarg)
            cofunc1[coarg.value] = func[arg.value]
            cofunc2[coarg.value] = 1 ^ func[arg.value]

        npn_class.append(BitArray(cofunc1))
        npn_class.append(BitArray(cofunc2))

    return set(func.value for func in npn_class)


def build_npn_classes(qargs):
    """
    Build all NPN classes for a given argument count.
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


def main():
    """
    An entry point.
    """
    for qargs in sys.argv[1:]:
        build_npn_classes(int(qargs))


if __name__ == '__main__':
    main()
