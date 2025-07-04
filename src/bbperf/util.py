# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

import sys
import socket

from . import const


def validate_args(args):
    if args.server and args.client:
        raise Exception("ERROR: cannot be both client and server")

    if (not args.server) and (not args.client):
        raise Exception("ERROR: must be either a client or a server")

    if args.port > 65535:
        raise Exception("ERROR: invalid server port {}".format(args.port))

    if args.verbosity and args.quiet:
        raise Exception("ERROR: cannot specify both verbosity and quiet")


def convert_udp_pps_to_batch_info(packets_per_sec):

    batch_size = const.RATE_LIMITED_BATCH_SIZE_PKTS_UDP_PKTS

    batches_per_sec = packets_per_sec / batch_size

    if batches_per_sec < 1:
        batches_per_sec = 1
        batch_size = 1

    delay_between_batches = 1.0 / batches_per_sec

    return batch_size, delay_between_batches


def done_with_socket(mysock):
    try:
        mysock.shutdown(socket.SHUT_RDWR)
    except:
        pass

    try:
        mysock.close()
    except:
        pass


def threads_are_running(thread_list):
    any_running = False

    for t in thread_list:
        if t.is_alive():
            any_running = True
        else:
            if t.exitcode != 0:
                # thread existing abnormally -- kill everything and go home
                raise Exception("FATAL: one of the subprocesses existed abnormally, name: {}, exitcode: {}".format(t.name, t.exitcode))

    return any_running


def parse_r_record(args, s1):
    r_record = {}

    swords = s1.split()

    # literal "a"
    r_record["r_record_type"] = swords[1]
    r_record["r_pkt_sent_time_sec"] = float(swords[2])
    r_record["r_sender_interval_duration_sec"] = float(swords[3])
    r_record["r_sender_interval_pkts_sent"] = int(swords[4])                # valid for udp only
    r_record["r_sender_interval_bytes_sent"] = int(swords[5])
    r_record["r_sender_total_pkts_sent"] = int(swords[6])                   # valid for udp only
    # literal "b"
    r_record["r_receiver_interval_duration_sec"] = float(swords[8])
    r_record["r_receiver_interval_pkts_received"] = int(swords[9])          # valid for udp only
    r_record["r_receiver_interval_bytes_received"] = int(swords[10])
    r_record["r_receiver_total_pkts_received"] = int(swords[11])            # valid for udp only
    # literal "c"
    r_record["r_pkt_received_time_sec"] = float(swords[13])
    r_record["interval_dropped"] = int(swords[14])
    r_record["interval_dropped_percent"] = float(swords[15])
    r_record["is_sample_valid"] = int(swords[16])
    # literal "d"

    r_record["rtt_sec"] = r_record["r_pkt_received_time_sec"] - r_record["r_pkt_sent_time_sec"]
    r_record["rtt_ms"] = r_record["rtt_sec"] * 1000

    try:
        # first record received has zeros
        sender_interval_rate_bps = (r_record["r_sender_interval_bytes_sent"] * 8.0) / r_record["r_sender_interval_duration_sec"]
    except ZeroDivisionError:
        sender_interval_rate_bps = 0

    r_record["sender_interval_rate_mbps"] = sender_interval_rate_bps / (10 ** 6)

    r_record["receiver_interval_rate_bytes_per_sec"] = r_record["r_receiver_interval_bytes_received"] / r_record["r_receiver_interval_duration_sec"]

    receiver_interval_rate_bps = r_record["receiver_interval_rate_bytes_per_sec"] * 8
    r_record["receiver_interval_rate_mbps"] = receiver_interval_rate_bps / (10 ** 6)

    r_record["buffered_bytes"] = int( r_record["receiver_interval_rate_bytes_per_sec"] * r_record["rtt_sec"] )

    if args.udp:
        try:
            # first record received has zeroes
            r_record["sender_pps"] = int(r_record["r_sender_interval_pkts_sent"] / r_record["r_sender_interval_duration_sec"])
        except ZeroDivisionError:
            r_record["sender_pps"] = 0

        r_record["receiver_pps"] = int(r_record["r_receiver_interval_pkts_received"] / r_record["r_receiver_interval_duration_sec"])
        r_record["total_dropped"] = r_record["r_sender_total_pkts_sent"] - r_record["r_receiver_total_pkts_received"]
        if r_record["total_dropped"] < 0:
            # this can happen if we happen to pick up an "early" a_b block (probably just negative by 1 or 2, not a big deal)
            r_record["total_dropped"] = 0

    else:
        r_record["sender_pps"] = -1
        r_record["receiver_pps"] = -1
        r_record["total_dropped"] = -1

    return r_record


def validate_data_connection(args, run_id, data_connection_initial_str):
    w = data_connection_initial_str.split(" ")

    if w[0] != "data":
        raise Exception("ERROR: data connection invalid (does not start with data) run_id {} received {}".format(
            run_id, data_connection_initial_str))

    data_connection_run_id = w[1]

    if data_connection_run_id != run_id:
        raise Exception("ERROR: data connection invalid (run_id incorrect) control run_id {} data run_id {} received {}".format(
            run_id, data_connection_run_id, data_connection_initial_str))

    if args.verbosity:
        print("data run_id is valid", flush=True)
