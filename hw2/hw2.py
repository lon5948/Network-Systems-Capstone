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
    def show_table(self): # display ARP table entries for this host
        print("---------------", self.name, ":\n")
        for keys, values in self.arp_table.items():
            print(keys, ":", values, end="\n")
    def clear(self): # clear ARP table entries for this host
        self.arp_table.clear()
    def update_arp(self, ip, mac): # update ARP table with a new entry
        self.arp_table[ip] = mac
    def handle_packet(self, src_ip, src_mac, dst_ip, dst_mac): # handle incoming packets
        self.update_arp(src_ip, src_mac)
        if dst_ip == self.ip:
            self.update_arp(src_ip, src_mac)
            self.send(src_ip, src_mac, dst_ip, dst_mac)
    def ping(self, dst_ip): # handle a ping request
        if(dst_ip in self.arp_table):
            self.send(self.ip, self.mac, dst_ip, self.arp_table[dst_ip])
        else:
            self.send(self.ip, self.mac, dst_ip, 'ffff')
    def send(self, src_ip, src_mac, dst_ip, dst_mac):
        node = self.port_to # get node connected to this host
        node.handle_packet(src_ip, src_mac, dst_ip, dst_mac) # send packet to the connected node

class switch:
    def __init__(self, name, port_n):
        self.name = name
        self.mac_table = dict() # maps MAC addresses to port numbers
        self.port_n = port_n # number of ports on this switch
        self.port_to = list() 
    def add(self, node): # link with other hosts or switches
        self.port_to.append(node)
        self.port_n = self.port_n + 1
    def show_table(self): # display MAC table entries for this switch
        print("---------------", self.name, ":\n")
        for keys, values in self.mac_table.items():
            print(keys, ":", values, end="\n")
    def clear(self): # clear MAC table entries for this switch
        self.mac_table.clear()
    def update_mac(self, mac, port): # update MAC table with a new entry
        self.mac_table[mac] = port
    def send(self, idx, src_ip, src_mac, dst_ip, dst_mac): # send to the specified port
        node = self.port_to[idx] 
        node.handle_packet(src_ip, src_mac, dst_ip, dst_mac) 
    def handle_packet(self, src_ip, src_mac, dst_ip, dst_mac): # handle incoming packets
        port = self.port_to.index(src_mac)
        self.update_mac(src_mac, port)
        if dst_mac == "ffff":
            for i in range(self.port_n):
                self.send(i, src_ip, src_mac, dst_ip, dst_mac)
        elif dst_mac in self.mac_table:
            self.send(self.mac_table[dst_mac], src_ip, src_mac, dst_ip, dst_mac) 
        else:
            for i in range(self.port_n):
                if i != port:
                    self.send(i, src_ip, src_mac, dst_ip, dst_mac)


def add_link(tmp1, tmp2): # create a link between two nodes
    tmp1.add()
    tmp2.add()

def set_topology():
    global host_dict, switch_dict
    hostlist = get_hosts().split(' ')
    switchlist = get_switches().split(' ')
    linklist = get_links().split(' ')
    ip_dic = get_ip()
    mac_dic = get_mac()

    host_dict = dict() # maps host names to host objects
    switch_dict = dict() # maps switch names to switch objects

    # create nodes and links
    for h in hostlist:
        host_dict[h] = host(h, ip_dic[h], mac_dic[h])
    
    for s in switchlist:
        switch_dict[s] = switch(s, 0)

    for l in linklist:
        pair = l.split(',')
        add_link(pair[0], pair[1])
    

def ping(tmp1, tmp2): # initiate a ping between two hosts
    global host_dict, switch_dict
    if tmp1 in host_dict and tmp2 in host_dict : 
        node1 = host_dict[tmp1]
        node2 = host_dict[tmp2]
        node1.ping(node2.ip)
    else:
        print("a wrong command\n")


def show_table(tmp): # display the ARP or MAC table of a node
    tmp.show_table()

def clear(tmp): # clear the ARP or MAC table of a node
    tmp.clear()

def run_net():
    while(1):
        command_line = input(">> ")
        # handle user commands
        command_line = command_line.split(' ')
        if len(command_line) == 3 and command_line[1] == "ping":
            ping(command_line[0], command_line[2])
        elif len(command_line) == 2 and command_line[0] == "show_table":
            if command_line[1] == "all_hosts":
                print("ip : mac")
                for h in get_hosts():
                    show_table(h)
            elif command_line[1] == "all_switches":
                print("mac : port")
                for s in get_switches:
                    show_table(s)
            elif(command_line[1][0] == "h"):
                print("ip : mac")
                show_table(command_line[1])
            elif(command_line[1][0] == "s"):
                print("mac : port")
                show_table(command_line[1])
        elif len(command_line) == 2 and command_line[0] == "clear":
            clear(command_line[0])
        else:
            print("a wrong command\n")
    
def main():
    set_topology()
    run_net()

if __name__ == '__main__':
    main()
