# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

import time

from . import const

class DataSampleEvaluatorClass:

    # args are client args
    def __init__(self, args0):
        self.args = args0
        self.valid_flag = False

    # once a sample is valid then all subsequent samples are valid
    def is_sample_valid(self, run_mode_running_start_time, dropped_this_interval_percent, curr_time):
        if self.valid_flag:
            return True

        # samples are never valid until we have passed the "ignore time"
        if curr_time < (run_mode_running_start_time + const.DATA_SAMPLE_IGNORE_TIME_SEC):
            return False

        # udp
        if self.args.udp and (dropped_this_interval_percent > 0):
            self.valid_flag = True
            return True

        # tcp
        if not self.args.udp:
            # this is a bit challenging to get right for all the various network conditions we might encounter
            # preserving this first attempt as comments just in case we might want to go back to something like this
            # throughput_rate_ratio = abs(sender_throughput_rate_mbps - receiver_throughput_rate_mbps) / receiver_throughput_rate_mbps
            # if (throughput_rate_ratio < 0.01) and (receiver_throughput_rate_mbps > 1.0):
            #     self.valid_flag = True
            #     return True

            # in the meantime, we'll do the following because it is easier and probably better (or at least good enough)
            if self.args.reverse:
                if curr_time > (run_mode_running_start_time + const.DATA_SAMPLE_IGNORE_TIME_TCP_DOWN_SEC):
                    self.valid_flag = True
                    return True
            else:
                if curr_time > (run_mode_running_start_time + const.DATA_SAMPLE_IGNORE_TIME_TCP_UP_SEC):
                    self.valid_flag = True
                    return True

        return False

