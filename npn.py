from itertools import permutations, product
import sys


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


def get_npn_class(qvalues, func, transforms):
    """
    Form NPN class with a given function.
    """
    npn_class = []
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

        npn_class.append(cofunc1)
        npn_class.append(cofunc2)

    return set(npn_class)


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
        func = 2 ** qones - 1
        func_last = 2 ** (qvalues-1)
        processed = set()
        while func < func_last:
            if func not in processed:
                npn_class = get_npn_class(qvalues, func, transforms)
                npn_class_len = len(npn_class)
                processed.update(npn_class)
                num += 1
                func_str = f"{func:b}".zfill(qvalues)
                print(f"{num:6d} {func_str} {npn_class_len:4d}", flush=True)
                if func == 0:
                    break
            func = ncm(func)


def main():
    """
    An entry point.
    """
    for qargs in sys.argv[1:]:
        build_npn_classes(int(qargs))


if __name__ == '__main__':
    main()
