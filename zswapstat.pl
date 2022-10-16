#!/usr/bin/perl
# zswapstat -- convenience script for reporting zswap statistics
# see also: https://www.kernel.org/doc/html/latest/vm/zswap.html

use strict;
use warnings;

use constant ZSWAP_DEBUG_DIR => "/sys/kernel/debug/zswap";

sub read_file {
    my ($path) = @_;
    open(my $f, '<', $path) or die "couldn't open $path";
    my @contents = <$f>;
    close($f) or die "couldn't close $path";
    return $contents[0];
}

my $page_size = `getconf PAGE_SIZE`;

opendir(my $d, ZSWAP_DEBUG_DIR)
    or die "couldn't open zswap debug dir; is the module loaded and enabled?";
my @files = readdir $d;
closedir($d);

open(COLUMN, "| column --separator : --table")
    or die "couldn't run column program";

select(COLUMN);

my ($value, $pool_total_size, $stored_pages);

foreach (@files) {
    if ($_ eq "." || $_ eq "..") {
        next;
    }

    $value = read_file(ZSWAP_DEBUG_DIR . "/" . $_);
    chomp($value);

    print($_, ":", $value, "\n");

    if ($_ eq "pool_total_size") {
        $pool_total_size = $value;
    } elsif ($_ eq "stored_pages") {
        $stored_pages = $value;
    }
}

my $stored_size = $stored_pages * $page_size;

my $compressed_mb = $pool_total_size / 1000 / 1000;
my $uncompressed_mb = ($stored_pages * $page_size) / 1000 / 1000;

my $savings =
    $stored_size > 0
    ? 1 - ($pool_total_size / $stored_size)
    : 0;

print("\n");
printf("compressed_size:%.1f MB\n", $compressed_mb);
printf("uncompressed_size:%.1f MB\n", $uncompressed_mb);
printf("space_savings:%.3f\n", $savings);
