#!/usr/bin/env python3

# ISC License
# Copyright 2022 Flisk <self@flisk.xyz>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

import argparse
import os
import resource
import sys


ZSWAP_DEBUG_DIR = '/sys/kernel/debug/zswap'

UNITS_ARGS = ['b', 'k', 'm', 'g', 't', 'p', 'e', 'z', 'y']
UNITS_IEC = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'GiB', 'TiB', 'EiB', 'ZiB', 'YiB']
UNITS_SI = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']


def main():
    args = parse_args()

    try:
        os.chdir(ZSWAP_DEBUG_DIR)
    except IOError as e:
        hint = {
            PermissionError: "did you forget to sudo?",
            FileNotFoundError: "is the zswap module available?",
        }.get(type(e))
        fail(f"couldn't chdir to {ZSWAP_DEBUG_DIR}: {e.strerror}", hint)

    output = []
    pool_total_size = None
    stored_pages = None

    for name in os.listdir(ZSWAP_DEBUG_DIR):
        with open(name) as f:
            value = f.read()
            value = value.strip()
            value = int(value)
        
        output.append((name, value))

        if not pool_total_size and name == 'pool_total_size':
            pool_total_size = value
        if not stored_pages and name == 'stored_pages':
            stored_pages = value
    
    if not pool_total_size:
        raise RuntimeError("missing required value: pool_total_size")
    if not stored_pages:
        raise RuntimeError("missing required value: stored_pages")

    # sentinel value telling print_output to insert a line break
    output.append(('', None))

    stored_size = stored_pages * resource.getpagesize()

    compressed = convert_size(pool_total_size, args)
    output.append(('compressed', compressed))

    uncompressed = convert_size(stored_size, args)
    output.append(('uncompressed', uncompressed))

    if stored_size > 0:
        savings = 1 - (pool_total_size / stored_size)
        savings = round(savings, 3)
    else:
        savings = 0

    output.append(('space_savings', savings))

    print_output(output)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--block-size', '-B',
        choices=UNITS_ARGS,
        default='m',
        help="Unit for scaling calculated values",
    )
    parser.add_argument(
        '--si',
        action='store_const', const=1000,
        default=1024,
        dest='size_base',
        help="Use SI units for size scaling (base-10 instead of base-2)",
    )
    return parser.parse_args()


def convert_size(n, args):
    exponent = UNITS_ARGS.index(args.block_size)
    value = n / args.size_base ** exponent

    if exponent > 1:
        value = round(value, 1)
    else:
        value = int(value)

    if args.size_base == 1024:
        unit = UNITS_IEC[exponent]
    else:
        unit = UNITS_SI[exponent]

    return f'{value} {unit}'


def print_output(output):
    max_field_len = max([len(name) for (name, _value) in output])
    row_format = f'{{:<{max_field_len}}}  {{:}}'

    for (name, value) in output:
        if name == '':
            print()
        else:
            print(row_format.format(name, value))


def fail(msg, hint=None):
    print(f'fatal: {msg}', file=sys.stderr)
    if hint:
        print(hint, file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
    main()