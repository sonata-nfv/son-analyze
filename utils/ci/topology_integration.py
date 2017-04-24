#!/usr/bin/env python2
# pylint: disable=missing-docstring
import sys
import time
import signal
import threading
import multiprocessing as mp
import logging
import os
from emuvim.dcemulator.net import DCNetwork
from mininet.node import RemoteController
from emuvim.api.sonata import SonataDummyGatekeeperEndpoint


_LOGGER = logging.getLogger(__name__)


class SigTermCatcher:  # pylint: disable=too-few-public-methods

    def __init__(self):
        _LOGGER.info("Setting up the signal catcher")
        self.terminating = False
        self.org_term = signal.getsignal(signal.SIGTERM)
        self.org_int = signal.getsignal(signal.SIGINT)
        self.org_usr1 = signal.getsignal(signal.SIGUSR1)

    def setup_signal(self):
        signal.signal(signal.SIGTERM, self.stop_containernet)
        signal.signal(signal.SIGINT, self.stop_containernet)
        signal.signal(signal.SIGUSR1, self.restart_containernet)

    def restore_signal(self):
        signal.signal(signal.SIGTERM, self.org_term)
        signal.signal(signal.SIGINT, self.org_int)
        signal.signal(signal.SIGUSR1, self.org_usr1)

    def register(self, forked_process, net):
        self.forked_process = forked_process
        self.net = net

    def stop_containernet(self, signum, frame):
        self.terminating = True
        msg = "Catched stopping signal {0!s} on frame {1!s} for pid {2!s} and parent pid {3!s}".format(signum, frame, os.getpid(), os.getppid())
        _LOGGER.warn(msg)
        self.net.stop()
        time.sleep(2)
        if self.forked_process.is_alive():
            self.forked_process.terminate()
        exit(1)

    def restart_containernet(self, signum, frame):
        msg = "Catched restarting signal {0!s} on frame {1!s} for pid {2!s} and parent pid {3!s}".format(signum, frame, os.getpid(), os.getppid())
        _LOGGER.warn(msg)
        self.net.stop()
        time.sleep(2)
        if self.forked_process.is_alive():
            self.forked_process.terminate()

    def is_alive(self):
        return not self.terminating


def setup_topology(net):
    _LOGGER.info("Setting up the topology")
    dc = net.addDatacenter("dc")  # pylint: disable=invalid-name
    # add the SONATA dummy gatekeeper to each DC
    sdkg1 = SonataDummyGatekeeperEndpoint("0.0.0.0", 5000, deploy_sap=True)
    sdkg1.connectDatacenter(dc)
    # run the dummy gatekeeper (in another thread, don't block)
    sdkg1.start()


def create_and_start_topology(net):
    _LOGGER.info("Creating and starting the topology")
    setup_topology(net)
    try:
        net.start()
    except Exception as e:
        print >>sys.stderr, "Ignoring exception in thread: {!s}".format(e)
    while True:
        time.sleep(120)


def spawn_process(sc):
    _LOGGER.info("Creating a topology process")
    net = DCNetwork(controller=RemoteController,
                    monitor=True,
                    enable_learning=True)
    forked_process = mp.Process(target=create_and_start_topology, args=(net,))
    sc.register(forked_process, net)
    return forked_process


def main():
    _LOGGER.info("Executing the integration topology with pid {0!s} and parent pid {1!s}".format(os.getpid(), os.getppid()))
    sc = SigTermCatcher()

    while True:
        if sc.is_alive():
            forked_process = spawn_process(sc)
            sc.restore_signal()
            forked_process.start()
            sc.setup_signal()
            forked_process.join()
        time.sleep(1)
    exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        _LOGGER.error("Ignoring exception in the main thread under pid {0!s} and parent pid {1!s}: {2!s}".format(os.getpid(), os.getppid(), e))
        print >>sys.stderr, msg
