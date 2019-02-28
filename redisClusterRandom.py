# coding: utf-8
from abc import abstractmethod
from random import randint, choice

from rediscluster import StrictRedisCluster

DEBUG = 1
CHARACTERPOOL = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def getRedisClusterClient():
    startup_nodes = [
        {
            'host': '192.168.8.28',
            'port': '7000'
        },
        {
            'host': '192.168.8.28',
            'port': '7001'
        },
        {
            'host': '192.168.8.28',
            'port': '7002'
        },
        {
            'host': '192.168.8.29',
            'port': '7003'
        },
        {
            'host': '192.168.8.29',
            'port': '7004'
        },
        {
            'host': '192.168.8.29',
            'port': '7005'
        }
    ]
    rc = StrictRedisCluster(startup_nodes=startup_nodes, decode_responses=True)
    return rc

class RedisRandom(object):
    num = 100
    strlen = 100
    cleannum = 0
    recyclnum = 0
    recyclemaxnum = num * 10

    def __init__(self, rc=None):
        if rc == None:
            rc = getRedisClusterClient()
        self.rc = rc

    @abstractmethod
    def _generate(self, exmin=None):
        pass

    @abstractmethod
    def _clean(self):
        pass

    def generate(self, num=None, strlen=None, exmin=None):
        if num:
            self.num = num
        if strlen:
            self.strlen = strlen
        self._generate(exmin=exmin)

    def clean(self, num=None):
        self.cleannum = 0
        self.recyclnum = 0
        if num:
            self.num = num
            self.recyclemaxnum = num * 10
        for i in xrange(self.num):
            if self.recyclnum > self.recyclemaxnum:
                break
            else:
                while True:
                    if self.recyclnum > self.recyclemaxnum:
                        break
                    self.recyclnum += 1
                    ret = self._clean()
                    if ret:
                        self.cleannum += 1
        return self.cleannum

    def flush(self):
        self.rc.flushall()
        self.rc.flushdb()

    def _getRandomStr(self, num=20):
        rstr = ''
        for i in xrange(num):
            rstr += choice(CHARACTERPOOL)
        return rstr

    def _getRandomSecond(self, min):
        num = randint(1, min)
        return num * 60

class StringRedisRandom(RedisRandom):
    def _generate(self, exmin=None):
        if exmin is None:
            for i in xrange(1, self.num):
                self.rc.set(self._getRandomStr(2), self._getRandomStr(self.strlen))
        else:
            for i in xrange(1, self.num):
                self.rc.set(self._getRandomStr(2), self._getRandomStr(self.strlen), ex=self._getRandomSecond(exmin))

    def _clean(self):
        key = self._getRandomStr(2)
        if self.rc.get(key):
            ret = self.rc.delete(key)
            if ret:
                if DEBUG:
                    print '{}: del string[{}]'.format(self.cleannum, key)
                return True
        return False

class ListRedisRandom(RedisRandom):
    def _generate(self, exmin=None):
        for i in xrange(1, self.num):
            self.rc.lpush(self._getRandomStr(1), self._getRandomStr(self.strlen))

    def _clean(self):
        key = self._getRandomStr(1)
        llen = self.rc.llen(key)
        if llen > 0:
            ret = self.rc.lpop(key)
            if ret:
                if DEBUG:
                    print '{}: pop list {}[{}], len now[{}]'.format(self.cleannum, key, ret, llen - 1)
                return True
        return False

if __name__ == '__main__':
    rc = getRedisClusterClient()
    srandom = StringRedisRandom(rc=rc)
    srandom.generate(num=1000, strlen=10)
    srandom.clean(num=1000)
    srandom.clean(num=1000)
    lrandom = ListRedisRandom(rc=rc)
    lrandom.generate(num=100, strlen=5)
    lrandom.clean(num=100)
    lrandom.clean(num=100)
