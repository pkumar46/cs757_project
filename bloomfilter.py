# Python 3 program to build Bloom Filter
# Install mmh3 and bitarray 3rd party module first
# pip install mmh3
# pip install bitarray
import math
import mmh3
from bitarray import bitarray

class BloomFilter(object):

    '''
    Class for Bloom filter, using murmur3 hash function
    '''

    def __init__(self, bitarray_size,items_count, num_hash):

        # Size of bit array to use
        self.size = bitarray_size

        # number of hash functions to use
        self.hash_count = num_hash

        # Bit array of given size
        self.bit_array = [bitarray(self.size),bitarray(self.size),bitarray(self.size),bitarray(self.size)]

        # initialize all bits as 0
        for i in range(4):
            self.bit_array[i].setall(0)

    def add(self, address, corenum):

        fusebits = []
        for i in range(self.hash_count):
            fusebits.append((hash(address) + i * mmh3.hash(address,i-1)) % self.size)
            # set the bit True in bit_array
            self.bit_array[corenum][(hash(address) + i * mmh3.hash(address,i-1)) % self.size] = True

    def lookup(self, address, corenum):

        for i in range(self.hash_count):
            if self.bit_array[corenum][(hash(address) + i * mmh3.hash(address,i-1)) % self.size] == False:
                return False
        return True


    @classmethod
    def get_hash_count(self, bitarray_size, num_of_addresses):
        k = (bitarray_size/num_of_addresses) * math.log(2)
        return int(k)
