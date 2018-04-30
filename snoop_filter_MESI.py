import os, errno
import csv
import re
import sys
from bloomfilter import BloomFilter
from random import shuffle

ignores = [0, 0, 0, 0]
# ignore = 0
last_time = 0
depth = 128
b = 1024  # size of bitarray
n = 20  # number of items to add
h = 1  # number of hash functions
total_snoop = 0
cacheline = 0
is_something_to_process = 0
number_of_filtered_tag_coparisons_bf = 0
number_of_filtered_tag_coparisons_el = 0
num_of_false_positive_snoop_bf = 0
num_of_false_positive_snoop_el = 0
real_snoops_required_bf = 0
real_snoops_required_el = 0
bloomf = BloomFilter(b, n, h)
print("Size of bit array:{}".format(bloomf.size))
print("bit array:{}".format(bloomf.bit_array))
print("Number of hash functions:{}".format(bloomf.hash_count))
tran_state = [{}, {}, {}, {}]
eviction_list = [[],[],[],[]]
core = 4
state = [{}, {}, {}, {}]
valid_cacheline = [{}, {}, {}, {}]
valid_state = {'M', 'E', 'S'}
invalid_state = {'NP', 'I'}
stable_state = {'M', 'E', 'S', 'NP', 'I'}
# sizeofAB = int(sys.argv[2])
# for i in range(4):
#    for j in range(sizeofAB):
#        core[i][j] = []
#        core[i][j].append(0)
#        core[i][j].append(None)

index = 0


def snoop_request(snoop_cacheline, this_corenum):
    global real_snoops_required_bf
    global num_of_false_positive_snoop_bf
    global real_snoops_required_el
    global num_of_false_positive_snoop_el
    global number_of_filtered_tag_coparisons_bf
    global number_of_filtered_tag_coparisons_el
    all_but_this = [0, 1, 2, 3]
    all_but_this.pop(this_corenum)
    #print(all_but_this)
    #print("snoop_cacheline:" + str(snoop_cacheline))
    #print("bit array:{}".format(bloomf.bit_array))

    # Bloom Filter lookup for all the other cores
    for i in all_but_this:
        if bloomf.lookup(snoop_cacheline, i):
            #print(i)
            #print(tran_state[i][snoop_cacheline])
            if (tran_state[i][snoop_cacheline][2] in invalid_state):
                #print("'{}' is a false positive!".format(snoop_cacheline))
                num_of_false_positive_snoop_bf = num_of_false_positive_snoop_bf + 1
            else:
                #print("'{}' is present!".format(snoop_cacheline))
                real_snoops_required_bf = real_snoops_required_bf + 1
        else:
            #print("'{}' is definitely not present!".format(snoop_cacheline))
            number_of_filtered_tag_coparisons_bf = number_of_filtered_tag_coparisons_bf + 1
    #Eviction list lookup
    for i in all_but_this:
        if snoop_cacheline in eviction_list[i]:
            #print("'{}' is definitely not present!".format(snoop_cacheline))
            number_of_filtered_tag_coparisons_el = number_of_filtered_tag_coparisons_el + 1
        else:
            if (tran_state[i][snoop_cacheline][2] not in invalid_state):
                #print("'{}' is a false positive!".format(snoop_cacheline))
                real_snoops_required_el = real_snoops_required_el + 1
            else:
                num_of_false_positive_snoop_el = num_of_false_positive_snoop_el + 1



