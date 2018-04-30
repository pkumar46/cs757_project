import os, errno
import csv
import re
import sys

core = [{},{},{},{}]
sizeofAB = int(sys.argv[2])
#for i in range(4):
#    for j in range(sizeofAB):
#        core[i][j] = []
#        core[i][j].append(0)
#        core[i][j].append(None)
per_right = 0
per_wrong = 0
per_wrong = 0
total_did_not_predict = 0
num_of_right_prediction = [0,0,0,0]
num_of_wrong_prediction = [0,0,0,0]
total_num_of_mem_inst = [0,0,0,0]
index = 0
with open(sys.argv[1]) as f:
    for line in f:
        m = re.search("(\d)        Seq.*line (0x[0123456789abcdefABCDEF]+)\] [LS].* PC (\d+) (0x[0123456789abcdefABCDEF]+)", line)
        if m:
            corenum = int(m.group(1))
            index = (int(m.group(4),0))%sizeofAB
            if index in core[corenum]:
                if core[corenum][index][1] == m.group(2):
                    if core[corenum][index][0]>=2:
                        #print("Was predicted and predicted right: core " + str(corenum))
                        num_of_right_prediction[corenum] = num_of_right_prediction[corenum] + 1
                        if core[corenum][index][0]!=3:
                            core[corenum][index][0] = core[corenum][index][0] + 1
                    else:
                        #print("Was not predicted1: core " + str(corenum))
                        if core[corenum][index][0]!=3:
                            core[corenum][index][0] = core[corenum][index][0] + 1
                else:
                    if core[corenum][index][0]>=2:
                        #print("Was predicted and predicted wrong: core " + str(corenum))
                        num_of_wrong_prediction[corenum] = num_of_wrong_prediction[corenum] + 1
                        if core[corenum][index][0]!=0:
                            core[corenum][index][0] = core[corenum][index][0] - 1
                    else:
                        #print("Was not predicted2: core " + str(corenum))
                        if core[corenum][index][0]!=0:
                            core[corenum][index][0] = core[corenum][index][0] - 1
                    core[corenum][index][1] = m.group(2)
            else:
                core[corenum][index] = []
                core[corenum][index].append(0)
                core[corenum][index].append(m.group(2))
                #print("first entry: core " + str(corenum))
            total_num_of_mem_inst[corenum] = total_num_of_mem_inst[corenum] + 1


    for i in range(4):
        per_right = per_right + num_of_right_prediction[i]
        per_wrong = per_wrong + num_of_wrong_prediction[i]
        total_did_not_predict = total_did_not_predict + (total_num_of_mem_inst[i] - num_of_wrong_prediction[i] - num_of_right_prediction[i])
    print("num_of_right_prediction: " + str(num_of_right_prediction))
    print("num_of_wrong_prediction: " + str(num_of_wrong_prediction))
    print("total_num_of_mem_inst: " + str(total_num_of_mem_inst))
    print("per_right_prediction: " + str(per_right))
    print("per_wrong_prediction: " + str(per_wrong))
    print("total did not predict: " + str(total_did_not_predict))
