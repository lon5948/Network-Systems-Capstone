from mininet.topo import Topo

class MyTopo(Topo):
    def build(self):
        #Add controller
        controller = self.addController('c1', controller=RemoteController, ip='', port=6633)

        # Add switches
        switch = self.addSwitch('s2')
        
        # Add hosts
        hosts = []
        for i in range(4):
            host = self.addHost('h{}'.format(i+5))
            hosts.append(host)
        
        # Add links
        self.addLink(controller, switch)
        for i in range(4):
            self.addLink(hosts[i+4], switch)