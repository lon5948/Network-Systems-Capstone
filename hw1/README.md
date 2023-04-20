## Overview
For this homework assignment, you need to write a C++ program that captures live network packets and prints some information in the packet, similar to what the tcpdump utility does.
cification

## pcap
### Environment (ubuntu 18.04)
- sudo apt-get install libpcap-dev
- g++ main.o -o main -lpcap (linking the object file with the libraries)

### User manual
- Function
  -  pcap_findalldevs
  - pcap_open_live
  - pcap_compile
  - pcap_setfilter
  - pcap_next
- Structure
  - pcap_if_t
  - pcap_t

## Program Arguments
Your program should correctly support the following arguments:
- --interface {interface}, -i {interface}
- --count {number}, -c {number}  
default = -1, which means that it will continuously capture packets until it is interrupted
- --filter {udp, tcp, icmp, all}, -f {udp, tcp, icmp, all}  
default = all  
It should correctly filter out UDP, TCP, and ICMP packets.

### Print Format
- Payload: You should print the first 16 bytes of the application data in the hexadecimal format.
If there is nothing in the payload, don’t print anything.
```
ASCII -> hex
a -> 61
b -> 62
1 -> 31
2 -> 32
a4bs5k1cdefg1257 -> 61 34 62 73 35 6B 31 63 64 65 66 67 31 32 35 37
```
- ICMP
```
Transport type: ICMP
Source IP: 10.0.0.1
Destination IP: 10.0.0.8
ICMP type value: 8
```
- TCP and UDP
```
Transport type: TCP (or UDP)
Source IP: 10.0.0.1
Destination IP: 10.0.0.2
Source port: 7777
Destination port: 8888
Payload: … (If there is no payload, don’t print anything)
```

### Testing Flow
We will compile your homework by simply typing ‘make’ in your homework directory, 
and run your program by typing `./main [argument] ...`
1. Compile  
`make`
2. Run your program (an example)  
- `./main --interface {interface} -c 3 --filter udp`
```
Transport type: UDP
Source IP: …
Destination IP: …
Source port: …
Destination port: …
Payload: …

Transport type: UDP
Source IP: …
Destination IP: …
Source port: …
Destination port: …
Payload: …

Transport type: UDP
Source IP: …
Destination IP: …
Source port: …
Destination port: …
Payload: …
```
- `./main`
```
wrong command
```
This error is caused because you did not specify the interface when running your program.
