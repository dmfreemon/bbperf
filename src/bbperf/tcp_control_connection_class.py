# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

import json
import argparse
import socket

from . import const
from . import util

from .exceptions import PeerDisconnectedException

# this needs to be serializable to get from driver to child thread
class TcpControlConnectionClass:

    # class variables

    def __init__(self, control_sock):
        self.control_sock = control_sock
        self.args = None

        self.read_buffer = bytearray()

        control_sock.settimeout(const.SOCKET_TIMEOUT_SEC)

        # set TCP_NODELAY because the control messages back to the
        # sender from the data receiver are part of the RTT measurement
        control_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def set_args(self, args):
        self.args = args


    def send_bytes(self, payload_bytes):
        self.control_sock.sendall(payload_bytes)

        if self.args.verbosity > 3:
            print("control conn sending: {}".format(payload_bytes.decode()), flush=True)


    def send_string(self, str0):
        self.send_bytes(str0.encode())


    def recv(self, max_bytes_to_read):

        recv_bytes = self.control_sock.recv(max_bytes_to_read)

        if len(recv_bytes) == 0:
            raise PeerDisconnectedException()

        self.read_buffer.extend(recv_bytes)


    def recv_into_buffer_until_minimum_size(self, minimum_buffer_size):

        while len(self.read_buffer) < minimum_buffer_size:

            num_bytes_remaining = minimum_buffer_size - len(self.read_buffer)

            self.recv(num_bytes_remaining)


    def recv_exact_num_bytes(self, exact_num_bytes_to_read):

        self.recv_into_buffer_until_minimum_size(exact_num_bytes_to_read)

        received_bytes = self.read_buffer[ 0 : exact_num_bytes_to_read ]
        self.read_buffer = self.read_buffer[ exact_num_bytes_to_read : ]

        return received_bytes


    def recv_into_buffer_until_substr_found(self, substr_bytes):

        while True:

            substr_idx = self.read_buffer.find(substr_bytes)
            if substr_idx > -1:
                # found
                break

            self.recv(const.BUFSZ)

        return substr_idx


    def recv_initial_string(self):
        # "control " + uuid of 36 characters
        len_str = 8 + 36

        self.recv_into_buffer_until_minimum_size(len_str)

        received_bytes = self.read_buffer[ 0 : len_str ]
        self.read_buffer = self.read_buffer[ len_str : ]

        received_str = received_bytes.decode()

        uuid = received_str[8:]

        return uuid


    def receive_args_from_client(self):
        # starts with "{" and ends with "}"

        substr_idx = self.recv_into_buffer_until_substr_found(b'}')

        received_bytes = self.read_buffer[ 0 : substr_idx + 1 ]
        self.read_buffer = self.read_buffer[ substr_idx + 1 : ]

        received_str = received_bytes.decode()

        args_d = json.loads(received_str)

        # recreate args as if it came directly from argparse
        args = argparse.Namespace(**args_d)

        return args


    def wait_for_start_message(self):
        len_str = len(const.START_MSG)

        self.recv_into_buffer_until_minimum_size(len_str)

        received_bytes = self.read_buffer[ 0 : len_str ]
        self.read_buffer = self.read_buffer[ len_str : ]

        received_str = received_bytes.decode()

        if received_str != const.START_MSG:
            raise Exception("ERROR: failed to receive start message")


    def recv_a_c_block(self):
        start_bytes = b' a '
        end_bytes = b' c '

        substr_idx = self.recv_into_buffer_until_substr_found(end_bytes)

        received_bytes = self.read_buffer[ 0 : substr_idx + 3 ]
        self.read_buffer = self.read_buffer[ substr_idx + 3 : ]

        if not (received_bytes.startswith(start_bytes) and received_bytes.endswith(end_bytes)):
            raise Exception("recv_a_c_block failed")

        return received_bytes


    def recv_a_d_block(self):
        start_bytes = b' a '
        end_bytes = b' d '

        substr_idx = self.recv_into_buffer_until_substr_found(end_bytes)

        received_bytes = self.read_buffer[ 0 : substr_idx + 3 ]
        self.read_buffer = self.read_buffer[ substr_idx + 3 : ]

        if not (received_bytes.startswith(start_bytes) and received_bytes.endswith(end_bytes)):
            raise Exception("recv_a_d_block failed")

        return received_bytes


    def close(self):
        util.done_with_socket(self.control_sock)
