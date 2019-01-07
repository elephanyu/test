# coding:utf-8
# author：Elephanyu
import ctypes
import traceback
from threading import Thread
from multiprocessing import Process

# 定义存储的IP和端口
UNIVIEW_STORAGE_IP = '192.168.1.1'
UNIVIEW_STORAGE_PORT = 10010

class tagCDSFileStat(ctypes.Structure):
    '''
        C结构体python定义    
    '''
    _pack_ = 4
    _fields_ = [
        ('szFileName', ctypes.c_char * 256),
        ('dulFileCapacity', ctypes.c_ulonglong),
        ('lCTime', ctypes.c_int),
        ('lMTime', ctypes.c_int),
        ('ulStat', ctypes.c_uint),
        ('dulDirId', ctypes.c_ulonglong),
        ('ulOpStat', ctypes.c_ulong)
    ]

class UNIVIEW_CDS:
    def __init__(self):
        self.lib = None
    
    def initLib(self):
        '''
            加载C库并初始化，初始化成功则赋值给self.lib
        '''
        try:
            lib = ctypes.cdll.LoadLibrary('libcds_libc_cds.so')
            cds_cfg = ctypes.create_string_buffer('', 4096)
            ctypes.memset(ctypes.addressof(cds_cfg), 0, ctypes.sizeof(cds_cfg))
            ret = lib.CDS_Init(ctypes.c_ulong(0), cds_cfg)
            if ret < 0:
                print "init uniview's libcds_libc_cds.so failed: %s" % ret
            else:
                self.lib = lib
        except Exception:
            print traceback.format_exc()

    def getLibStatus(self):
        '''
            C库加载初始化是否成功
        '''
        if self.lib is not None:
            return True
        else:
            return False

    def getLib(self):
        return self.lib

    def readFile(self, url, piclen=None):
        '''
            read file binary content
            :param url: the file path
            :param piclen: default 3*1024*1024 if None, is needed when url without fid fields
            :return fileBinaryContent
        '''
        if piclen is None:
            if 'fid=' in url:
                piclen = int(url.split('-')[-1], 16)
            else:
                piclen = 3 * 1024 * 1024
        pic_buf = ctypes.create_string_buffer('', piclen)
        ret = self.lib.CDS_ReadOnceEx(ctypes.c_char_p(url), ctypes.c_uint(0), ctypes.c_uint(piclen), pic_buf)
        if ret < 0:
            print 'uniview CDS_ReadOnceEx err：%s' % ret
            return None
        else:
            return pic_buf[0:ret]

    def getFileLen(self, url):
        '''
            get the file length
            :param url: the file path
            :return filelen: None or the file length
        '''
        filestat = tagCDSFileStat()
        ret = self.lib.CDS_GetFileStat(ctypes.c_char_p(url), ctypes.byref(filestat))
        if ret < 0:
            print 'uniview CDS_GetFileStat err: %s' % ret
            return None
        else:
            return filestat.dulFileCapacity


class Threader(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.lib = None
        self.url = None

    def setLib(self, lib):
        self.lib = lib

    def setUrl(self, url):
        self.url = url
        print 'seturl: %s' % url

    def run(self):
        '''
            如果存储url包含fid=，则fid的值即为16进制的图片长度
            否则，使用C库获取图片长度
            最后，通过url和图片长度使用C库读取图片二进制流        
        '''
        if 'fid=' not in self.url:
            ret2 = self.lib.getFileLen(self.url)
            if ret2 is None:
                print 'get url[%s] len err' % self.url
            piclen = ret2
        else:
            piclen = int(self.url.split('-')[-1], 16)
        if piclen is not None:
            ret3 = self.lib.readFile(self.url, piclen=piclen)
            if ret3 is not None:
                print 'read url[%s] success, len: %s' % (self.url, len(ret3))
            else:
                print 'read url[%s] error' % self.url

class Procer(Process):
    def __init__(self):
        Process.__init__(self)
        self.lib = None
        self.urls = None

    def setLib(self, lib):
        self.lib = lib

    def setUrls(self, urls):
        self.urls = urls

    def run(self):
        threads = []
        for url in self.urls:
            t = Threader()
            t.setLib(self.lib)
            t.setUrl(url)
            threads.append(t)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

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
    p1 = Procer()
    p2 = Procer()
    lib = UNIVIEW_CDS()
    lib.initLib()
    if lib.getLibStatus():
        # uniview C库支持进程并发，不支持线程并发
        p1.setLib(lib)
        p1.setUrls(urls)
        p2.setLib(lib)
        p2.setUrls(urls)
        p1.start()
        p2.start()
    else:
        print 'lib init err'
