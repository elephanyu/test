# coding:utf-8
# author：elephanyu
import os
import sys
import ctypes
import traceback
from threading import Thread
from multiprocessing import Process
# 包含库目录，便于加载库
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'packages'))
# 包含配置目录，便于读取配置
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'conf'))
# 导入存储ip和port配置
from globals import UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, HTTP_GET_RETRY_NUM

class Proc(Process):
    def __init__(self, urls):
        Process.__init__(self)
        ret = self.get_init_lib()
        if not ret:
            sys.exit()
        else:
            self.lib = ret
        self.urls = urls

    def get_init_lib(self):
        try:
            lib = ctypes.cdll.LoadLibrary('libcds_libc_cds.so')
            cds_cfg = ctypes.create_string_buffer('', 4096)
            ctypes.memset(ctypes.addressof(cds_cfg), 0, ctypes.sizeof(cds_cfg))
            ret = lib.CDS_Init(ctypes.c_ulong(0), cds_cfg)
            if ret != 0:
                print "init uniview's libcds_libc_cds.so failed: %s" % ret
                return None
            else:
                return lib
        except Exception:
            print traceback.format_exc()
            return None

    def run(self):
        threads = []
        ret = self.get_init_lib()
        if ret is not None:
            for url in self.urls:
                thread1 = Thred(self.lib, url)
                thread2 = Thred(self.lib, url)
                threads.append(thread1)
                threads.append(thread2)
            for thread in threads:
                thread.start()
        else:
            print 'lib init err'

class Thred(Thread):
    def __init__(self, lib, url):
        Thread.__init__(self)
        self.lib = lib
        self.url = url

    def run(self):
        lasterr = ''
        for i in range(HTTP_GET_RETRY_NUM):
            if 'fid=' in self.url:
                piclen = int(self.url.split('-')[-1], 16)
            else:
                class tagCDSFileStat(ctypes.Structure):
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

                filestat = tagCDSFileStat()
                ret1 = self.lib.CDS_GetFileStat(ctypes.c_char_p(self.url), ctypes.byref(filestat))
                if ret1 < 0:
                    lasterr = 'uniview CDS_GetFileStat err'
                    continue
                else:
                    piclen = filestat.dulFileCapacity
                    # piclen = 3 * 1024 * 1024
            pic_buf = ctypes.create_string_buffer('', piclen)
            ret = self.lib.CDS_ReadOnceEx(ctypes.c_char_p(self.url), ctypes.c_uint(0), ctypes.c_uint(piclen), pic_buf)
            if ret < 0:
                lasterr = 'uniview CDS_ReadOnceEx err：%s' % ret
                continue
            else:
                filename = self.name + '.jpg'
                with open(filename, 'wb+') as fp:
                    fp.write(pic_buf[0:ret])
                print 'download %s success and saved in %s' % (self.url, filename)
        print 'exception occurs when get url[%s]. [%s]' % (self.url, lasterr)

if __name__ == '__main__':
    links = [
            '/20180322/6101007005/3/2/20180322194058000859721_1.jpg',
            '/20180330/6101012059/20180330101316944_PIC_1_254673.jpg'
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
    try:
        proc = Proc(urls)
        proc.start()
        proc.join()
    except Exception:
        print traceback.format_exc()
