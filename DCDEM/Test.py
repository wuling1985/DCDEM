from edge import edge
from collections import deque
from copy import deepcopy
from collections import defaultdict
import numpy as np


def Create_Graph(file):
    Edges = {}
    Vetexs = {}
    with open(file, 'r') as f:
        for line in f:
            node1, node2 = line.strip().split()
            if int(node1) == int(node2):
                print("remove self edge :{}-{}".format(node1, node2))
                continue
            e = edge(node1, node2)
            Edges["{0}->{1}".format(e.getNode1(), e.getNode2())] = e
            Vetexs.setdefault(e.getNode1(), set(e.getNodes())).add(e.getNode2())
            Vetexs.setdefault(e.getNode2(), set(e.getNodes())).add(e.getNode1())

    Adj = deepcopy(Vetexs)
    for k, v in Adj.items():
        v.remove(k)
    return Edges, Vetexs, Adj


def similarity(v1, v2, Vetexs):
    s1 = (Vetexs[v1] & Vetexs[v2])
    s2 = (Vetexs[v1] | Vetexs[v2])
    return (len(s1) / len(s2))


def get_Neighbor(e, Edges, Vetexs):
    V1, V2 = e.getNode1(), e.getNode2()
    N1 = set()
    N2 = set()
    for v1, v2 in [(V1, v) for v in Vetexs[V1] if ((v != V2) and (v != V1))]:
        if v1 < v2:
            N1.add(Edges["{0}->{1}".format(v1, v2)])
        else:
            N1.add(Edges["{0}->{1}".format(v2, v1)])
    for v1, v2 in [(V2, v) for v in Vetexs[V2] if ((v != V1) and (v != V2))]:
        if v1 < v2:
            N2.add(Edges["{0}->{1}".format(v1, v2)])
        else:
            N2.add(Edges["{0}->{1}".format(v2, v1)])
    return N1, N2


def get_Neigbborsize(e, Vetexs):
    v1 = e.getNode1()
    v2 = e.getNode2()
    return len(Vetexs[v1]) + len(Vetexs[v2]) - 2


def get_Neighborlinks(e, epson, Edges, Vetexs):
    v1, v2 = e.getNodes()
    N = [(v1, v) for v in Vetexs[v1] if ((v != v2) and (v != v1) and (similarity(v, v2, Vetexs) >= epson))] + \
        [(v2, v) for v in Vetexs[v2] if ((v != v1) and (v != v2) and (similarity(v, v1, Vetexs) >= epson))]
    N2 = set()
    for v1, v2 in N:
        if v1 < v2:
            N2.add(Edges["{0}->{1}".format(v1, v2)])
        else:
            N2.add(Edges["{0}->{1}".format(v2, v1)])
    return N2


def updateEgelabel(l, id):
    if id in l.label.keys():
        l.label[id] = l.label[id] + 1
    else:
        l.label[id] = 1


def borderProcess(CLSet, BLSet):
    for e in BLSet:
        s = sorted(e.label.items(), key=lambda x: x[1], reverse=False)
        CLSet[s[0][0]].append(e)
        e.classfied = True
        e.id = s[0][0]


def outlierProcess(CLSet, OLSet, E, V):
    # 排序以下：
    for e, _ in sorted([(e, get_Neigbborsize(e, V)) for e in OLSet], key=lambda x: x[1], reverse=True, ):
        # print("outlier {}".format(e))
        N1, N2 = get_Neighbor(e, E, V)
        # print("v1:{}".format(len(N1)))
        # print("v2:{}".format(len(N2)))
        v1 = False
        v1_id = None
        for e1 in N1:
            # N1 中的边如果都是有一条已经有社区归属，那么v1这个点就已经有社区归属了。
            # print(e)
            if e1.classfied == True:
                v1_id = e1.id
                v1 = True
                break
        # print("v1相连的边其他边是否已有社区归属:{}-{}".format(v1,v1_id))
        v2 = False
        v2_id = None
        for e2 in N2:
            # print(e)
            # N1 中的边如果都是有一条已经有社区归属，那么v1这个点就已经有社区归属了。
            if e2.classfied == True:
                v2 = True
                v2_id = e2.id
                break
        # print("v2相连的邻边是否已有社区归属:{}-{}".format(v2,v2_id))
        if v1 == False and v2 == False:
            # 把v1 和 v2 以及与之相连的outlierlink 单独划分成一个社区。
            # print("initate a new community from outlier links")
            cur_id = len(CLSet)
            newset = []
            e.classfied = True
            e.id = cur_id
            newset.append(e)
            for e in N1 | N2:
                e.id = cur_id
                e.classfied = True
                newset.append(e)
            CLSet.append(newset)
            continue
        if v1 == False and v2 == True:
            # 把v1与v2这条边加到v2的邻居社区中：可以加到与v2中最后的社区
            e.classfied = True
            e.id = v2_id
            CLSet[v2_id].append(e)
            # print("将v1加到与v2相同的社区")
            continue
        if v1 == True and v2 == False:
            # 把v2这条边加到v1的邻居社区中：可以加到与v2中最后的社区
            e.classfied = True
            e.id = v1_id
            CLSet[v1_id].append(e)
            # print("将v2加到与v1相同的社区")
            continue