def process_if_necessary():
    global total_snoop
    global is_something_to_process
    # push a cachline to private cache and update corresponding bloom filter
    # for i in core[this_corenum][cacheline]:
    for i in range(core):
        for cachelinep in tran_state[i]:
            if (tran_state[i][cachelinep][0] == '1') and (tran_state[i][cachelinep][3] != 'IFETCH'):
                #Update the Per-core Eviction list
                if (tran_state[i][cachelinep][1] in valid_state) and (tran_state[i][cachelinep][2] in invalid_state):
                    #print("Line" + str(cachelinep) + " got evicted!!")
                    if len(eviction_list[i]) < depth:
                        eviction_list[i].append(cachelinep)
                    elif len(eviction_list[i]) == depth:
                        eviction_list[i].pop(0)
                        eviction_list[i].append(cachelinep)
                if (tran_state[i][cachelinep][1] in invalid_state) and (tran_state[i][cachelinep][2] in valid_state) and (cachelinep in  eviction_list[i]):
                    #print("Line" + str(cachelinep) + " became valid!! Removing from eviction list")
                    eviction_list[i].remove(cachelinep)

                if (tran_state[i][cachelinep][1] in invalid_state) and (tran_state[i][cachelinep][2] in valid_state):
                    bloomf.add(cachelinep, i)
                    # Snoop broadcasted so initiates Other core's BF lookup
                    total_snoop = total_snoop + 3
                    snoop_request(cachelinep, i)

                if (tran_state[i][cachelinep][1] in ['E', 'M']) and (tran_state[i][cachelinep][2] in invalid_state):
                    # Snoop broadcasted so initiates Other core's BF lookup
                    total_snoop = total_snoop + 3
                    snoop_request(cachelinep, i)

                if (tran_state[i][cachelinep][1] in ['M']) and (tran_state[i][cachelinep][2] in ['S']):
                    # Snoop broadcasted so initiates Other core's BF lookup
                    total_snoop = total_snoop + 3
                    snoop_request(cachelinep, i)

                if (tran_state[i][cachelinep][1] in ['S']) and (tran_state[i][cachelinep][2] in ['M']):
                    # Snoop broadcasted so initiates Other core's BF lookup
                    total_snoop = total_snoop + 3
                    snoop_request(cachelinep, i)
            tran_state[i][cachelinep][0] = '0'


def add_to_ds(i):
    if i > 0:
        print("valid_cache:" + str(i) + '----' + str(valid_cacheline))
        print("tran" + str(i) + '----' + str(tran_state))


with open(sys.argv[1]) as f:
    for line in f:
        # m = re.search("(\d)[ ]+(Seq|L1Cache)[ ]+(\S+)[ ]+(\S+)?>(\S+)?[ ]+\S+[ ]+line (0x[0123456789abcdefABCDEF]+)\][ ]?(\S+)?.*", line)
        m = re.search(
            "(\d+).*(\d)[ ]+(Seq|L1Cache)[ ]+(\S+)[ ]+(\S+)?>(\S+)?[ ]+\S+[ ]+line (0x[0123456789abcdefABCDEF]+)\][ ]?(\S+)?.*",
            line)
        if m:
            time = m.group(1)
            corenum = int(m.group(2))
            unit = m.group(3)
            cmd_rec = m.group(4)
            state_tran_from = m.group(5)
            state_tran_to = m.group(6)
            cacheline = m.group(7)
            inst = m.group(8)
            this_corenum = corenum
            print(line)
            # print(str(corenum) + unit + cmd_rec + str(state_tran_from) + str(state_tran_to) + cacheline + str(inst))
            if cmd_rec == 'Begin':
                for i in range(core):
                    tran_state[i][cacheline] = ['0', '0', '0', inst]
                process_if_necessary()

                if inst == 'IFETCH':
                    ignores[corenum] = 1
                else:
                    ignores[corenum] = 0
                # Start processing this line
                if ignores[corenum] == 0:
                    add_to_ds(-1)
            elif cmd_rec == 'Done':
                if ignores[corenum] == 0:
                    add_to_ds(-2)
                last_time = time
                cacheline_old = cacheline
            else:
                #print(tran_state[corenum][cacheline])
                if state_tran_from in stable_state:
                    tran_state[corenum][cacheline][1] = state_tran_from
                if state_tran_to in stable_state:
                    tran_state[corenum][cacheline][2] = state_tran_to
                    tran_state[corenum][cacheline][0] = '1'
                is_last_line_Done = 0
                add_to_ds(-3)
            #print(core)
            #print(total_snoop)
            #print(num_of_false_positive_snoop)
            #print(real_snoops_required)

print("total_snoop: " + str(total_snoop))
print("real_snoops_required_bf: " + str(real_snoops_required_bf))
print("real_snoops_required_el: " + str(real_snoops_required_el))
print("num_of_false_positive_snoop_bf: " + str(num_of_false_positive_snoop_bf))
print("num_of_false_positive_snoop_el: " + str(num_of_false_positive_snoop_el))
print("number_of_filtered_tag_coparisons_bf: " + str(number_of_filtered_tag_coparisons_bf))
print("number_of_filtered_tag_coparisons_el: " + str(number_of_filtered_tag_coparisons_el))

# print("bit array:{}".format(bloomf.bit_array))
