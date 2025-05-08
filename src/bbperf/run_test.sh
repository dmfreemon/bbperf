#!/bin/bash

# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

SERVER_ADDR=127.0.0.1

DURATION=10

OPTARGS=""
#OPTARGS="-k -g"

set -x

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -R

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -b 5M

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -b 5M -R

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -b 5Kpps

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -b 5Kpps -R

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -b 20Kpps

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -b 20Kpps -R

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -b 5M -u

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -b 5M -u -R

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -b 5Kpps -u

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -b 5Kpps -u -R

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -b 20Kpps -u

./bbperf.py -c $SERVER_ADDR -t $DURATION $EXTRAARGS -b 20Kpps -u -R
