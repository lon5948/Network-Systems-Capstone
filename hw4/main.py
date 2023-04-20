def run_ospf(link_cost: list):
    N = len(link_cost)
    flag = True
    log = list()
    receive = [[] for i in range(N)]
    send = [[i] for i in range(N)]
    visited = [[i] for i in range(N)]
    neighbors = [[j for j in range(N) if link_cost[i][j] > 0 and link_cost[i][j] < 999] for i in range(N)]
    # flooding
    while flag:
        flag = False
        round_log = list()
        for i in range(N):
            for s in send[i]:
                for n in neighbors[i]:
                    if s not in visited[n]:
                        receive[n].append(s)
                        visited[n].append(s)
                        round_log.append((i, s, n))
                        flag = True
        for i in range(N):
            send[i] = receive[i].copy()
            receive[i].clear()
        round_log = sorted(round_log)
        log.extend(round_log)
    # min cost
    min_cost = [link_cost[i].copy() for i in range(N)]
    for i in range(N):
        trace = list()
        visited_r = [i]
        target = i
        while True: 
            for n in neighbors[target]:
                if n not in visited_r:
                    if min_cost[i][target] + link_cost[target][n] < min_cost[i][n]:
                        min_cost[i][n] = min_cost[i][target] + link_cost[target][n]                   
                    trace.append((min_cost[i][n], n))
            trace = sorted(trace)
            while len(trace) > 0 and trace[0][1] in visited_r:
                trace.remove(trace[0])
            if len(trace) > 0:
                target = trace[0][1]
                trace.remove(trace[0])
                visited_r.append(target)
            else:
                break
    return (min_cost, log)


def run_rip(link_cost: list):
    N = len(link_cost)
    log = list()
    min_cost = [link_cost[i].copy() for i in range(N)]
    change = [True for i in range(N)]
    flag = True
    neighbors = [[j for j in range(N) if link_cost[i][j] > 0 and link_cost[i][j] < 999] for i in range(N)]    
    while flag:
        flag = False
        for i in range(N):
            if change[i]:
                change[i] = False
                for n in neighbors[i]:
                    log.append((i, n))
        temp = [min_cost[i].copy() for i in range(N)]
        for i in range(N):
            for n in neighbors[i]:
                for j in range(N):
                    if link_cost[n][i] + temp[i][j] < temp[n][j]:
                        min_cost[n][j] = link_cost[n][i] + temp[i][j]
                        change[n] = True
                        flag = True
    return (min_cost, log)


def main(link_cost: list):
    print('OSPF:\n', run_ospf(link_cost))
    print('-------------------------------------------')
    print('RIP:\n', run_rip(link_cost))
    

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

