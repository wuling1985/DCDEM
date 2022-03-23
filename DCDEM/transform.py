
if __name__ == "__main__":

    for k in range(60,101):
        filename = "Input/as733/as_t{}.txt".format(k)
        with open(filename, "r") as f:
            X = [(line.split()[0],line.split()[1]) for line in f.readlines() if not line.startswith("#")]
        with open("C:/Users/hanming/Desktop/GreMod/as733/as_inc_{}.txt".format(k-59), "w") as f:
            for x in X:
                 f.write(x[0])
                 f.write("\t")
                 f.write(x[1])
                 f.write("\n")
