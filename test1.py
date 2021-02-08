import networkx as nx
from gurobipy import *
#导入gurobi库
try:
    model = Model("mip1")
    #c=[[1,1,1],[1,1,1],[1,1,1]]
    #n = len(c)
    G = nx.random_geometric_graph(50,0.2)
    n = 50
    c = []
    for node in G.nodes():
        c.append([])
    for node in G.nodes():
        for n in G.nodes():
            c[node].append(0)
    for edge in G.edges():
        c[edge[0]][edge[1]] = 1
        c[edge[1]][edge[0]] = 1


    s = {}
    rs = {}
    rn = {}
    racl = {}
    for i in range(0,n):
        for x in range(0,50):
            name = 's_'+str(i)+'_'+str(x)
            s[i,x] = model.addVar(0,1,vtype = GRB.BINARY,name = name)
        for j in range(0,n):
            name = 'racl_'+str(i)+'_'+str(j)
            racl[i,j] = model.addVar(0,1,vtype = GRB.BINARY, name = name)
    for x in range(0,50):
        for y in range(0,50):
            name = 'rs_'+str(x)+'_'+str(y)
            rs[x,y] = model.addVar(0,1,vtype = GRB.BINARY,name = name)
        for i in range(0,n):
            name ='rn_'+str(x)+'_'+str(i)
            rn[x,i] = model.addVar(0,1,vtype = GRB.BINARY, name = name)

    srs = {}
    srssum = {}
    rnsrs = {}
    srnsrs = {}
    rnsrs_1 = {}
    s_1_1_rnsrs_acl = {}
    for x in range(0,50):
        for y in range(0,50):
            for j in range(0,n):
                name = 'srs_'+str(x)+'_'+str(y)+'_'+str(j)
                srs[x,y,j] = model.addVar(0,1,vtype = GRB.BINARY, name = name)
        for i in range(0,n):
            name = 'srssum_'+str(x)+'_'+str(i)
            srssum[x,i] = model.addVar(0,1,vtype = GRB.BINARY, name = name)

            name = 'rnsrs_'+str(x)+'_'+str(i)
            rnsrs[x,i] = model.addVar(0,2,vtype = GRB.INTEGER, name = name)

            name = 'rnsrs_1_' + str(x) +'_'+ str(i)
            rnsrs_1[x, i] = model.addVar(0, 1, vtype=GRB.BINARY, name=name)

    for i in range(0,n):
        for j in range(0,n):
            for x in range(0,50):
                name = 'srnsrs_' + str(i) + '_'+str(j)+'_'+str(x)
                srnsrs[i,j,x] = model.addVar(0, 2, vtype=GRB.INTEGER, name=name)

                name = 's_1_1_srnsrs_acl_' + str(i) +'_'+ str(j) +'_'+ str(x)
                s_1_1_rnsrs_acl[i, j, x] = model.addVar(-1, 1, vtype=GRB.INTEGER, name=name)


    obj = LinExpr(0)
    for x in range(0,50):
        for y in range(0,50):
            obj.addTerms(1,rs[x,y])
        for i in range(0,n):
            obj.addTerms(1,rn[x,i])

    model.setObjectiveN(obj, priority = 1, index = 0)
    obj.clear()

    obj = LinExpr(0)
    for i in range(0,n):
        for j in range(0,n):
            obj.addTerms(1,racl[i,j])
    model.setObjectiveN(obj,priority = 0, index = 1)

    for i in range(0,n):
        lhs = LinExpr(0)
        for x in range(0,50):
            lhs.addTerms(1,s[i,x])
        model.addConstr(lhs == 1, name = 'subnet_assign_'+str(i))

    #for x in range(0,50):
     #   model.addConstr(rs[x,x]==1, name = 'secugroup_rule_'+str(x))

    for x in range(0,50):
        for y in range(0,50):
            for j in range(0,n):
                model.addConstr(srs[x,y,j]>=s[j,y]+rs[x,y]-1)
                model.addConstr(srs[x,y,j]<=rs[x,y])
                model.addConstr(srs[x,y,j]<=s[j,y])
    for x in range(0,50):
        for j in range(0,n):
            lhs = LinExpr(0)
            for y in range(0,50):
                lhs.addTerms(1, srs[x,y,j])
            model.addConstr(srssum[x,j] == lhs)
            lhs.clear()
            model.addConstr(rnsrs[x, j] == rn[x,j]+srssum[x,j])
            model.addConstr(rnsrs_1[x, j] >= (1-rn[x, j]) + (1-srssum[x, j])-1)
            model.addConstr(rnsrs_1[x, j] <= (1 - rn[x, j]))
            model.addConstr(rnsrs_1[x, j] <= (1 - srssum[x, j]))
    for i in range(0,n):
        for j in range(0,n):
            for x in range(0,50):
                model.addConstr(srnsrs[i,j,x] <= 2*s[i,x])
                model.addConstr(srnsrs[i,j,x] <= rnsrs[x,j])
                model.addConstr(srnsrs[i,j,x]>=rnsrs[x,j]-2*(1-s[i,x]))

                model.addConstr(s_1_1_rnsrs_acl[i, j, x] <= 1-rnsrs_1[x,j]-racl[i,j])
                model.addConstr(s_1_1_rnsrs_acl[i, j, x] >= 1-rnsrs_1[x,j]-racl[i,j] -1 +s[i,x])
                model.addConstr(s_1_1_rnsrs_acl[i, j, x] >= -1*s[i,x])
                model.addConstr(s_1_1_rnsrs_acl[i, j, x] <= s[i,x])
    for i in range(0,n):
        for j in range(0,n):
            if i != j:
                lhs = LinExpr(0)
                lhs2 = LinExpr(0)
                for x in range(0, 50):
                    lhs.addTerms(1, srnsrs[i, j, x])
                    lhs2.addTerms(1, s_1_1_rnsrs_acl[i, j, x])
                model.addConstr(lhs >= c[i][j])
                model.addConstr(lhs2 == c[i][j])
                lhs.clear()
                lhs2.clear()

    model.optimize()
    for v in model.getVars():
        if(v.x==1):
            print(v.varName,v.x)




except GurobiError:
        print('Error reported')
