## Overview
For this Mininet-based SDN implementation task, you need to write a python program to create the network topology and a controller that implements crucial functions.

## Environment
#### Python 3.8
#### Ubuntu 20.04
#### Virtualbox
#### Mininet 2.3.1b1 (master branch)
```
git clone https://github.com/mininet/mininet (or download zip on github)

cd mininet/util/

./install.sh -n3v
```
#### Ryu 4.34 (pip install)  
(It is recommended to develop a good habit of using python-venv.)
```
pip3 install eventlet==0.30.2

pip3 install wheel

pip3 install ryu
```

## Network Topology
```
2 VMs
1 controller
2 switches
8 (4 + 4 ) hosts (Their IDs are assigned in a linear way)
```
![image](https://github.com/lon5948/Network-Systems-Capstone/blob/main/hw7/topo.jpg)

## Instruction
Hint: Both VMs need to be on the same LAN
- Controller
  - VM1: `ryu-manager {controller_code} --verbose`
- Mininet
  - VM1, VM2: `sudo mn --custom {topology_code} --topo={topology_name} --controller=remote,ip={controller_ip}`
- List the OVS interfaces and their corresponding OpenFlow port numbers.
  - `sudo ovs-vsctl -- --columns=name,ofport list Interface`

## Part 1: Creating the SDN Network
- Write a python program for implementing the required control function in the Ryu controller
- Write a python program for creating the network topology

### Control Function that is required to implement
#### Four flow tables (default_table, filter_table_1, filter_table_2, forward_table) are used to implement the required control function.

For a packet:
1. Go to default_table
2. Then go to filter_table_1
3. If this packet is identified as an ICMP packet, it will go to filter_table_2, otherwise it will go to forward_table
4. For filter_table_2, if the packet comes from the switch’s {target_ports}, it will be dropped, otherwise it will go to forward_table.
5. For forward table, forward the packet  
  
ps: {target_ports} = (port_3 and port_4)

## Part 2: Building the GRE tunnel
Run on both VMs:  
`sudo ovs-vsctl add-port {switch_name} {gre_port_name} – set interface {gre_interface_name} type=gre options:remote_ip={another_vm_ip}`
