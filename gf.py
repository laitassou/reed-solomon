"""
"""
import numpy as np
from typing import List


# Use primitive polynomial x^8 + x^4 + x^3 + x^2 + 1
class GFGenerator:
    def __init__(self, primitive_coefs: List, generator_coefs: List):
        self.prime_coefs = primitive_coefs
        self.gen_coefs = generator_coefs

        self.primitive = np.poly1d(self.prime_coefs)
        self.generator = np.poly1d(self.gen_coefs)
        self.exp_lut = np.zeros(256, dtype=int)

        self.log_lut = np.zeros(256)

        print(self.primitive)
        print(self.generator)

        self._compute_exp_lut()
        self._compute_log_lut()

    def __str__(self):
        return str(self.primitive)

    def _compute_exp_lut(self):
        current_polynom = np.poly1d([1])
        for i in range(256):

            if i == 0:
                self.exp_lut[i] = 1
            else:
                tmp = np.polymul(current_polynom, self.generator)
                if tmp.order == 8:
                    current_polynom = tmp + self.primitive
                else:
                    current_polynom = tmp
                tmp_coefs = current_polynom.c
                current_polynom = np.poly1d(tmp_coefs % 2)
                self.exp_lut[i] = int(current_polynom(2))

    def _compute_log_lut(self):
        for i in range(256):
            if i == 0:
                self.log_lut[i] = np.nan
            else:
                self.log_lut[i] = np.where(self.exp_lut == i)[0][0]

    def mul(self, u, v):
        if u > 255 or u < 0:
            raise ValueError("u unbound")
        if v > 255 or v < 0:
            raise ValueError("v unbound")

        if u == 0 or v == 0:
            return 0
        log_u = int(self.log_lut[u])
        log_v = int(self.log_lut[v])
        exp = (log_u + log_v) % 255
        return self.exp_lut[exp]

    def add(self, u, v):
        return u ^ v

    def div(self, u, v):
        # u / v =  u * inv(v)
        if v == 0:
            raise ValueError("divider is zero")
        if u == 0:
            return 0
        log_u = int(self.log_lut[u])
        log_v = int(self.log_lut[v])
        inv_log_v = 255 - log_v
        exp = (log_u + inv_log_v) % 255
        return self.exp_lut[exp]


if __name__ == "__main__":
    # from high power to low power, x8 + x4 + x3 + x + 1
    # coefs = [1, 0, 0, 0, 1, 1, 0, 1, 1]
    # gen = [1, 1]  # x + 1
    coefs = [1, 0, 0, 0, 1, 1, 1, 0, 1]
    gen = [1, 0]  # x + 1
    gf = GFGenerator(coefs, gen)

    print(gf.exp_lut)
    print(gf.log_lut)
