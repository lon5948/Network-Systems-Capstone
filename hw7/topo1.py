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
