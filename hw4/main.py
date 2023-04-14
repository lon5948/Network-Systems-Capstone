class router:
    def __init__(self, id, cost):
        self.id = id
        self.cost = cost
        self.min_cost = cost
        self.visited = list()
        self.send = list()
        self.receive = list()
        self.neighbor = list()
    def add_neighbor(self, n):
        self.neighbor.append(n)
    def flood(self, src):
        self.receive.append(src)
        self.visited.append(src)

def set_topology(link_cost: list):
    global routers
    N = len(link_cost)
    routers = list()
    for i in range(N):
        routers.append(router(i, link_cost[i]))
        routers[i].visited.append(i)
        routers[i].send.append(i)
    for i in range(N):    
        for j in range(N):
            if link_cost[i][j] > 0 and link_cost[i][j] < 999:
                routers[i].add_neighbor(routers[j])
#-> tuple[list, list]
def run_ospf(link_cost: list):
    N = len(link_cost)
    flag = True
    log = list()
    # flooding
    while flag:
        flag = False
        round_log = list()
        for i in range(N):
            for s in routers[i].send:
                for n in routers[i].neighbor:
                    if s not in n.visited:
                        n.flood(s)
                        round_log.append((i, s, n.id))
                        flag = True
        for i in range(N):
            routers[i].send = routers[i].receive.copy()
            routers[i].receive.clear()
        round_log = sorted(round_log)
        log.extend(round_log)
    # min cost
    min_cost_list = list()
    for i in range(N):
        trace = list()
        visited_r = [i]
        target = i
        while True: 
            for n in routers[target].neighbor:
                if n.id not in visited_r:
                    if routers[i].min_cost[target] + link_cost[target][n.id] < routers[i].min_cost[n.id]:
                        routers[i].min_cost[n.id] = routers[i].min_cost[target] + link_cost[target][n.id]                   
                    trace.append((routers[target].min_cost[n.id], n.id))
            trace = sorted(trace)
            while len(trace) > 0 and trace[0][1] in visited_r:
                trace.remove(trace[0])
            if len(trace) > 0:
                target = trace[0][1]
                trace.remove(trace[0])
                visited_r.append(target)
            else:
                break
        min_cost_list.append(routers[i].min_cost)
    return (min_cost_list, log)
            

        

'''
def run_rip(link_cost: list) -> tuple[list, list]:
    pass
'''
def main(link_cost: list):
    set_topology(link_cost)
    print('OSPF:\n', run_ospf(link_cost))
    #print('RIP:\n', run_rip(link_cost))
    pass
    

if __name__ == '__main__':
    
    link_cost = [
                    [  0,   2,   5,   1, 999, 999],
                    [  2,   0,   3,   2, 999, 999],
                    [  5,   3,   0,   3,   1,   5],
                    [  1,   2,   3,   0,   1, 999],
                    [999, 999,   1,   1,   0,   2],
                    [999, 999,   5, 999,   2,   0]
                ]
    
    main(link_cost)

