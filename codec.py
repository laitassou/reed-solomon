"""
"""
import numpy as np
from typing import List

from gf import GFGenerator


class Codec:
    """
    k : message length
    n : codeword length
    in other literature work we define rs(n, k) where n is codeword length
    and k is message length.
    """

    def __init__(self, n, k, root_powers: List):
        if n < k:
            raise ValueError("invalid config")

        # from high power to low power, x8 + x4 + x3 + x2 + 1
        self.gf_prim = [1, 0, 0, 0, 1, 1, 1, 0, 1]
        self.gf_gen = [1, 0]  # x
        self.gf = GFGenerator(self.gf_prim, self.gf_gen)
        self.k = k
        self.m = n - k
        self.n = n
        self.root_powers = root_powers
        self.gx = self._init_gx()

    def _init_gx(self):
        # repsresented with list [] where first postion is x^0
        legnth = len(self.root_powers) + 1
        px = [0] * legnth
        px[0] = 1
        for pow in self.root_powers:
            shift = [0] + px[:-1]
            mul = [0] * legnth
            root = self.gf.exp_lut[pow]
            for i in range(len(px)):
                mul[i] = self.gf.mul(px[i], root)
            for i in range(len(px)):
                px[i] = self.gf.add(mul[i], shift[i])

        print("px:", px)
        return px

    def encode(self, message: List):
        """
        Encode using LFSR
        Encoding works:
        Take a message m(x)= sigma(a(i) * x^(i))
        we multiply this message by x^(m)
        then we divide by g(x) and add r(x) as parity to message
        we obtain : c(x) = m(x) * x^(m)  + r(x) , c(x) is a multiple of g(x)
        This means that if message is transmitted without errors then roots of g(x)
        are also roots of c(x), this will be the property to use for decoding
        """

        # assume message is of class bytes of length k
        if len(message) != self.k:
            raise ValueError()
        m_x = [0] * self.k
        for i in range(self.k):
            m_x[i] = message[i]

        # LFSR
        state = [0] * (self.m)
        mult = [0] * (self.m)
        print("gx:", self.gx)
        for i in range(self.k):
            feedback = self.gf.add(m_x[i], state[self.m - 1])
            for j in range(self.m):
                mult[j] = self.gf.mul(self.gx[j], feedback)
            for j in reversed(range(self.m)):
                if j == 0:
                    state[j] = mult[j]
                else:
                    state[j] = self.gf.add(state[j - 1], mult[j])

        reverse = state[::-1]
        return m_x + reverse

    def _compute_syndroms(self, msg):
        """
        compute syndroms for received message
        """
        if len(msg) != self.n:
            raise ValueError()

        # init syndroms
        syndroms = [0] * self.m
        for j in range(self.m):
            for i in range(self.n):
                pow = (self.root_powers[j] * i) % 255
                syndroms[j] = self.gf.add(
                    syndroms[j], self.gf.mul(msg[self.n - 1 - i], self.gf.exp_lut[pow])
                )

        print("syndroms:", syndroms)
        return syndroms

    def decode_vandermonde(self, msg, erasure_pos: List[int]):
        """ """
        # Ref design, defines decode matrixes
        # Via Vandermonde :  M(x) * err(x) = S(x)

        for pos in erasure_pos:
            if pos >= self.n or pos < 0:
                raise ValueError("Invalid positions")

        syndroms = self._compute_syndroms(msg)
        print("syndroms:", syndroms)

        # Matrix
        vand_matrix = []
        print("vand_matrix:", vand_matrix)
        for j in range(len(erasure_pos)):
            row = []
            for i in range(len(erasure_pos)):
                pow = (self.root_powers[j] * (self.n - 1 - erasure_pos[i])) % 255
                row.append(self.gf.exp_lut[pow])
            vand_matrix.append(row)

        print("vand_matrix:", vand_matrix)

        # Matrix inversion, we call this Vandermonde as we obtain a
        # Vandermonde Matrix, which is reversible
        nb_errors = len(erasure_pos)
        synds = syndroms[:nb_errors]
        # Jordan/Gauss
        inv_vand_matrix = []
        for i in range(nb_errors):
            inv_vand_matrix.append(vand_matrix[i].copy())

        for i in range(nb_errors):
            row = inv_vand_matrix[i].copy()
            # normalize
            row_norm = [0] * nb_errors
            print("row:", row)
            for k in range(nb_errors):
                print("row:", row[k], row[i])
                row_norm[k] = self.gf.div(row[k], row[i])
            print("row norm:", row_norm)
            synds[i] = self.gf.div(synds[i], row[i])
            inv_vand_matrix[i] = row_norm.copy()
            print("inv_vand_matrix after norm", inv_vand_matrix, synds)
            for j in range(nb_errors):
                if j == i:
                    continue

                norm = inv_vand_matrix[i][i]
                for k in range(nb_errors):
                    # print("row:", row[k], row[i])
                    inv_vand_matrix[i][k] = self.gf.div(inv_vand_matrix[i][k], norm)
                print("nom inv matrix:", inv_vand_matrix)
                synds[i] = self.gf.div(synds[i], norm)

                for k in range(nb_errors):
                    inv_vand_matrix[i][k] = self.gf.mul(
                        inv_vand_matrix[i][k], inv_vand_matrix[j][i]
                    )
                synds[i] = self.gf.mul(synds[i], inv_vand_matrix[j][i])

                print("inv_vand_matrix: mult", inv_vand_matrix)
                for k in range(nb_errors):
                    inv_vand_matrix[j][k] = self.gf.add(
                        inv_vand_matrix[j][k],
                        inv_vand_matrix[i][k],
                    )
                synds[j] = self.gf.add(synds[j], synds[i])

            print("inv vand after j rows:", inv_vand_matrix, synds)
            norm = inv_vand_matrix[i][i]
            for k in range(nb_errors):
                # print("row:", row[k], row[i])
                inv_vand_matrix[i][k] = self.gf.div(inv_vand_matrix[i][k], norm)
            print("nom inv matrix:", inv_vand_matrix)
            synds[i] = self.gf.div(synds[i], norm)

        print("inv vand:", inv_vand_matrix, synds)

        return inv_vand_matrix, synds
    
    def recover_message(self, msg, erasure_pos, magnitude):
        """
        """
        message = []
        for i in range(len(msg)):
            if i in erasure_pos:
                pos = erasure_pos.index(i)
                print("correction:" ,i, pos)
                message.append(self.gf.add(msg[i], magnitude[pos]))
            else:
                message.append(msg[i])
        return message
        
    def decode_berlekamp(self, msg, erasure_pos: List[int]):
        """
        # No need to apply Berlekamp algorithm
        # as we know error positions.
        # we need only to compute error magnitudes
        # via Forney algorithm
        """
        # define erasure locator polynom
        # apply Forney, Lagrange interpolation
        syndroms = self._compute_syndroms(msg)
        # Lagrange interpolation, basic equation
        # for i in range (self.m)
        #      s(i) = sigma(e(i) * root_i^ pos_error_j(i))


if __name__ == "__main__":
    # from high power to low power, x8 + x4 + x3 + x + 1
    coefs = [1, 0, 0, 0, 1, 1, 0, 1, 1]
    gen = [1, 1]  # x + 1

    codec = Codec(12, 8, [1, 2, 3, 4])
    message = "00000000"

    coded = codec.encode(message)
    print("coded Message ", coded)
    codec._compute_syndroms(coded)
