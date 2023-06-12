from codec import Codec
import numpy as np


if __name__ == "__main__":
    # from high power to low power, x8 + x4 + x3 + x^2 + 1
    coefs = [1, 0, 0, 0, 1, 1, 1, 0, 1]
    gen = [1, 0]  # x + 1

    codec = Codec(12, 8, [0, 1, 2, 3])
    message = "10000000"
    message_bytes = message.encode("utf-8")
    print("message_bytes:", message_bytes)
    msg = codec.encode(message_bytes)
    print("encoded msg:", bytes(msg))

    message = "00000001"
    message_bytes = message.encode("utf-8")
    print("message_bytes:", message_bytes)
    msg = codec.encode(message_bytes)
    print("encoded msg:", bytes(msg))
    codec._compute_syndroms(msg)

    message = b"\x00\x00\x00\x00\x00\x00\x00\x00"
    # message_bytes = message.encode('utf-8')
    print("message_bytes:", message)
    msg = codec.encode(message)
    print("encoded msg:", bytes(msg))

    # add errors
    err_msg = b"\x00\x00\x99\x05\x00\x00\x00\x09\x00\x00\x00\x00"
    codec._compute_syndroms(err_msg)
    err_pos = [2, 3, 7]
    _, magnitude = codec.decode_vandermonde(err_msg, [2, 3, 7])
    decode_message = codec.decode_message(err_msg, err_pos, magnitude)

    print("decoded message :", bytes(decode_message))
