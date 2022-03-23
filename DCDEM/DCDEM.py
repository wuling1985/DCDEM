from edge import edge
from collections import deque
import numpy as np
from CalEQ import cal_EQ
from copy import deepcopy
from time import  time

def Create_Graph(file):
    print("Inite the Graph from :{}".format(file))
    Edges = set();
    Vetexs = {}
    V = set()
    with open(file, 'r') as f:
        for line in f:
            if line.startswith("#"):
                continue
            node1, node2 = line.strip().split()
            if int(node1) == int(node2):
                # print("remove self edge :{}-{}".format(node1, node2))
                continue
            V.add(int(node1))
            V.add(int(node2))
            e = edge(node1, node2)
            Edges.add(e)
            Vetexs.setdefault(e.getNode1(), set()).add(e.getNode2())
            Vetexs.setdefault(e.getNode2(), set()).add(e.getNode1())
        E2 = {}
        for e in Edges:
            E2["{0}->{1}".format(e.getNode1(), e.getNode2())] = e
    return E2, Vetexs, V


def similarity(v1, v2, Vetexs):
    s1 = (Vetexs[v1] & Vetexs[v2])
    s2 = (Vetexs[v1] | Vetexs[v2])
    return (len(s1) / len(s2))


def similarity2(v1, v2, adjMat, E):
    '''
    计算邻边之间的相似度
    :param v1: 其中一条边的节点
    :param v2: 另一条边的节点
    :param Vetexs: 网络的邻接矩阵，用于获取邻居信息
    :param E: 边集
    :return: 相似度值
    '''
    total = 0
    for v in adjMat[v1]:
        if v > v1:
            total += E["{}->{}".format(v1, v)].weight
        else:
            total += E["{}->{}".format(v, v1)].weight
    for v in adjMat[v2]:
        if v > v2:
            total += E["{}->{}".format(v2, v)].weight
        else:
            total += E["{}->{}".format(v, v2)].weight

    insec = 0
    for v in (adjMat[v1] & adjMat[v2]):
        if v > v1:
            insec += E["{}->{}".format(v1, v)].weight
        else:
            insec += E["{}->{}".format(v, v1)].weight
        if v > v2:
            insec += E["{}->{}".format(v2, v)].weight
        else:
            insec += E["{}->{}".format(v, v2)].weight

    return (insec / total)


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
    return len(Vetexs[v1]) + len(Vetexs[v2]) - 1


def get_Neighborlinks(e, epson, Edges, Vetexs):
    v1, v2 = e.getNodes()
    N = [(v1, v) for v in Vetexs[v1] if ((v != v2) and (v != v1) and (similarity2(v, v2, Vetexs, Edges) >= epson))] + \
        [(v2, v) for v in Vetexs[v2] if ((v != v1) and (v != v2) and (similarity2(v, v1, Vetexs, Edges) >= epson))]
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


def borderProcessVersion2(CLSet, BLSet):
    for e in BLSet:
        for k, v in e.label.items():
            e.label[k] = v / len(CLSet[k])
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
    CS2 = {}
    for id, ls in enumerate(LinkSets):
        cs = set()
        for e in ls:
            cs.update(e.getNodes())
            CS2.setdefault(e.getNode1(), set()).add(id)
            CS2.setdefault(e.getNode2(), set()).add(id)
        CS.append(cs)
    return CS, CS2


def writetofile(CS, outputfile):
    with open(outputfile, "w") as f:
        for cs in CS:
            for id in cs:
                f.write(str(id))
                f.write(" ")
            f.write("\n")


def excute(E, V, epson, u):
    CLSet = []
    BLSet = []
    OLSet = []
    id = 0  # 边社区编号
    for e in E.values():
        if e.classfied == False and e.border == False and e.IsOutlier == False:
            if len(get_Neighborlinks(e, epson, E, V)) >= u:
                # 该边是核心边，对边属性赋值
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
    # print("step2:border processing:")
    # stept2: 对噪声边进行处理
    # borderProcess(CLSet, BLSet)
    borderProcess(CLSet, BLSet)
    # print("step:outlier processing:")
    # STEP3: 噪声边处理
    outlierProcess(CLSet, OLSet, E, V)

    CS, CS2 = formCommunity(CLSet)
    # mod = cal_EQ(CS, V)
    return -1, CS, CS2


def calStrSim(v1, v2, lastComStru):
    s1 = lastComStru.get(v1, None)
    s2 = lastComStru.get(v2, None)
    if s1 is not None and s2 is not None:
        return len(s1 & s2) / len(s1 | s2)
    else:
        return 0


def evoMat(currentEdges, lastEdges, lastComStru, beta=0.5):
    for id, e in currentEdges.items():
        v1, v2 = [int(v) for v in id.split("->")]
        gamma = calStrSim(v1, v2, lastComStru)
        if id in lastEdges.keys():
            e.weight = e.weight * (1 - beta) + beta * (lastEdges[id].weight + gamma)
        else:
            e.weight = e.weight * (1 - beta) + beta * (0 + gamma)


if __name__ == "__main__":
    # infile = "Input/dynamic/enron_t8.txt"
    # optmod = 0
    # optepscon = 0
    # optu = 0
    # optCS = -1
    # for u in range(2, 10):
    #     for epson in np.arange(0, 0.5, 0.01):
    #         outputfile = "Output/dynamic/community_u{}_epson{:.2f}.txt".format(u, epson)
    #         mod, CS = excute(infile, epson, u)
    #         if mod > optmod:
    #             optmod = mod
    #             optepscon = epson
    #             optu = u
    #             optCS = CS
    # writetofile(CS, outputfile)
    # print("best mod:{}-{}-{}".format(optmod, optepscon, optu))
    # optmod = 0
    # optepson = 0
    # optu = 0
    # optCS = -1

    # 执行初始时刻的网络，获得当前时刻的社区结构
    # 用于寻找最好的初始时刻网络结构
    # for u in range(8, 12):
    #     for epson in np.arange(0.6, 0.7, 0.02):
    #         E, V, total_V = Create_Graph("Input/as733/as_t60.txt")
    #         mod, CS, _ = excute(E, V, epson,u)
    #         print("{}-{:.2f}-{}".format(u,epson,mod))
    #         # writetofile(CS, "Output/groundTruth/result4-{:.2f}-{}.txt".format(epson, u))

    beta = 0.5
    lastComStru = None  # 用于保存前一个时刻的社区结构
    lastEdges = None  # 用于保存前一时刻的边集
    t1 = time()
    E, V, total_V = Create_Graph("Input/as733/as_t60.txt")
    lastEdges = deepcopy(E)

    mod1, _, lastComStru = excute(E, V, 0.6, 9)
    t2 = time()
    print("1:{}".format(t2-t1))
    # print("{}:{}".format(60,mod1))
    for T in range(61, 101):
        for u in [5]:
            for epson in [0.3]:
                file = "Input/as733/as_t{}.txt".format(T)
                start = time()
                curEdges, curAdjMat, V = Create_Graph(file)
                tempEdges = deepcopy(curEdges)
                evoMat(tempEdges, lastEdges, lastComStru, beta)
                mod2, curCS, curStru = excute(tempEdges, curAdjMat, epson, u)
                end = time()
                print("{}:{}".format(T,(end - start)))
                # print("{}:{}".format(T,mod2))
                # writetofile(curCS, "Output/groundTruth/result{}-{:.2f}-{}.txt".format(T, epson, u))
                lastComStru = curStru
                lastEdges = curEdges



