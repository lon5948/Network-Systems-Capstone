from setting import get_hosts, get_switches, get_links, get_ip, get_mac

class host:
    def __init__(self, name, ip, mac):
        self.name = name
        self.ip = ip
        self.mac = mac 
        self.port_to = None 
        self.arp_table = dict() # maps IP addresses to MAC addresses
    def add(self, node):
        self.port_to = node
    def show_table(self):
        # display ARP table entries for this host
    def clear(self):
        # clear ARP table entries for this host
    def update_arp(self, ...):
        # update ARP table with a new entry
    def handle_packet(self, ...): # handle incoming packets
        # ...
    def ping(self, dst_ip, ...): # handle a ping request
        # ...
    def send(self, ...):
        node = self.port_to # get node connected to this host
        node.handle_packet(...) # send packet to the connected node

class switch:
    def __init__(self, name, port_n):
        self.name = name
        self.mac_table = dict() # maps MAC addresses to port numbers
        self.port_n = port_n # number of ports on this switch
        self.port_to = list() 
    def add(self, node): # link with other hosts or switches
        self.port_to.append(node)
    def show_table(self):
        # display MAC table entries for this switch
    def clear(self):
        # clear MAC table entries for this switch
    def update_mac(self, ...):
        # update MAC table with a new entry
    def send(self, idx, ...): # send to the specified port
        node = self.port_to[idx] 
        node.handle_packet(...) 
    def handle_packet(self, ...): # handle incoming packets
        # ...


def add_link(tmp1, tmp2): # create a link between two nodes
    # ...
    return

def set_topology():
    global host_dict, switch_dict, link_dict
    hostlist = get_hosts().split(' ')
    switchlist = get_switches().split(' ')
    linklist = get_links().split(' ')
    ip_dic = get_ip()
    mac_dic = get_mac()

    host_dict = dict() # maps host names to host objects
    switch_dict = dict() # maps switch names to switch objects
    link_dict = dict() # maps switch/hosts names to neighbors

    # create nodes and links
    for h in hostlist:
        host_dict[h] = host(h, ip_dic[h], mac_dic[h])
    
    for l in linklist:
        pair = l.split(',')
        if pair[0] not in link_dict:
            link_dict[pair[0]] = list()
        link_dict[pair[0]].append(pair[1])
        if pair[1] not in link_dict:
            link_dict[pair[1]] = list()
        link_dict[pair[1]].append(pair[0])
    
    for s in switchlist:
        switch_dict[s] = switch(s, len(link_dict[s]))

    

def ping(tmp1, tmp2): # initiate a ping between two hosts
    global host_dict, switch_dict
    if tmp1 in host_dict and tmp2 in host_dict : 
        node1 = host_dict[tmp1]
        node2 = host_dict[tmp2]
        node1.ping(node2.ip)
    else : 
        # invalid command


def show_table(tmp): # display the ARP or MAC table of a node
    # ...
    return


def clear():
    # ...
    return

def run_net():
    while(1):
        command_line = input(">> ")
        # handle user commands
        command_line = command_line.split(' ')
        if len(command_line) == 3 and command_line[1] == "ping":
            ping(command_line[0], command_line[2])
        elif len(command_line) == 2 and command_line[0] == "show_table":
            if command_line[1] == "all_hosts":
                for h in get_hosts():
                    show_table(h)
            elif command_line[1] == "all_switches":
                for s in get_switches:
                    show_table(s)
            else:
                show_table(command_line[1])

    
def main():
    set_topology()
    run_net()


if __name__ == '__main__':
    main()
