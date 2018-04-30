import os, errno
import csv
import re
import sys

#number of cores = 4
total_loc = 0
total_mem = 0
final_avg = 0
core = [{},{},{},{}]
localitycount = [0,0,0,0]
ratio = [0,0,0,0]
meminstcount = [0,0,0,0]
depth = int(sys.argv[2])
with open(sys.argv[1]) as f:
    for line in f:
        m = re.search("(\d)        Seq.*line (0x[0123456789abcdefABCDEF]+)\] [LS].* PC (\d+) (0x[0123456789abcdefABCDEF]+)", line)
        if m:
            meminstcount[int(m.group(1))] = meminstcount[int(m.group(1))] + 1
            corenum = int(m.group(1))
            #print(m.group(1) + "  " + m.group(2) + "  " + m.group(4))
            if (m.group(4) in core[corenum]) and (m.group(2) in core[corenum][m.group(4)]):
                localitycount[int(m.group(1))] = localitycount[int(m.group(1))] + 1
                #print("match")
                #print(core)
            if m.group(4) in core[corenum]:
                if (len(core[corenum][m.group(4)]) < depth):
                    # append the new number to the existing array at this slot
                    core[corenum][m.group(4)].append(m.group(2))
                    #print("depth was less")
                    #print(core)
                elif len(core[corenum][m.group(4)]) == depth:
                    core[corenum][m.group(4)].pop(0)
                    core[corenum][m.group(4)].append(m.group(2))
                    #print("depth was equal")
                    #print(core)

            else:
                # create a new array in this slot
                core[corenum][m.group(4)] = [m.group(2)]
                #print("first entry")
                #print(core)

#print(pc)
print("locality: " + str(localitycount))
print("meminstcount: " + str(meminstcount))
for i in range(4):
    if(meminstcount[i] != 0):
        total_loc = total_loc + localitycount[i]
        total_mem = total_mem + meminstcount[i]
final_avg = total_loc/total_mem


print("final_avg: " + str(final_avg))
'''
with open(filename, 'a') as myfile:
         wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
              wr.writerow(dataitem_list)
'''
