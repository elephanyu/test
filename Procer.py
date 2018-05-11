# coding:utf-8
# author：elephanyu
import os
import sys
import traceback
from multiprocessing import Process
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'conf'))
from globals import UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT
from uniview_cds import UNIVIEW_CDS

class Procer(Process):
    def __init__(self):
        Process.__init__(self)
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
            if 'fid=' not in self.url:
                print 5
                ret2 = self.lib.getFileLen(self.url)
                print 6
                if ret2 is None:
                    print 'get url[%s] len err' % self.url
                    return
                piclen = ret2
            else:
                piclen = int(self.url.split('-')[-1], 16)
            print 3
            ret3 = self.lib.readFile(self.url, piclen=piclen)
            print 4
            if ret3 is not None:
                print 'read url[%s] success, len: %s' % (self.url, len(ret3))
            else:
                print 'read url[%s] error' % self.url
        else:
            print 'lib init err'

if __name__ == '__main__':
    link = '/20180322/6101007005/3/2/20180322194058000859721_1.jpg'
    # link = '/usrDirCode5178/20180330/6101004027/01/2/K_610100402700_01_2_20180330101412615_1.jpg?dev=cdvserver2&fid=792839-17-6716200000-A77F71-23704'
    if 'fid=' in link:
        url = '%s:%s%s' % (UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, link)
    else:
        url = '%s:%s/%s%s' % (UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, 'usrDirCode5178', link)
    p1 = Procer()
    p1.setUrl(url)
    p1.start()
    p1.join()
