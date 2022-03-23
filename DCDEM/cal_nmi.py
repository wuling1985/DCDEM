import numpy as np
import os
if __name__ =="__main__":
    os.chdir("Output/groundTruth")
    # optV = 0
    # optE = 0
    # optU = 0
    # for u in range(2, 10):
    #     for epson in np.arange(0.1, 0.5, 0.05):
    # # for u in [5,6]:
    # #     for epson in np.arange(0.540, 0.550, 0.001):
    #         cmd ="mutual3 expand.t04.comm result4-{:.2f}-{}.txt".format(epson,u)
    #         v=float(os.popen(cmd).read().split()[-1])
    #         print("{}-{:.2f}:{}".format(u,epson,v))
    #         if v > optV:
    #             optV=v
    #             optE = epson
    #             optU = u
    # print("{}-{}-{:.2f}".format(optV,optU,optE))
    # os.chdir("Input/S-on")
    # t=5
    for k in [1,2,3,4,5,6,7]:
        cmd = "mutual3 expand.t0{}.comm GreMod_community_{}.txt".format(k, k)
        v = float(os.popen(cmd).read().split()[-1])
        print("{}".format(v))