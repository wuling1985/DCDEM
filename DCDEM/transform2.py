

if __name__ == "__main__":
    with open("as.txt","r") as f:
        for line in f.readlines():
            for x in line.split(","):
                print(x)
