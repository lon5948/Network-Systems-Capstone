from mininet.topo import Topo

class MyTopo(Topo):
    def build(self):
        # Add controller
        controller = self.addController('c1')

        # Add switches
        switch = self.addSwitch('s1')
        
        # Add hosts
        hosts = []
        for i in range(4):
            host = self.addHost('h{}'.format(i+1))
            hosts.append(host)
        
        # Add links
        self.AddLink(controller, switch)
        for i in range(4):
            self.addLink(hosts[i], switch)