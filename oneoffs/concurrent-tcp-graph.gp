#!/usr/bin/gnuplot

# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

#maxy1 = 3000
#maxy2 = 450

# no warp 1 concurrent
#datafile1 = "/tmp/bbperf-graph-data-tcp-0awjkcwe"
#pngfile = "concurrent-tcp-graph-no-warp-1.png"

# with warp 1 concurrent
#datafile1 = "/tmp/bbperf-graph-data-tcp-1jphj_ou"
#pngfile = "concurrent-tcp-graph-warp-1.png"

#maxy1 = 12000
#maxy2 = 450

# no warp 2 concurrent
#datafile1 = "/tmp/bbperf-graph-data-tcp-tykna1_8"
#datafile2 = "/tmp/bbperf-graph-data-tcp-5tx5l_0n"
#pngfile = "concurrent-tcp-graph-no-warp-2.png"

# with warp 2 concurrent
#datafile1 = "/tmp/bbperf-graph-data-tcp-zp6bclc4"
#datafile2 = "/tmp/bbperf-graph-data-tcp-16_ed27r"
#pngfile = "concurrent-tcp-graph-warp-2.png"

maxy1 = 25000
maxy2 = 250

# no warp 4 concurrent
#datafile1 = "/tmp/bbperf-graph-data-tcp-8xjnqent"
#datafile2 = "/tmp/bbperf-graph-data-tcp-o35__mv3"
#datafile3 = "/tmp/bbperf-graph-data-tcp-ml2tbm6p"
#datafile4 = "/tmp/bbperf-graph-data-tcp-3kpom5x4"
#pngfile = "concurrent-tcp-graph-no-warp-4.png"

# with warp 4 concurrent
datafile1 = "/tmp/bbperf-graph-data-tcp-xdux57u9"
datafile2 = "/tmp/bbperf-graph-data-tcp-ia0jj9ot"
datafile3 = "/tmp/bbperf-graph-data-tcp-itigjslj"
datafile4 = "/tmp/bbperf-graph-data-tcp-znlha1rw"
pngfile = "concurrent-tcp-graph-warp-4.png"

set grid

set key right top
set key box opaque

set style data lines

# x,y
# noenhanced to avoid need to escape underscores in labels
set terminal pngcairo size 1200,500 noenhanced
set output pngfile

# generate stats for column 2
# nooutput - do not sent to "screen"
# name - prefix
stats datafile1 using 1 nooutput name "datafile1_XRANGE"
stats datafile2 using 1 nooutput name "datafile2_XRANGE"
stats datafile3 using 1 nooutput name "datafile3_XRANGE"
stats datafile4 using 1 nooutput name "datafile4_XRANGE"

set multiplot title "bbperf concurrent TCP ".pngfile layout 1,1

set lmargin 12

# dt 1 (solid), dt 2 (dotted), dt 4 (dot dash)
# lc 1 (purple), lc 2 (green), lc 3 (lt blue), lc 4 (orange), lc 6 (blue), lc 7 (red), lc 8 (black)

set ylabel "ms"
set xrange [0:300]
set yrange [0:maxy1]

plot datafile1 using ($1-datafile1_XRANGE_min):7 title "unloaded RTT" lw 2 lc 1, \
     ""        using ($1-datafile1_XRANGE_min):8 title "loaded RTT (flow #1)" lw 2 lc 4, \
     datafile2 using ($1-datafile2_XRANGE_min):8 title "loaded RTT (flow #2)" lw 2 lc 6, \
     datafile3 using ($1-datafile3_XRANGE_min):8 title "loaded RTT (flow #3)" lw 2 lc 2, \
     datafile4 using ($1-datafile4_XRANGE_min):8 title "loaded RTT (flow #4)" lw 2 lc 3

#set ylabel "Mbps"
#set yrange [0:maxy2]

#plot datafile1 using ($1-datafile1_XRANGE_min):6 title "goodput (flow #1)" lw 1.5 lc 4
#     datafile2 using ($1-datafile2_XRANGE_min):6 title "goodput (flow #2)" lw 1.5 lc 6
#     datafile3 using ($1-datafile3_XRANGE_min):6 title "goodput (flow #3)" lw 1.5 lc 2, \
#     datafile4 using ($1-datafile4_XRANGE_min):6 title "goodput (flow #4)" lw 1.5 lc 3

unset multiplot

