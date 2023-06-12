import os

from lrc_rs import lrc_rs

from codec import Codec

if __name__ == '__main__' :


    # compare
    codec = Codec(9, 6, [0, 1, 2])
    msg = b"\x01\x00\x00\x00\x00\x00"
    encoded_rs = codec.encode(msg)

    print("encoded_rs:", encoded_rs, bytes(encoded_rs))
    
    lrc = lrc_rs(10, 6, 2, 2,[1, 2])

    message = b"\x01\x00\x00\x00\x00\x00"

    out = lrc.encode(message)
    print("encode:", bytes(out))



    message = b"\x01\x00\x00\x02\x00\x00"

    out = lrc.encode(message)
    print("encode:", bytes(out))

    
    # test recover data using local parity
    err_msg = b"\x01\x02\x00\x02\x00\xffM\x12\x01\x02"
    decoded = lrc.decode_lrc(err_msg, [1, 5])
    print("decoded 1: ", decoded, bytes(decoded))

    # test recover parity using local parity:
    err_msg = b"\x01\x00\x00\x02\x00\x00M\x12\xf4\x42"
    decoded = lrc.decode_lrc(err_msg, [8, 9])
    print("decoded 2: ", decoded, bytes(decoded))


    # test decoding syndroms
    message = b"\x01\x00\x00\x01\x00\x00"

    out = lrc.encode(message)
    print("encode 3:", bytes(out))


    dec = b"\x01\x00\x00\x01\x00\x00\xce\x11\x01\x01"
    decoded = lrc.decode_lrc(dec, [])

    
    print('start decoding mix specific matrix')
    # test recover parity using global parity:
    err_msg = b"\x01\x03\x07\x01\x00\x00\xce\x11\x01\x01"
    decoded = lrc.decode_lrc(err_msg, [1,2])
    print("decoded 2: ", decoded, bytes(decoded))
    

    

    
