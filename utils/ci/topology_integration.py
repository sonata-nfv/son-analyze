#!/usr/bin/env python2
# pylint: disable=missing-docstring
import sys
import time
import signal
import threading
import multiprocessing as mp
import logging
import os
import socket
import stat
from emuvim.api.rest.rest_api_endpoint import RestApiEndpoint
from emuvim.dcemulator.net import DCNetwork
from mininet.node import RemoteController
from mininet.log import setLogLevel
from emuvim.api.sonata import SonataDummyGatekeeperEndpoint


_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class SigTermCatcher:  # pylint: disable=too-few-public-methods

    def __init__(self):
        _LOGGER.info("Setting up the signal catcher")
        self.restart_lock = mp.Lock()
        self.terminating = False
        self.stop_hooks = []
        self.org_term = signal.getsignal(signal.SIGTERM)
        self.org_int = signal.getsignal(signal.SIGINT)
        self.org_usr1 = signal.getsignal(signal.SIGUSR1)

    def setup_signal(self):
        signal.signal(signal.SIGTERM, self.stop_containernet)
        signal.signal(signal.SIGINT, self.stop_containernet)
        signal.signal(signal.SIGUSR1, self.restart_containernet)

    def ignore_signal(self):
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGUSR1, signal.SIG_IGN)

    def restore_signal(self):
        signal.signal(signal.SIGTERM, self.org_term)
        signal.signal(signal.SIGINT, self.org_int)
        signal.signal(signal.SIGUSR1, self.org_usr1)

    def register(self, forked_process, lock):
        self.forked_process = forked_process
        self.lock = lock

    def stop_containernet(self, signum, frame):
        msg = "Catched stopping signal {0!s} on frame {1!s} for pid {2!s} and parent pid {3!s}".format(signum, frame, os.getpid(), os.getppid())
        _LOGGER.warn(msg)
        # self.net.stop()
        self.lock.release()
        # for elt in self.stop_hooks:
        #     elt()
        for i in range(30):
            if self.forked_process.is_alive():
                self.forked_process.terminate()
                time.sleep(1)
            else:
                break
        self.terminating = True

    def restart_containernet(self, signum, frame):
        msg = "Catched restarting signal {0!s} on frame {1!s} for pid {2!s} and parent pid {3!s}".format(signum, frame, os.getpid(), os.getppid())
        _LOGGER.warn(msg)
        # self.net.stop()
        self.lock.release()
        for i in range(30):
            if self.forked_process.is_alive():
                self.forked_process.terminate()
                time.sleep(1)
            else:
                break

    def is_alive(self):
        return not self.terminating

    def add(self, to_be_stopped):
        self.stop_hooks.insert(0, to_be_stopped)


def setup_topology(net):
    _LOGGER.info("Setting up the topology")
    dc = net.addDatacenter("dc1")  # pylint: disable=invalid-name
    net.addLink(dc, net.addSwitch("s1"), delay="10ms")
    # add the SONATA dummy gatekeeper to each DC
    rapi1 = RestApiEndpoint("0.0.0.0", 5001)
    rapi1.connectDCNetwork(net)
    rapi1.connectDatacenter(dc)
    rapi1.start()
    sdkg1 = SonataDummyGatekeeperEndpoint("0.0.0.0", 5000, deploy_sap=False)
    sdkg1.connectDatacenter(dc)
    # run the dummy gatekeeper (in another thread, don't block)
    sdkg1.start()


def create_and_start_topology(lock, restart_lock):
    _LOGGER.info("Creating and starting the topology")
    net = DCNetwork(controller=RemoteController,
                    monitor=True,
                    enable_learning=True)
    restart_lock.acquire()
    setup_topology(net)
    try:
        net.start()  # non blocking call
        _LOGGER.info("Waiting for the barrier to stop the topology")
        lock.acquire()
        _LOGGER.info("Stopping the topology")
        net.stop()
        lock.release()
    except Exception as e:
        _LOGGER.error("Ignoring exception in thread: {!s}".format(e))
    restart_lock.release()
    exit(1)
        # print >>sys.stderr, "Ignoring exception in thread: {!s}".format(e)
    # while True:
    #     time.sleep(120)


def spawn_process(sc):
    _LOGGER.info("Creating a topology process")
    # net = DCNetwork(controller=RemoteController,
    #                 monitor=True,
    #                 enable_learning=True)
    lock = mp.Lock()
    lock.acquire()
    forked_process = mp.Process(target=create_and_start_topology, args=(lock, sc.restart_lock))
    sc.register(forked_process, lock)
    return forked_process


def create_socket():
    _LOGGER.info("Creating a socket and listen")
    path = "/tmp/.sonata_integration.socket"
    if os.path.exists(path):
        os.remove(path)
    # server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(path)
    os.chmod(path, stat.S_IRWXO)
    server.listen(1)
    return server


def listen_socket(server, sc):
    while sc.is_alive():
        # (datagram, addr) = server.recvfrom(len('a'))
        try:
            client, addr = server.accept()
        except socket.error as e:
            _LOGGER.error("Ignoring error while accepting connection: {0!s}".format(e))
            exit(1)
        _LOGGER.info("Accepted connection from {0!s}".format(addr))
        datagram = client.recv(len('a'))
        if datagram:
            _LOGGER.info("Received {0!s} from {1!s}".format(datagram, addr))
            if datagram == 'r':
                sc.restart_containernet(-1, -2)
                sc.restart_lock.acquire()
                _LOGGER.info("Restart done")
                # server.send('o')
                client.send('o')
                sc.restart_lock.release()
            client.close()
        else:
            client.close()
            break


def spawn_socket_thread(sc):
    _LOGGER.info("Creating a socket process")
    server = create_socket()
    t = threading.Thread(target=listen_socket, args=(server, sc))
    return (t, server)


def main():
    _LOGGER.info("Executing the integration topology with pid {0!s} and parent pid {1!s}".format(os.getpid(), os.getppid()))
    setLogLevel('debug')  # set Mininet loglevel
    # create_and_start_topology(DCNetwork(controller=RemoteController,
    #                                     monitor=True,
    #                                     enable_learning=True))
    sc = SigTermCatcher()
    (server_thread, server) = spawn_socket_thread(sc)
    server_thread.start()

    while True:
        if sc.is_alive():
            forked_process = spawn_process(sc)
            sc.ignore_signal()
            forked_process.start()
            sc.setup_signal()
            forked_process.join()
        else:
            break
        time.sleep(1)

    _LOGGER.info("Stopping the server")
    server.shutdown(socket.SHUT_RDWR)
    server_thread.join()
    exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        _LOGGER.error("Ignoring exception in the main thread under pid {0!s} and parent pid {1!s}: {2!s}".format(os.getpid(), os.getppid(), e))
