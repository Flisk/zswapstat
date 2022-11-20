# zswapstat

This is a relatively simple script that provides human-readable statistics for
the [zswap Linux kernel module][1]. It outputs each field provided in
`/sys/kernel/debug/zswap`, as well as some values derived from those fields.

## Requirements

Python 3.9 or newer. Older versions may work, but have not been tested.

## Sample Output

```
# zswapstat
same_filled_pages      1692
stored_pages           11626
pool_total_size        20344832
duplicate_entry        0
written_back_pages     0
reject_compress_poor   59
reject_kmemcache_fail  0
reject_alloc_fail      0
reject_reclaim_fail    0
pool_limit_hit         0

compressed             19.4 MiB
uncompressed           45.4 MiB
space_savings          0.573
```

```
# zswapstat -h
usage: zswapstat [-h] [--block-size {b,k,m,g,t,p,e,z,y}] [--si]

optional arguments:
  -h, --help            show this help message and exit
  --block-size {b,k,m,g,t,p,e,z,y}, -B {b,k,m,g,t,p,e,z,y}
                        Unit for scaling calculated values
  --si                  Use SI units for size scaling (base-10 instead of base-2)
```

## Licensing

This script is licensed under the ISC license. The license terms are listed in
the copyright header of `zswapstat.py`.

[1]: https://www.kernel.org/doc/html/latest/admin-guide/mm/zswap.html