def formCommunity(LinkSets):
    # 将核心的边社区集转化为结点社区
    CS = []
    for ls in LinkSets:
        cs = []
        for e in ls:
            cs.append(e.getNode1())
            cs.append(e.getNode2())
        cs = set(cs)
        CS.append(cs)
    return CS


def writetofile(CS, outputfile):
    with open(outputfile, "w") as f:
        for cs in CS:
            for id in cs:
                f.write(str(id))
                f.write(" ")
            f.write("\n")


def cal_EQ(cover, G):
    vertex_community = defaultdict(lambda: set())
    for i, c in enumerate(cover):
        for v in c:
            vertex_community[v].add(i)
    m = 0.0
    for v, neighbors in G.items():
        for n in neighbors:
            if v > n:
                m += 1
    total = 0.0
    for c in cover:
        for i in c:
            o_i = len(vertex_community[i])
            k_i = len(G[i])
            for j in c:
                o_j = len(vertex_community[j])
                k_j = len(G[j])
                if i > j:
                    continue
                t = 0.0
                if j in G[i]:
                    t += 1.0 / (o_i * o_j)
                t -= k_i * k_j / (2 * m * o_i * o_j)
                if i == j:
                    total += t
                else:
                    total += 2 * t
    return round(total / (2 * m), 4)


if __name__ == "__main__":
    optMod = 0.0
    optU = -1
    optEpson = 0.0
    for epson in np.arange(0.3, 0.6, 0.05):
        for u in np.arange(8, 9, 1):
            infile = "Input/real network/polblog.txt"
            E, V, adj = Create_Graph(infile)
            CLSet = []
            BLSet = []
            OLSet = []
            id = 0  # 边社区编号
            for e in E.values():
                if e.classfied == False and e.border == False and e.IsOutlier == False:
                    if len(get_Neighborlinks(e, epson, E, V)) >= u:
                        e.classfied = True
                        e.id = id
                        # 以该边为中心扩展，形成核心边社区。
                        CL = []
                        CL.append(e)
                        Q = deque()
                        Q.append(e)
                        while len(Q) != 0:
                            e = Q.popleft()
                            R = get_Neighborlinks(e, epson, E, V)
                            for l in R:
                                # 不访问已经分类过的核心边
                                if l.classfied == False:
                                    if l.IsOutlier == True:
                                        l.IsOutlier = False
                                        l.border = True
                                        updateEgelabel(l, id)
                                        continue
                                    if l.border == True:
                                        updateEgelabel(l, id)
                                        continue
                                    if len(get_Neighborlinks(l, epson, E, V)) >= u:
                                        l.classfied = True
                                        l.id = id
                                        CL.append(l)
                                        Q.append(l)
                                    else:
                                        l.border = True
                                        updateEgelabel(l, id)
                        CLSet.append(CL)
                        id = id + 1
                    else:
                        e.IsOutlier = True
            # extract border links into BLset
            for e in E.values():
                if e.border == True:
                    BLSet.append(e)
            # extract noise links into OLset
            for e in E.values():
                if e.IsOutlier == True:
                    OLSet.append(e)
            # stept2: 对噪声边进行处理
            borderProcess(CLSet, BLSet)
            # STEP3: 噪声边处理
            outlierProcess(CLSet, OLSet, E, V)
            CS = formCommunity(CLSet)
            curMod = cal_EQ(CS, adj)
            if curMod > optMod:
                optMod = curMod
                optEpson = epson
                optU = u
    print("optMod:{}({:.3f}-{})".format(optMod, optEpson, optU))
