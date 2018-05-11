# coding:utf-8
# author：elephanyu
import os
import sys
import traceback
from threading import Thread
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'conf'))
from globals import UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT
from uniview_cds import UNIVIEW_CDS

class Threader(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.lib = None
        self.url = None

    def setLib(self, lib):
        self.lib = lib

    def setUrl(self, url):
        self.url = url

    def run(self):
        if 'fid=' not in self.url:
            ret2 = self.lib.getFileLen(self.url)
            if ret2 is None:
                print 'get url[%s] len err' % self.url
                return
            piclen = ret2
        else:
            piclen = int(self.url.split('-')[-1], 16)
        ret3 = self.lib.readFile(self.url, piclen=piclen)
        if ret3 is not None:
            print 'read url[%s] success, len: %s' % (self.url, len(ret3))
        else:
            print 'read url[%s] error' % self.url

class Threader2(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.lib = None
        self.url = None

    def _initLib(self):
        lib = UNIVIEW_CDS()
        lib.initLib()
        if lib.getLibStatus():
            self.lib = lib
        else:
            print 'lib init err'

    def _getLibStatus(self):
        if self.lib is not None:
            return True
        else:
            return False

    def setUrl(self, url):
        self.url = url

    def run(self):
        self._initLib()
        if self._getLibStatus():
            t1 = Threader()
            t2 = Threader()
            t1.setLib(self.lib)
            t1.setUrl(self.url)
            t2.setLib(self.lib)
            t2.setUrl(self.url)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        else:
            print 'lib init err'

if __name__ == '__main__':
    link = '/20180322/6101007005/3/2/20180322194058000859721_1.jpg'
    # link = '/usrDirCode5178/20180330/6101004027/01/2/K_610100402700_01_2_20180330101412615_1.jpg?dev=cdvserver2&fid=792839-17-6716200000-A77F71-23704'
    if 'fid=' in link:
        url = '%s:%s%s' % (UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, link)
    else:
        url = '%s:%s/%s%s' % (UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, 'usrDirCode5178', link)
    t = Threader2()
    t.setUrl(url)
    t.start()
    t.join()

