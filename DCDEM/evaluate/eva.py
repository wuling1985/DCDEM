import os
from collections import deque

def search(path):
    #先判断路径是否存在
    if os.path.exists(path):
        #转化为绝对路径
        if not os.path.isabs(path):
            path = os.path.abspath(path)
            print(path)
        if os.path.isfile(path):
            print(path)
        else:
            Q = deque()
            Q.append(path)
            while len(Q)!=0:
                p = Q.popleft()
                for subfile in os.listdir(p):
                    if os.path.isfile(os.path.join(p,subfile)):
                        print(os.path.join(p,subfile))
                    else:
                        Q.append(os.path.join(p,subfile))

if __name__ =="__main__":
    search("../Input")
