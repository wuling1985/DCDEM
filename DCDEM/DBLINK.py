from collections import deque
from edge import edge
import numpy as np
import time

def Create_Graph(file):
   print("Inite the Graph from :{}".format(file))
   Edges=set()
   Vetexs={}
   with open(file,'r') as f:
       for line in f:
           node1,node2=line.split()
           if int(node1) == int(node2):
               print("remove self edge {} - {}".format(node1,node2))
               continue
           e=edge(node1,node2)
           Edges.add(e)
           #包括自身
           Vetexs.setdefault(e.getNode1(), set(e.getNodes())).add(e.getNode2())
           Vetexs.setdefault(e.getNode2(), set(e.getNodes())).add(e.getNode1())
       E2={}
       for e in Edges:
           E2["{0}->{1}".format(e.getNode1(),e.getNode2())]=e
   print("nodes :{}".format(len(Vetexs)))
   print("edges :{}".format(len(E2)))
   print("avg k:{}".format(len(E2)/len(Vetexs)))
   return E2,Vetexs

def similarity(v1,v2,Vetexs):
    s1=(Vetexs[v1] & Vetexs[v2])
    s2=(Vetexs[v1]| Vetexs[v2])
    return (len(s1) / len(s2))

def get_Neighborlinks(e,epson,Edges,Vetexs):
    v1,v2=e.getNodes()
    N = [(v1, v) for v in Vetexs[v1] if ((v != v2)and(v!=v1) and (similarity(v, v2,Vetexs)>=epson))] + \
        [(v2, v) for v in Vetexs[v2] if ((v != v1)and(v!=v2) and (similarity(v, v1,Vetexs)>=epson))]
    N2=set()
    for v1,v2 in N:
        if v1 < v2:
            N2.add(Edges["{0}->{1}".format(v1,v2)])
        else:
            N2.add(Edges["{0}->{1}".format(v2,v1)])
    return N2

def originDBLink(file1,file2 ,u, epson):

    E, V = Create_Graph(file1)
    LCS = []
    CS = []

    for e in E.values():

        if e.visited == False:

            if len(get_Neighborlinks(e, epson, E, V)) >= u:
                e.visited = True
                LC = set()
                LC.add(e)
                Q = deque()
                Q.append(e)
                while len(Q) != 0:
                    e = Q.popleft()
                    R = get_Neighborlinks(e, epson, E, V)
                    for l in R:
                        if l.visited ==  True:
                            if l.IsOutlier == True:
                                l.IsOutlier=False
                                LC.add(l)
                        else:
                            if len(get_Neighborlinks(l, epson, E, V)) >= u:
                                l.visited =True
                                LC.add(l)
                                Q.append(l)
                            else:
                                l.visited=True
                                LC.add(l)
                LCS.append(LC)

            else:
                e.IsOutlier = True
                e.visited = True


    for ls in LCS:
        cs = set()
        for e in ls:
            cs.add(e.getNode1())
            cs.add(e.getNode2())
        CS.append(cs)

    with open(file2, "w") as f:
        for cs in CS:
            for id in cs:
                f.write(str(id))
                f.write(" ")
            f.write("\n")

if __name__ =="__main__":

    infile = "Input/real network/karate.txt"


    for u in [5]:
        for epson in [0.3]:
    #         output = "C:/Users/hanming/Desktop/modclac/modcalc/data/community_u{}_epson{:.2f}.txt".format(u, epson)
    #         #output="Output/karate/DBLINK/community_u{}_epson{:.3f}.txt".format(u, epson)
    #         # output = "Output/temp/community_u{}_epson{:.2f}.txt".format(u, epson)
            output="Output/temp/community1_u{}_epson{:.2f}.txt".format(u, epson)
            start=time.clock()
            originDBLink(infile, output, u, epson)
            end=time.clock()
            print(end-start)
    # originDBLink(infile,4, 0.4)
    # Create_Graph(infile)
    # print(E)
    # print(V)
    # print(get_Neighborlinks(E["0->1"],0.4,E,V))