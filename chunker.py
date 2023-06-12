import os.path
from constants import K, M, N, roots

from codec import Codec
from typing import List
from struct import pack


# file to check
file_path = r"/etc/magic"

sz = os.path.getsize(file_path)
print(f"The {file_path} size is", sz, "bytes")

K = 8
chunk_size = sz // (K - 1)
buffer_size = 20


class Chunker:
    """ """

    def __init__(self, n, k, roots):
        if n <= k:
            raise ValueError(f"invalid config {n}, {k}")
        self.n = n
        self.k = k
        self.m = n - k
        self.codec = Codec(n, k, roots)

        if not os.path.exists("data"):
            os.makedirs("data")

    def each_chunk(self, stream, id):
        size = 0
        to_break = False
        stream.seek(id * chunk_size)
        while True:  # until EOF
            if size + buffer_size < chunk_size:
                read_size = buffer_size
            else:
                read_size = chunk_size - size
            to_break = True
            chunk = stream.read(read_size)
            if not chunk:
                yield chunk
                break
            size = size + read_size
            if to_break:
                yield chunk
                break

    def one_chunk(self, stream, id):
        size = 0
        to_break = False
        buffer_read = 20
        read_size = buffer_read
        while True:  # until EOF
            if size + buffer_size < chunk_size:
                read_size = buffer_read
            else:
                read_size = chunk_size - size
            to_break = True
            chunk = stream.read(read_size)
            if not chunk:
                yield chunk
                break
            size = size + read_size
            if to_break:
                yield chunk
                break

    def get_all_chunks(self, file):
        with open(file, "rb") as fp:
            for x in range(self.k):
                it = self.each_chunk(fp, x)
                for el in it:
                    print("el:", el)
                    yield el

    def _encode(self):
        """
        Split file into chunks and encode in order to generate parity
        chunks
        """
        chunks = self.get_all_chunks(file_path)

        data = []
        for chunk in chunks:
            data.append(chunk)

        for i in range(len(data[0])):
            to_encode = bytearray()
            for x in range(K):
                if x == K - 1:
                    try:
                        byte_from_chunk = data[x][i]
                        print("normal byte_from_chunk", byte_from_chunk)
                    except Exception as exc:
                        print(str(exc))
                        byte_from_chunk = 0x00
                        print("except byte_from_chunk", byte_from_chunk)

                    to_encode.append(byte_from_chunk)
                else:
                    to_encode.append(data[x][i])
            print("to_encode:", to_encode)
            message = to_encode
            print("message:", message)
            encoded = self.codec.encode(message)
            print("encoded:", encoded)

            yield encoded

    def encode(self):
        """ """
        encoded = self._encode()

        fdescriptors = []
        for i in range(N):
            fp = open(f"./data/file-chunks-{i}", "wb")
            fdescriptors.append(fp)

        print(fdescriptors)
        for enc in encoded:
            print("enc:", enc)
            for i, el in enumerate(enc):
                print("i, el:", i, el, chr(el))
                fdescriptors[i].write(pack("B", el))

        for i in range(N):
            fdescriptors[i].close()

    def reconstruct(self, positions: List[int]):
        """
        Given error positions, read necessary chunks and generate original
        file
        """

        for el in positions:
            if el >= self.n or el < 0:
                raise ValueError(f"position error invalid {el}")

        if len(positions) > self.m:
            raise ValueError("impossible to reconstruct more than {self.m}")

        print("decode")
        # chunks to read from, select only k chunks
        to_read = []
        for i in range(N):
            if i not in positions:
                to_read.append(i)

            if len(to_read) == self.k:
                break

        fdescriptors = []
        fdreconstruct = {}

        data = {}

        error_positions = []

        for k in range(self.n):
            if k not in to_read:
                error_positions.append(k)

        # prepare files to write reconstructed chunks
        for u in error_positions:
            file = f"./data/file-chunks-reconstrcut-{u}"
            fp_rec = open(file, "wb")
            fdreconstruct[u] = fp_rec

        for i in to_read:
            file = f"./data/file-chunks-{i}"
            fp = open(file, "rb")
            fdescriptors.append(fp)

            chunks = self.one_chunk(fp, i)
            length = 0
            for chk in chunks:
                print("chk:", i, chk)
                data[i] = chk
                length = len(chk)

        print("data:", data)
        for j in range(length):
            to_decode = bytearray()
            for i in range(self.n):
                if i in data.keys():
                    to_decode.append(data[i][j])
                else:
                    to_decode.append(0x00)
            print("to_decode:", to_decode, type(to_decode), error_positions)

            _, magnitude = self.codec.decode_vandermonde(
                bytes(to_decode), error_positions
            )

            decoded_message = self.codec.recover_message(
                bytes(to_decode), error_positions, magnitude
            )

            print("decode_message", j, bytes(decoded_message))

            # write to rec chunk
            for u in error_positions:
                fdreconstruct[u].write(pack("B", decoded_message[u]))

        for i in range(self.k):
            fdescriptors[i].close()

        # write to rec chunk
        for u in error_positions:
            fdreconstruct[u].close()


if __name__ == "__main__":
    chunker = Chunker(N, K, roots)
    encoded = chunker.encode()
    decode = chunker.reconstruct([0])
