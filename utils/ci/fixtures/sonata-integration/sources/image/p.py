import sys
import gc
import time
import math
from twisted.internet import epollreactor
epollreactor.install()
from twisted.internet import reactor
from twisted.web.client import HTTPConnectionPool
import treq


pool = HTTPConnectionPool(reactor)
loop_counter = 0
acc = []


p = 60
sp = 40


def c(x_in_period):
    # tmp = math.fabs(x % p - (x % p) % sp)
    tmp = math.fabs(x_in_period - x_in_period % sp)
    if tmp == 0:
        return 1
    else:
        return 0


def d(x):
    x_in_period = x % p
    return int(100 * math.sin((math.pi * x_in_period) / sp)) * c(x_in_period)

def inverse(y):
    if y == 0:
        return 1
    else:
        return 0


def loop(limit):
    global loop_counter
    global acc
    loop_counter += 1
    size = 0
    # x_mod = loop_counter % 120
    # nb_request = 0
    # if x_mod <= 100:
    #     nb_request = int(500 * math.sin(math.pi * x_mod / 100.0))
    nb_request = d(loop_counter)
    if (loop_counter % p) == 0:
        acc = []
        gc.collect()
    if sp <= (loop_counter % p):
        size = 409600.0 * math.log(1.0 + ((loop_counter % (p - sp)) / (p - sp)) * p)
        acc.append(bytearray(int(size)))
    print('... {0:d} -> {1:d}, len(acc)={2:d}, size={3:f}'.format(loop_counter, nb_request, len(acc), size))
    for _ in range(nb_request):
        # size = int(1024 * math.log(loop_counter % p) * inverse(c(loop_counter % p)))
        # acc.append(bytearray(size))
        tmp = treq.get("http://10.30.0.2:2002",
                       timeout=1,
                       persistent=True,
                       pool=pool)
        tmp.addErrback(lambda _: None)
    if limit < 0 or loop_counter < limit:
        reactor.callLater(1, loop, limit)
    else:
        reactor.stop()


def main(args):
    limit = -1
    if len(args) == 2:
        limit = int(args[1])
    print("limit= {0:d}, args={1!s}".format(limit, args))
    target = b"http://10.30.0.2:2002"
    d = treq.get(target)
    d.addCallback(lambda _: None)
    reactor.callLater(1, loop, limit)
    reactor.run()


# def main():
#     target = b"http://10.30.0.2:2002"
#     reactor.run()
#     for i in range(5):
#         now = time.time()
#         print("{0!s}".format(i))
#         d = agent.request(
#             'GET',
#             target,
#             Headers({'User-Agent': ['Twisted Web Client Example']}),
#             None)
#         delta = time.time() - now
#         time.sleep(min(delta, 1.0))


# import http.client


# def main():
#     conn = http.client.HTTPConnection("10.30.0.2", port=2002)
#     conn.connect()
#     for i in range(5):
#         now = time.time()
#         print("{0!s}".format(i))
#         conn.request("GET", "/")
#         conn.getresponse()
#         delta = time.time() - now
#         time.sleep(min(delta, 1.0))
#     conn.close()


if __name__ == "__main__":
    main(sys.argv)
