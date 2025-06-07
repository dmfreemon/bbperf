

def sendto(args, udp_sock, peer_addr, payload_bytes):
    num_payload_bytes = len(payload_bytes)

    num_bytes_sent = udp_sock.sendto(payload_bytes, peer_addr)

    if num_bytes_sent <= 0 or num_bytes_sent != num_payload_bytes:
        raise Exception("ERROR: udp_helper.sendto(): send failed")

    if args.verbosity > 2:
        print("udp_helper.sendto(): data sent: {}".format(
            payload_bytes.decode()), flush=True)
