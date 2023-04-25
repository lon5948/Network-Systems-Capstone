## Overview
Using QUIC’s headers and frame structure to implement the following functions with a UDP socket.

- Error control
- Flow control
- Congestion control

## Error Control
- Since UDP is an unreliable transport protocol, you must perform your own error control.
- Set a timer for each packet; if the recipient doesn’t respond with an ACK in time, the packet should be retransmitted.
- Re-order the packets before passing them to the application layer, as the received packets may be out of order.

## Flow Control
- Make sure that the faster sender does not overwhelm the slower receiver.
- At the connection setup stage, both sides should negotiate the maximum size of each side’s receiving window, then use the maximum remote receiving window size as its maximum sending window size.

## Congestion Control
- You can use the TCP new Reno algorithm to implement the congestion control.
- use tc to test if your QUIC program can adapt its sending rate to the available bandwidth when you use tc to change the available bandwidth.

## TEST
To test the function, you can try the following tc command:
```
sudo tc qdisc show dev lo
sudo tc qdisc add dev lo root netem loss 5%
sudo tc qdisc change dev lo root netem rate 10Mbit
sudo tc qdisc del dev lo root netem rate 10Mbit
```