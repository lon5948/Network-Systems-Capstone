## Overview
For this homework, you are tasked with designing an interactive program that creates a virtual network, similar to what is done with Mininet.

In the program, you need to research and understand how switches populate their switch table entries and how hosts populate their ARP table entries so that packets can be properly forwarded to their destinations.

## Topology
8 hosts + 7 switches
The names of the hosts and switches may differ from those during the demonstration.
The red numbers in the topology map refer to the port numbers of those switches.  
  
![](https://github.com/lon5948/Network-Systems-Capstone/blob/main/hw2/topology.jpg)
- Import [setting.py](https://github.com/lon5948/Network-Systems-Capstone/blob/main/hw2/setting.py)
  - hosts
  - switches
  - links  

## Rules
For the command h1 ping h2, the following actions will occur:

- h1:
  - h1 will check if the IP of h2 is in its ARP table.
  - If it is, h1 will send an ICMP request to the MAC address of h2.
  - If not, h1 will broadcast an ARP request to all hosts by setting the destination MAC address to ‘ffff’. Switches will handle this.
  - After receiving an ARP reply from h2, h1 will update its ARP table and send an ICMP request to h2.

- h2:
  - After receiving an ARP request, h2 will update its ARP table and send an ARP reply to h1 since the destination IP matches its own IP.
  - After receiving an ICMP request, h2 will send an ICMP reply to h1.

- Other hosts:
  - After receiving an ARP/ICMP request, they will drop the request since the destination IP does not match their own IP, .

- Switch:
  - After receiving a packet, the switch will first update its MAC table with the source’s MAC address.
  - If the destination MAC address is ‘ffff’, the switch will recognize it as an ARP request and broadcast the packet.
  - Otherwise, the switch will check if the MAC address of h2 is in its MAC table.
  - If it is, the switch will send the packet on the specific port.
  - If not, the switch will flood the packet by sending it on every other port except the one it came from."

## Command
1. ping:  
e.g.
`h1 ping h2` (No need to print anything)  
2. show_table (for switches and hosts)  
    - show_table {host-name/switch-name}  
e.g.  
`show_table h1` (show arp table in h1)  
`show_table s1` (show mac table in s1)  
    - show_table {all_hosts/all_switches}  
`show_table all_hosts` (show all hosts’ arp table)  
`show_table all_switches` (show all switches’ arp table)  
3. clear:  
e.g.  
`clear h1` (clear arp table in h1)  
`clear s1` (clear mac table in s1)  
4. If the entered command is not “ping,” “show_table,” or “clear”  
print “a wrong command”  

## Print Format
- show_table {host_name}
  - First line: `ip : mac`
  - Then: `---------------{host_name}:`
  - Then print every entry in its ARP table in the format `h1ip : h1mac`
- show_table {switch_name}
  - First line: `mac : port`
  - Then: `---------------{switch_name}:`
  - Then print every entry in its MAC table in the format `h1mac : 0`

## Examples
- 4 hosts + 3 switches  
`python3 main.py`  
> show_table all_hosts
```
ip : mac
---------------h1:
---------------h2:
---------------h3:
---------------h4:
```
> show_table all_switches
```
mac : port
---------------s1:
---------------s2:
---------------s3:
```
> h1 ping h2  
> show_table all_hosts  
(for h1 : `h2ip : h2mac`, for h2 : `h1ip : h1mac`, no entry in h3 and h4’s arp_table)  
```
ip : mac
---------------h1:
h2ip : h2mac
---------------h2:
h1ip : h1mac
---------------h3:
---------------h4:
```
> show_table all_switches  
```
mac : port
---------------s1:
h1mac : 0
h2mac : 1
---------------s2:
h1mac : 0
---------------s3:
h1mac : 2
```

> clear h1  
> show_table all_hosts  
```
ip : mac
---------------h1:
---------------h2:
h1ip : h1mac
---------------h3:
---------------h4:
```
> show_table h2  
```
ip : mac
---------------h2:
h1ip : h1mac
```
