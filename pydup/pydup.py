# coding=utf-8

"""This is an initial implementation of LSH following the post from eventbrite.com blog

https://engineering.eventbrite.com/multi-index-locality-sensitive-hashing-for-fun-and-profit/

"""

from __future__ import division

import re
import hashlib
import struct
import math

from collections import defaultdict

repeated_char_pattern = re.compile(r"(.)\1{1,}", re.DOTALL)


def tokenize_sentence(sentence):
    for word in sentence.split(' '):
        # for full in nltk.tokenize.sent_tokenize(sentence):
        # for word in nltk.tokenize.word_tokenize(full):
        word = word.lower()
        word = _replace_repeated_chars(word)
        word = word.strip('\'"!?,.')
        yield word


def _replace_repeated_chars(sentence):
    """look for 2 or more repetitions of character and replace with the character
    itself

    """
    return repeated_char_pattern.sub(r"\1\1", sentence)


def _minHash_similarity(hashesA, hashesB, N):
    """ Check how many of the hashes in the two groups are equal, that means the same token
    was found in the two sentences

        A higher result, more similarity between sentences

        O(N M^2)
    """
    count = 0
    count = sum(1 for i in range(N) if hashesA[i] == hashesB[i])

    return count/N


def _hamming_distance(bitsA, bitsB, N):
    """Hamming distance returns the number of equals bits"""
    X = bin( bitsA ^ bitsB)[2:]
    X = X.zfill(N)  # pad with leading zero to match the N bits
    count = 0

    return sum(1 for i in range(N) if int(X[i]) == 1)


def _generate_hash(seed, token):
    """ Calculate the hash given a seed plus token, then the digest is unpacked
    and converted to int, the final hash is just 4 from the first 4 chars of the digest. Any
    consistent hashing function should be enough

        :returns: Integer of the partial digest
    """
    return struct.unpack(
        'i', hashlib.md5(u'{0}${1}'.format(seed, token).encode('utf-8')).digest()[0:4])[0]


def minHash(tokens, N):
    """ For each token, will generate N hashes, then get the minimal ones
    and returns it.

    """
    final_hashes = list()

    for seed in range(N):
        hash_list = [_generate_hash(seed, token) for token in tokens]
        final_hashes.append(min(hash_list))
    return final_hashes


def bitsimilarity(bitsA, bitsB, N):
    """Returns the percent of similarity (using Hamming distance)

       O(M^2)

    """
    distance = _hamming_distance(bitsA, bitsB)
    similarity = 1 - distance / N
    return similarity


def bitsampling(hashes, N):
    """ Instead of storing the minHash, we can do better just storing the least significant bit
    of each hash

        returns a bit vector with the least significat bits
    """
    bits = 0

    for i in range(N):
        bits = (bits << 1) | (hashes[i] & 1)

    return bits


def split_chunks(bits, chunk_size):
    """Split the bitvector in groups of bits

        :param bits: bitvector
        :param chunk_size: number of bits per each chunk
    """
    # pad to left with zero to match the chunk multiple bits
    size = len(bin(bits)[2:])
    bit_vector = bin(bits << (size % chunk_size))[2:]
    chunks = []
    for i in range(0, size, chunk_size):
        chunks.append(int(bit_vector[i:i+chunk_size], 2))
    return chunks


def generate_close_chunks(chunk):
    """Generates close chunks, numbers with one bit difference with original chunk

        returns list of chunks

    """
    size = len(bin(chunk)[2:])
    close_chunks = []
    for i in range(size):
        # apply a XOR operations with a zero-vector with just one bit as 1, the bit is
        # moved each iteration
        close_chunks.append(chunk ^ (1 << i))
    close_chunks.append(chunk)
    return close_chunks


class LSHTable(object):
    def __init__(self, hash_iter=32, radius=4):
        """
            :param hash_iter: the number of different hashes to be generated per token (chosen empirically),
                also represents the bitvector length
            :param radius: number of unequal bits to match two bitvectors

        """
        self._hash_iter = hash_iter
        self._radius = radius
        self._chunk_size = hash_iter // self._radius

        # initialize an empty table
        self._table = [defaultdict(list) for i in range(math.ceil(self._hash_iter / self._chunk_size))]

    def bitvector_from_tokens(self, tokens):
        hashes = minHash(tokens, N=self._hash_iter)  # minimal hashes generated in each iteration
        return bitsampling(hashes, N=self._hash_iter)  # take the less significant bit of each hash

    def add(self, bitvector):
        chunks = split_chunks(bitvector, self._chunk_size)
        for i, c in enumerate(chunks):
            if not chunks[i] in self._table[i]:
                self._table[i][chunks[i]].append(bitvector)

    def lookup(self, bitvector):
        chunks = split_chunks(bitvector, self._chunk_size)
        matches = []
        for i, chunk in enumerate(chunks):
            close_chunks = generate_close_chunks(chunk)
            for close in close_chunks:
                if close in self._table[i]:
                    matches.extend(self._table[i][close])
        return matches
