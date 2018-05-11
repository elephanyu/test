# coding:utf-8
# author：elephanyu
import os
import sys
import traceback
from threading import Thread
from multiprocessing import Process
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'conf'))
from globals import UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT
from uniview_cds import UNIVIEW_CDS

class Threader(Thread):
    def __init__(self, lib=None):
        Thread.__init__(self)
        self.lib = lib
        self.url = None

    def setUrl(self, url):
        self.url = url
        print 'seturl: %s' % url

    def run(self):
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

class Procer(Process):
    def __init__(self):
        Process.__init__(self)
        self.lib = None
        self.urls = None

    def _intiLib(self):
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

    def setUrls(self, urls):
        self.urls = urls

    def run(self):
        threads = []
        self._intiLib()
        if self._getLibStatus():
            for url in self.urls:
                t = Threader(self.lib)
                t.setUrl(url)
                threads.append(t)
            for thread in threads:
                thread.start()
        else:
            print 'lib init err'

if __name__ == '__main__':
    links = [
            '/20180322/6101007005/3/2/20180322194058000859721_1.jpg',
            '/20180330/6101012059/20180330101316944_PIC_1_254673.jpg',
            '/usrDirCode5178/20180330/6101004027/01/2/K_610100402700_01_2_20180330101412615_1.jpg?dev=cdvserver2&fid=792839-17-6716200000-A77F71-23704',
            '/usrDirCode5178/20180330/6101006001/01/2/K_20180330101416402_1_533944.jpg?dev=cdvserver3&fid=7289-23-190C200007-1C2C3A4-87EF7'
        ]
    urls = []
    for link in links:
        if 'fid=' in link:
            url = '%s:%s%s' % (UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, link)
        else:
            url = '%s:%s/%s%s' % (UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, 'usrDirCode5178', link)
        urls.append(url)
    p = Procer()
    p.setUrls(urls)
    p.start()



