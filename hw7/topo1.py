from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.net import Mininet
import sys

class MyTopo(Topo):

    def build(self):
        # Add switches
        switch = self.addSwitch('s1')
        
        # Add hosts
        hosts = []
        for i in range(4):
            host = self.addHost('h{}'.format(i+1))
            hosts.append(host)
        
        # Add links
        for i in range(4):
            self.addLink(hosts[i], switch)
topos = {'mytopo': (lambda: MyTopo())}
#net = Mininet(topo=MyTopo(), controller=None)
#controller_ip = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
#controller = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)
#net.start()
#controller.start()
#net.interact()
# topos = {'mytopo': (lambda: MyTopo())}
