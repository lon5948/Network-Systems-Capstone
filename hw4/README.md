## Overview
Given a topology graph and the costs of every links, your program should compute the shortest path 
results by using RIP and OSPF, respectively. You need to provide source code and slides to explain 
how you implement these protocols.

## OSPF
For OSPF, each node needs to flood its link state to all other nodes in the network, and this should be implemented by the flooding algorithm. 
For a node, it is not allowed to send its link state directly to each of other nodes.  

The return type is tuple, and the first element of the tuple is the path cost (each list is for a router). 
The second element contains the logs showing how a router sends a link state to another router. Each element is a tuple. 

## RIP
For RIP, each node will send its distance vector to all of its neighbors.   

The return type is tuple, and the first element of the tuple is the path cost (each list is for a router). The second element contains the logs showing how a router sends messages to another router. Each element is a tuple.

## Test Data
Below are some test data and their answers
```
testdata = [ 
    [0, 4, 1, 999], 
    [4, 0, 2, 999], 
    [1, 2, 0, 3], 
    [999, 999, 3, 0]
]
```
```
ans_ospf = (
     [[0, 3, 1, 4], 
      [3, 0, 2, 5], 
      [1, 2, 0, 3], 
      [4, 5, 3, 0]], 

     [(0, 0, 1), (0, 0, 2), (1, 1, 0), 
      (1, 1, 2), (2, 2, 0), (2, 2, 1), 
      (2, 2, 3), (3, 3, 2), (2, 0, 3), 
      (2, 1, 3), (2, 3, 0), (2, 3, 1)]
)
```
```
ans_rip = (
     [[0, 3, 1, 4], 
      [3, 0, 2, 5], 
      [1, 2, 0, 3], 
      [4, 5, 3, 0]], 
     
     [(0, 1), (0, 2), (1, 0), 
      (1, 2), (2, 0), (2, 1), 
      (2, 3), (3, 2), (0, 1), 
      (0, 2), (1, 0), (1, 2), 
      (3, 2)]
)
```

