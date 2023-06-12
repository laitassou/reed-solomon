import os
import random 
from codec import Codec


if __name__ == "__main__":
    K = 8
    N = 12
    M = 4 
    codec = Codec(N, K, [0, 1, 2, 3])
    
    # TEST OK 
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

    # add  3 errors
    err_msg = b"\x00\x00\x99\x05\x00\x00\x00\x09\x00\x00\x00\x00"
    codec._compute_syndroms(err_msg)
    err_pos = [2, 3, 7]
    _, magnitude = codec.decode_vandermonde(err_msg, [2, 3, 7])
    decoded_message = codec.recover_message(err_msg, err_pos, magnitude)

    print("decoded message :", bytes(decoded_message))
    if (bytes(decoded_message[:len(message)]) != message):
        raise ValueError("Error decoding message,%s", message)
   
    message = b"\x01\x00\x00\x00\x00\x00\x00\x00"
    # message_bytes = message.encode('utf-8')
    print("message_bytes:", message)
    msg = codec.encode(message)
    print("encoded msg:", bytes(msg))

    # add errors
    err_msg = b"\x0a\x00\x00\xfe\x00\x00\x00\x00\xfe\x81\xf2\x8c"
    print("error message", err_msg)
    err_pos = [0, 3]
    print("err_pos:", err_pos)
    _, magnitude = codec.decode_vandermonde(err_msg, err_pos)
    decoded_message = codec.recover_message(err_msg, err_pos, magnitude)

    print("decoded message :", bytes(decoded_message))
    if (bytes(decoded_message[:len(message)]) != message):
        raise ValueError("Error decoding message,%s", message)


    message = b"\x01\x00\x00\x00\x00\x00\x00\x00"
    # message_bytes = message.encode('utf-8')
    print("message_bytes:", message)
    msg = codec.encode(message)
    print("encoded msg:", bytes(msg))

    # add errors
    err_msg = b"\x0a\x00\x00\xfe\x00\x00\x00\x00\xfe\x81\xf2\x8c"
    print("error message", err_msg)
    err_pos = [0, 3]
    print("err_pos:", err_pos)
    _, magnitude = codec.decode_vandermonde(err_msg, err_pos)
    decoded_message = codec.recover_message(err_msg, err_pos, magnitude)

    print("decoded message :", bytes(decoded_message))
    if (bytes(decoded_message[:len(message)]) != message):
        raise ValueError("Error decoding message,%s", message)

    # Random
    for i in range(1000):
        print("iteration:", i)
        message = os.urandom(K)
        # message_bytes = message.encode('utf-8')
        print("message_bytes:", message)
        msg = codec.encode(message)
        print("encoded msg:", bytes(msg))

        # add random errors up to M
        nb_error_insert = random.randint(1, M)
        list_of_positions = random.sample(range(0, N-1), nb_error_insert)
        list_of_errors = os.urandom(nb_error_insert)
        print("list_of_positions:", list_of_positions)
        print("list_of_errors:", list_of_errors)
    
        err_msg = msg.copy()
        count = 0
        for i in range(len(msg)):
            if i in  list_of_positions:
                err_msg[i] = list_of_errors[count]
                count = count + 1
        
        print("err_msg :", bytes(err_msg))

        _, magnitude = codec.decode_vandermonde(err_msg, list_of_positions)
        decoded_message = codec.recover_message(err_msg, list_of_positions, magnitude)

        print("decoded message :", bytes(decoded_message))
        if (bytes(decoded_message[:len(message)]) != message):
            raise ValueError("Error decoding message,%s", message)    