#!/usr/bin/env python2
# pylint: disable=missing-docstring
import time
import signal
import threading
from emuvim.dcemulator.net import DCNetwork
from mininet.node import RemoteController
from emuvim.api.sonata import SonataDummyGatekeeperEndpoint


class SigTermCatcher:

    def __init__(self, net):
        self.net = net
        signal.signal(signal.SIGTERM, self.stop_containernet)
        signal.signal(signal.SIGINT, self.stop_containernet)

    def stop_containernet(self, signum, frame):
        self.net.stop()
        time.sleep(2)
        exit(1)


def _in_separate_thread(net):
    net.start()


def setup_topology(net):
    dc = net.addDatacenter("dc")
    # add the SONATA dummy gatekeeper to each DC
    sdkg1 = SonataDummyGatekeeperEndpoint("0.0.0.0", 5000, deploy_sap=True)
    sdkg1.connectDatacenter(dc)
    # run the dummy gatekeeper (in another thread, don't block)
    sdkg1.start()


def main():
    net = DCNetwork(controller=RemoteController, monitor=True, enable_learning=True)
    SigTermCatcher(net)
    setup_topology(net)

    t = threading.Thread(target=_in_separate_thread, args=(net,))
    t.start()
    while True:
        time.sleep(120)
    exit(2)


if __name__ == "__main__":
    main()
