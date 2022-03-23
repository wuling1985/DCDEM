from collections import defaultdict
from collections import deque
from edge import edge
import copy
import numpy as np
import time
from math import exp


def create_Graph(file):
    # print("Inite the Graph from :{}".format(file))
    Edges = {}
    Vetexs = {}
    with open(file, 'r') as f:
        for line in f:
            node1, node2 = line.strip().split()
            if int(node1) == int(node2):
                print("remove selfEdge {} - {}".format(node1, node2))
                continue
            e = edge(node1, node2)
            Edges["{0}->{1}".format(e.getNode1(), e.getNode2())] = e
            # 包括自身
            Vetexs.setdefault(e.getNode1(), set(e.getNodes())).add(e.getNode2())
            Vetexs.setdefault(e.getNode2(), set(e.getNodes())).add(e.getNode1())
    Adj = copy.deepcopy(Vetexs)
    for k, v in Adj.items():
        v.remove(k)
    return Edges, Vetexs, Adj


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
    return N1 | N2


def sim(v1, v2, Vetexs, E, alpha=0.8):
    s1 = list(Vetexs[v1] & Vetexs[v2])
    s2 = (Vetexs[v1] | Vetexs[v2])
    sim1 = (len(s1) / len(s2))
    nums_of_edges = sum([1 for v1 in s1 for v2 in s1 if v1 < v2 and "{0}->{1}".format(v1, v2) in E.keys()])
    sims = (2 * nums_of_edges) / (len(s1) * (len(s1)))
    sim3 = alpha * sim1 + (1 - alpha) * sims
    return exp(sim3) / (1 + exp(sim3))


def sim2(e1, e2, V, E, alpha=0.8):
    S1 = set(e1.getNodes()) & set(e2.getNodes())
    # print("S1:{}".format(S1))
    if len(S1) == 0:
        return 0
    else:
        v1 = [v for v in e1.getNodes() if v not in S1][0]
        v2 = [v for v in e2.getNodes() if v not in S1][0]
        # print("v1:{},v2:{}".format(v1,v2))
        s1 = list(V[v1] & V[v2])
        s2 = (V[v1] | V[v2])
        sim1 = (len(s1) / len(s2))
        nums_of_edges = sum([1 for v1 in s1 for v2 in s1 if v1 < v2 and "{0}->{1}".format(v1, v2) in E.keys()])
        sim2 = (2 * nums_of_edges) / (len(s1) * (len(s1)))
        sim3 = alpha * sim1 + (1 - alpha) * sim2
        return exp(sim3) / (1+sim3)


def get_Neighborlinks(e, epson, Edges, Vetexs):
    v1, v2 = e.getNodes()
    N = [(v1, v) for v in Vetexs[v1] if ((v != v2) and (v != v1) and (sim(v, v2, Vetexs, Edges) >= epson))] + \
        [(v2, v) for v in Vetexs[v2] if ((v != v1) and (v != v2) and (sim(v, v1, Vetexs, Edges) >= epson))]
    N2 = set()
    for v1, v2 in N:
        if v1 < v2:
            N2.add(Edges["{0}->{1}".format(v1, v2)])
        else:
            N2.add(Edges["{0}->{1}".format(v2, v1)])
    return N2


def expand(E, V, epson, u):
    CLS = []
    BLS = []
    id = 0  # 边社区编号
    for e in E.values():
        if e.visited == False:
            if len(get_Neighborlinks(e, epson, E, V)) >= u:
                # print("核心边:{}".format(e))
                e.visited = True
                e.classfied = True
                e.core = True
                e.id = id
                CL = [e]
                Q = deque()
                Q.append(e)
                while len(Q) != 0:
                    e = Q.popleft()
                    R = get_Neighborlinks(e, epson, E, V)
                    for l in R:
                        # 只对未划分的边进行处理
                        if l.classfied == False:
                            if l.visited == True:
                                if l.IsOutlier == True:
                                    l.IsOutlier = False
                                    l.border = True
                            else:
                                if len(get_Neighborlinks(e, epson, E, V)) >= u:
                                    l.classfied = True
                                    l.core = True
                                    l.id = id
                                    l.visited = True
                                    CL.append(l)
                                    Q.append(l)
                                else:
                                    l.border = True
                                    l.visited = True
                CLS.append(CL)
                id += 1
            else:
                e.visited = True
                e.IsOutlier = True
                # print("noise edge {}".format(e))
    for e in E.values():
        if e.border == True:
            BLS.append(e)
    return CLS, BLS

def updating_Strategy(CLS, BLS, epson, V, E):
    for e in BLS:
        dt = {}  # {id:[core edges connected with e ]}
        for m, n, v in [(l.id, l, sim2(l, e, V, E)) for l in get_Neighbor(e, E, V) if l.core == True]:
            dt.setdefault(m, []).append(v)
        # print(dt)
        ID = list(dt.keys())
        if len(ID) == 1:
            # print("该边只属于一个社区")
            e.classfied = True
            e.id = ID[0]
        else:
            max = epson
            tempId = ID[0]
            for i, vs in dt.items():
                for v in vs:
                    if v > max:
                        max = v
                        tempId = i
            # print("id:{},max:{}".format(tempId, max))
            # print("将{}加入{}社区".format(e, tempId))
            CLS[tempId].append(e)
    return CLS


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
    optCS = None
    infile = "Input/real network/CA-GrQc.txt"
    for u in np.arange(3,4,1):
        for epson in np.arange(0.52,0.59,0.01):
            print("create graph from file :{}".format(infile))
            E, V, adj = create_Graph(infile)
            print("stage1: detect core linksets and border linksets...")
            CLS, BLS = expand(E, V, epson, u)
            print("stage2: excuting border link updating...")
            LS = updating_Strategy(CLS, BLS, epson, V, E)
            print("stage3: generating community structrue...")
            CS = formCommunity(CLS)
            curMod = cal_EQ(CS, adj)
            print("curMod:{} ({}-{:.3f})".format(curMod,u,epson))
            if curMod > optMod:
                optU = u
                optEpson = epson
                optMod = curMod
                optCS = CS
    print("optMod:{}({:.3f}-{})".format(optMod,optEpson,optU))
    writetofile(optCS,"Output/Temp/CA-GrQc_comm.txt")