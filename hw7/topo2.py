from mininet.topo import Topo

class MyTopo(Topo):
    def build(self):
        # Add switches
        switch = self.addSwitch('s2')
        
        # Add hosts
        hosts = []
        for i in range(4):
            host = self.addHost('h{}'.format(i+5))
            hosts.append(host)
        
        # Add links
        for i in range(4):
            self.addLink(hosts[i], switch)

topos = {'mytopo': (lambda: MyTopo())}
