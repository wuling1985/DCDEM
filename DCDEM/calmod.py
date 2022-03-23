from CalEQ import cal_EQ

if __name__ == "__main__":


    print("start")
    for t in range(1,42):
        file = "C:/Users/hanming/Desktop/GreMod/as733/as_inc_{}.txt".format(t)
        adj = {}
        with open(file,"r") as f:
            for line in f.readlines():
                v1,v2 = line.split()
                adj.setdefault(v1, set()).add(v2)
                adj.setdefault(v2, set()).add(v1)
        commfile = "C:/Users/hanming/Desktop/GreMod/as733/GreMod_community_{}.txt".format(t)
        comm = []
        with open(commfile,"r") as f:
            for line in f.readlines():
                comm.append(line.split())

        mod = cal_EQ(comm,adj)

        print(mod)