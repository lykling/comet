"""confuse command
"""
from collections.abc import Iterable


def args_parser(parser):
    """parse arguments
    """
    parser.add_argument(
        '-c',
        '--clarify',
        action='store_true',
        help='clarify',
    )
    parser.add_argument(
        '-m',
        '--magic',
        type=int,
        help='magic number',
    )
    parser.add_argument(
        '-b',
        '--block-size',
        type=int,
        default=8,
        help='block size',
    )
    parser.add_argument(
        '-B',
        '--block-order',
        type=str,
        default='1,3,0,2',
        help='block confuse order',
    )
    parser.add_argument(
        'number',
        type=int,
        help='number to confuse or clarify',
    )


def _bit_mask(block_size: int, shift: int):
    """get bit mask
    """
    return ((1 << block_size) - 1) << (shift * block_size)


def _move_bits(number: int, block_size: int, pos_a: int, pos_b: int):
    """move bits
    """
    mask_a = _bit_mask(block_size, pos_a)
    mask_b = _bit_mask(block_size, pos_b)
    if pos_a > pos_b:
        return ((number & mask_a) >> ((pos_a - pos_b) * block_size)) & mask_b
    if pos_a < pos_b:
        return ((number & mask_a) << ((pos_b - pos_a) * block_size)) & mask_b
    return number & mask_a


def _clarify(number: int, magic: int, block_size: int,
             rules: Iterable[tuple[int, int]], expand_mask: int):
    """clarify number
    """
    number ^= magic
    result = 0
    for pos_a, pos_b in rules:
        result |= _move_bits(number, block_size, pos_a, pos_b)

    result |= number & expand_mask

    return result


def _confuse(number: int, magic: int, block_size: int,
             rules: Iterable[tuple[int, int]], expand_mask: int):
    """confuse number
    """
    result = 0
    for pos_a, pos_b in rules:
        result |= _move_bits(number, block_size, pos_a, pos_b)

    result |= number & expand_mask
    result ^= magic

    return result


def clarify(number: int, magic: int, block_size: int, block_order: str):
    """clarify command
    """
    order = list(map(int, block_order.split(',')))
    rules = zip(order, range(len(order)))
    result = _clarify(number, magic, block_size, rules, 0xffffffff00000000)
    return result


def confuse(number: int, magic: int, block_size: int, block_order: str):
    """confuse command
    """
    order = list(map(int, block_order.split(',')))
    rules = zip(range(len(order)), order)
    result = _confuse(number, magic, block_size, rules, 0xffffffff00000000)
    return result


def entrypoint(args):
    """command entrypoint
    """
    if args.clarify:
        print(
            clarify(args.number, args.magic, args.block_size,
                    args.block_order))
    else:
        print(
            confuse(args.number, args.magic, args.block_size,
                    args.block_order))
