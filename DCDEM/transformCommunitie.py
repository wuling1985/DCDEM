if __name__ == "__main__":

    for om in range(1,8):
        communities = {}
        with open("Input/artificial network/Sv/community_{}.dat".format(om),"r") as f:
            for line in f:
                v = line.strip().split()[0]
                coo = line.strip().split()[1:]
                for co in coo:
                    if co in communities.keys():
                        communities[co].add(v)
                    else:
                        communities[co] = set(v)
        with open("Input/artificial network/Sv/community_{}.txt".format(om),"w") as f:
            for Vs in communities.values():
                for id in Vs:
                    f.write(str(id))
                    f.write(" ")
                f.write("\n")