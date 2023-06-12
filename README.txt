Reed solomon is used for error corrections and erasures. According to application domain , it comes with 
different constaints like message length for storage.
For Telecom It uses for example GF(2^8), and is mainly for error correction than erasure.
In fact ECC RS cand handle both of errors and erasures but has a theoritic limit of correction.
And for Nand memories we prefer BCH codes where we operate in GF(2)
Storage: RS Vandermonde uses matrix to encode, decode messages, however this has a cost of O(n^3)
and could be used only for small matrixes.

The optimial coding / decoding uses following standards

Encoding : could be done with matrix or LFSR ( Linear feedback shift register)
And uses gnerator polynomial g(x).

Encoding computes parity to add to message and [message + parity ] is a codeword.

To explain basically the theory, codewords are a subspace of all possible messages.
And the particulariy of codeword c(x) is that  c(x) is divisible by g(x).
When small number of errors occurs we are not far from a codeword in term of hamming distance
and this allows to recover from errors.


Decoding is done in follwoing steps:

1) Syndromes calculus
2) Error locator polynom using Berlekamp-Massey or Euclide algorithmi, algorithm operates in max (2t steps) 
   where t is the decoding error capacity
3) Chien search to locate errors positions, errors are inverse of roots of locator polynom.
4) Forney algorithm to compute error magnitude


Current implementation of liberasure for RS_VAND
Matrix based to describe in details

possible implementation using Berlekamp
Ths implemntation could use a thread pool, this pool is started at init and wait for tasks to perform.
One task is taking input data to decode and perform complete decoding cycle for errors or erasures


