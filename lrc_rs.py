"""
"""
import numpy as np
from typing import List

from gf import GFGenerator


class lrc_rs:
    """
    k : message length
    n : codeword length
    in other literature work we define rs(n, k) where n is codeword length
    and k is message length.
    """

    def __init__(self, n, k, l, r, root_powers: List):
        if n < k:
            raise ValueError("invalid config")

        # from high power to low power, x8 + x4 + x3 + x2 + 1
        self.gf_prim = [1, 0, 0, 0, 1, 1, 1, 0, 1]
        self.gf_gen = [1, 0]  # x
        self.gf = GFGenerator(self.gf_prim, self.gf_gen)
        self.k = k
        self.m = n - k
        self.n = n
        self.l = l
        self.r = r
        self.root_powers = root_powers
        self.gx = self._init_gx()
        self.vand_matrix = []

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

        main_parity = self.m -2 

        # LFSR
        state = [0] * (main_parity)
        mult = [0] * (main_parity)
        print(f"rs gx: %s m %d", self.gx, self.m)

        subgroup_size = self.k // self.l


        parity_0 = 0 
        parity_1 = 0
        for i in range(self.k):
            feedback = self.gf.add(m_x[i], state[main_parity - 1])
            # compute local parities
            if i < subgroup_size:
                parity_1 = self.gf.add(parity_1, m_x[i])
            else:
                parity_0 = self.gf.add(parity_0, m_x[i])

            for j in range(main_parity):
                mult[j] = self.gf.mul(self.gx[j], feedback)
            for j in reversed(range(main_parity)):
                if j == 0:
                    state[j] = mult[j]
                else:
                    state[j] = self.gf.add(state[j - 1], mult[j])

            print('rs state ', state)

        reverse = state[::-1]
        # overwrite last element or parity with two local parities
        #first_global_parity = reverse.pop()
        #print("poped parity:", first_global_parity)
        print("appended local parities", parity_0, parity_1)
        
        reverse.append(parity_1)
        reverse.append(parity_0)

        # check
        """
        tmp = 0
        for el in reverse:
            tmp = self.gf.add(tmp , el)

        if tmp != first_global_parity:
            raise ValueError("check here:", tmp, first_global_parity)
        """
        return m_x + reverse


    def _split_message(self, message: List):
        """
        split message of k elements into l groups
        if self.k is not a multiple of self.l , this will lead to groups of
        different size.
        the last group has the highest size
        in a general manner l would b 2
        """
        subgroup_size = self.k // self.l
        return message[0:subgroup_size], message[subgroup_size:]

    def _decode_local_parity(self, pos_group, decoded_msg, pos_local_first, erasure_pos):
        pos0 = pos_group.copy()
        #print("pos_local_first:", pos_local_first , decoded_msg)
        pos0.append(pos_local_first)
        common = set(erasure_pos).intersection(set(pos0))
        common = list(common)
        print("common group 0:", common, erasure_pos,pos0, pos_group)
        val = 0
        local_err_pos = None
        if len(common) == 0:
            return None, 0, []
        if len(common) == 1:
            self.local_decode_used = True
            local_err_pos = common[0]
            for el in pos0:
               if el in common:
                   continue
               val = self.gf.add(val, decoded_msg[el])
            #decoded_msg[local_err_pos] = val   
        return local_err_pos, val, common

    def decode_lrc(self, msg, erasure_pos: List[int]):
        decoded_msg = [0] * self.n
        repaired = 0

        if len(erasure_pos) > self.l + self.r:
            raise ValueError(f"cant decode high number of errors {len(erasure_pos)}")
        print(msg, decoded_msg)
        for i in range(self.n):
            decoded_msg[i] = msg[i]

        #message format
        #[k data] , P1 , P2 , PX , PY
        for pos in erasure_pos:
            if pos >= self.n or pos < 0:
                raise ValueError("Invalid positions")

        group0, group1 = self._split_message(msg[:self.k])

        pos_group0 = [i for i in range(0, len(group0))]
        pos_group1 = [i for i in range(len(group0), self.k)]

        pos_global = [i for i in range(self.k, self.n-2)]

        pos_local_first = self.n-2
        pos_local_second = self.n-1

        remain_pos = erasure_pos.copy()
        print('erasure_pos:', erasure_pos)
        # handle local parity px
        # check first if recover from local parities
        pos, val, common0 = self._decode_local_parity(pos_group0, decoded_msg, pos_local_first, erasure_pos)
        print("laa pos, val", pos, val, common0)
        if pos is not None:
            repaired = repaired + 1
            decoded_msg[pos] = val
            remain_pos.remove(pos)
        """
        elif val is None:
            print("can't recovr only from parity")
        else:
            print("No error to fix")
        """
            
        print("dec message after local parity", decoded_msg)
        # handle local parity px
        #check first if recover from local parities
        pos, val, common1 = self._decode_local_parity(pos_group1, decoded_msg, pos_local_second, erasure_pos)
        if pos is not None:
            repaired = repaired + 1
            decoded_msg[pos] = val
            remain_pos.remove(pos)
        """
        else:
            print("can't recovr only from parity") 
        """
        # prepare matrix for decoding remaining errors
        # remaining error >= 2, otherwise we recover from parity
        # so let's use local parities and global parities

        # can't recover in following conditions:
        if len(common0) > self.r+1:
            raise ValueError("cant recover, ")

        if len(common1) > self.r+1:
            raise ValueError("cant recover, ")
        
        # At this stage there are two remaining errors
        

        print("laa remain:", common0, common1, remain_pos)
        self._decode_remain(decoded_msg, common0, common1, repaired, remain_pos)

        return decoded_msg


    def _compute_syndroms(self, msg):
        """
        compute syndroms for received message
        """
        if len(msg) != self.n:
            raise ValueError()
        print("message:", bytes(msg))
        # init syndroms
        syndroms = [0] * self.m
        for j in range(self.m):
            for i in range(self.n):
                #print("indexes: ", j , i , msg[i], self.vand_matrix[j][self.n - 1 - i], self.vand_matrix[j][self.n - 1 - i])
                syndroms[j] = self.gf.add(
                    syndroms[j], self.gf.mul(msg[i], self.vand_matrix[j][self.n - 1 -i])
                )

        print("syndroms:", syndroms)
        return syndroms

    def _compute_matrix(self, msg):

        # Matrix*
        self.vand_matrix = []
        print("vand_matrix:", self.vand_matrix)

        group0, group1 = self._split_message(msg[:self.k])

        pos_group0 = [i for i in range(0, len(group0))]
        pos_group1 = [i for i in range(len(group0), self.k)]
        
        pos_global = [i for i in range(self.k, self.n-2)]

        pos_local_first = self.n-2
        pos_local_second = self.n-1

        vec_parity = [0] * self.n
        parity_index = 1
        vec_parity[parity_index] = 1
        for i in range(len(msg)):
            if i < len(pos_group0):
                vec_parity[self.n - 1 -i] = 1

        global_to_use =  0
        print("laa vec_parity 0:", vec_parity)
        # add local parities equations

        self.vand_matrix.append(vec_parity)

        vec_parity = [0] * self.n
        parity_index = 0
        vec_parity[parity_index] = 1
        for i in range(len(msg)):
            if i >= len(pos_group0) and i < len(pos_group0) + len(pos_group1):
                vec_parity[self.n - 1 -i] = 1
       
        print("laa vec_parity 1:", vec_parity)

        self.vand_matrix.append(vec_parity)
        
        for j in range(self.m - self.l):
            row = []
            for i in range(self.n):
                if i  < self.l:
                    pow = 0
                    val = None
                else:
                    pow = (self.root_powers[j] * (i-1)) % 255
                    val = self.gf.exp_lut[pow]
                #print("j, i, pow", j, i , pow)
                """
                if i >= self.l and i < (self.l + self.r):
                    #tmp =  self.gf.add(self.gf.exp_lut[pow], 1)
                    tmp = self.gf.exp_lut[pow]
                    row.append(tmp)
                else:    
                    row.append(self.gf.exp_lut[pow])
                """
                if val is None:
                    row.append(0)
                else:
                    row.append(val)

            self.vand_matrix.append(row)
        
        print("vand_matrix:", self.vand_matrix)
        return self.vand_matrix



    def _decode_remain(self, msg, common0, common1, repaired, remain_pos: List[int]):
        """ """
        # Ref design, defines decode a Vandermonde like  matrixes
        # Vandermonde :  M(x) * err(x) = S(x)


        #syndroms = self._compute_syndroms(msg)
        #print("syndroms:", syndroms)

        # Matrix

        matrix = self._compute_matrix(msg)

        synds = self._compute_syndroms(msg)
        errors = sum(synds)
        print("errors:", errors)
        if errors == 0:
            print("syndroms to zeros")
            return remain_pos, synds
        
        matrix_decode = []
        global_to_use = 0

        synds_to_use = []

        if (len(common0) >= 2):
            row = [matrix[0][self.n - 1 -c] for c in remain_pos]
            matrix_decode.append(row)
            global_to_use = global_to_use + 1
            synds_to_use.append(synds[0])

        if (len(common1) >= 2):
            row = [matrix[1][self.n - 1 -c] for c in remain_pos]
            matrix_decode.append(row)
            global_to_use = global_to_use + 1
            synds_to_use.append(synds[1])

        for j in range(len(remain_pos)- global_to_use):
            row = [matrix[j+2][self.n - 1 -c] for c in remain_pos]
            matrix_decode.append(row)
            synds_to_use.append(synds[j+2])


        print("matrix_decode:", matrix_decode)
        print("remain_pos:", remain_pos)
        print("synds_to_use:", synds_to_use)
        print("global_to_use:", global_to_use)
    
        # Matrix inversion, we call this Vandermonde as we obtain a
        # Vandermonde Matrix, which is reversible
        nb_errors = len(remain_pos)
        synds = synds_to_use
        # Jordan/Gauss
        inv_vand_matrix = []
        for i in range(nb_errors):
            inv_vand_matrix.append(matrix_decode[i].copy())

        for i in range(nb_errors):
            print('i', i, inv_vand_matrix)
            row = inv_vand_matrix[i].copy()
            # normalize
            row_norm = [0] * nb_errors
            print("row:", row)
            if row[i] == 0:
                for u in range(nb_errors):
                    if inv_vand_matrix[u][i] != 0:
                        for v in range(nb_errors):
                            row[v] = self.gf.add(row[v], inv_vand_matrix[u][v])
                        synds[i] = self.gf.add(synds[i], synds[u])
                        break
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
                print('norm:', i, j, norm, inv_vand_matrix)
                for k in range(nb_errors):
                    # print("row:", row[k], row[i])
                    inv_vand_matrix[i][k] = self.gf.div(inv_vand_matrix[i][k], norm)
                print("nom inv matrix:", inv_vand_matrix)
                synds[i] = self.gf.div(synds[i], norm)

                if inv_vand_matrix[j][i] != 0:
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

        inv_vand_matrix, synds

        return
    
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
