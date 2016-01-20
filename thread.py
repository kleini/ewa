import sys
from threading import Thread
from time import sleep


alive = True
i = 0
j = 0


def run_i():
    global i
    while alive:
        i += 1


def run_j():
    global j
    while alive:
        j += 1


def main():
    global alive
    ti = Thread(target=run_i)
    tj = Thread(target=run_j)
    ti.setDaemon(True)
    tj.setDaemon(True)
    ti.start()
    tj.start()
    sleep(2)
    alive = False
    ti.join()
    tj.join()
    print('i=%d j=%d' % (i, j))
    return 0


if __name__ == '__main__':
    sys.exit(main())
