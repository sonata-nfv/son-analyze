#!/usr/bin/env python2
# pylint: disable=missing-docstring
import sys
import time
import signal
import threading
import logging
from emuvim.dcemulator.net import DCNetwork
from mininet.node import RemoteController
from emuvim.api.sonata import SonataDummyGatekeeperEndpoint


_LOGGER = logging.getLogger(__name__)


class SigTermCatcher:  # pylint: disable=too-few-public-methods

    def __init__(self, net):
        _LOGGER.info("Setting up the signal catcher")
        self.net = net
        signal.signal(signal.SIGTERM, self.stop_containernet)
        signal.signal(signal.SIGINT, self.stop_containernet)

    def stop_containernet(self, signum, frame):
        msg = "Catched signal {0!s} on frame {1!s}".format(signum, frame)
        _LOGGER.warn(msg)
        self.net.stop()
        time.sleep(2)
        exit(1)


def _in_separate_thread(net):
    _LOGGER.info("Starting the topology")
    try:
        net.start()
    except Exception as e:
        print >>sys.stderr, "Ignoring exception in thread: {!s}".format(e)


def setup_topology(net):
    _LOGGER.info("Setting up the topology")
    dc = net.addDatacenter("dc")  # pylint: disable=invalid-name
    # add the SONATA dummy gatekeeper to each DC
    sdkg1 = SonataDummyGatekeeperEndpoint("0.0.0.0", 5000, deploy_sap=True)
    sdkg1.connectDatacenter(dc)
    # run the dummy gatekeeper (in another thread, don't block)
    sdkg1.start()


def main():
    _LOGGER.info("Executing the integration topology")
    net = DCNetwork(controller=RemoteController,
                    monitor=True,
                    enable_learning=True)
    SigTermCatcher(net)
    setup_topology(net)

    sub_thread = threading.Thread(target=_in_separate_thread, args=(net,))
    sub_thread.start()
    while True:
        time.sleep(120)
    exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        msg = "Ignoring exception in the main thread: {!s}".format(e)
        print >>sys.stderr, msg
