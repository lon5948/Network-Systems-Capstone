## Overview
Design and implement a simulation program to study the channel efficiency of the Aloha, 
Slotted Aloha, CSMA, and CSMA/CD protocols under different operation conditions.

## Methods

### Aloha
- All hosts can send packets at any time.
- If a host does not receive an acknowledgement, it considers that a collision has occurred.
- If a collision occurs, the host waits for a random time to retransmit.  

![](https://github.com/lon5948/Network-Systems-Capstone/blob/main/hw3/aloha.jpg)

### Slotted Aloha
- All host can send packets at and only at the beginning of each time slot.
- If a host does not receive an acknowledgement, it considers that a collision has occurred.
- If a collision occurs, the host decides whether to retransmit with probability p at the beginning of each following slot.      

![](https://github.com/lon5948/Network-Systems-Capstone/blob/main/hw3/slotted.jpg)

### CSMA
- All hosts detect if someone else is sending before starting to send.  
  - non-persistent: If someone is sending, the host waits for a random time and detects again. (We adopt this method.)
  - 1-persistent: If someone is sending, the host keeps detecting until it finds that no one is sending.
- If a host does not receive an acknowledgement, it considers that a collision has occurred.
- If a collision occurs, the host waits for a random time to retransmit.

### CSMA/CD
- All hosts detect if someone else is sending before starting to send.
  - non-persistent: If someone is sending, the host waits for a random time and detects again. (We adopt this method.)
  - 1-persistent: If someone is sending, the host keeps detecting until it finds that no one is sending.
- If a host does not receive an acknowledgement, it considers that a collision has occurred…
- If a collision occurs, the host waits for a random time to retransmit.
- The host detects collisions during transmission and aborts the transmission if a collision is detected.

### CSMA and CSMA/CD with Link Delay
![](https://github.com/lon5948/Network-Systems-Capstone/blob/main/hw3/link_delay.jpg)

## Performance Metrics
![](https://github.com/lon5948/Network-Systems-Capstone/blob/main/hw3/performance_metric.jpg)

