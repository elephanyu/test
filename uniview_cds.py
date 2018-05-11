# coding:utf-8
import os
import sys
import ctypes
import traceback
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'packages'))

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

class UNIVIEW_CDS:
    def __init__(self):
        self.lib = None

    '''
        set lib if lib init success
    '''
    def initLib(self):
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

    '''
        get lib status
        :return bool: True or False
    '''
    def getLibStatus(self):
        if self.lib is not None:
            return True
        else:
            return False

    '''
        get lib and judge the lib initing result
        :return lib: None or init lib 
    '''
    def getLib(self):
        return self.lib

    '''
        read file binary content
        :param url: the file path
        :param piclen: default 3*1024*1024 if None, is needed when url without fid fields
        :return fileBinaryContent
    '''
    def readFile(self, url, piclen=None):
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

    '''
        get the file length
        :param url: the file path
        :return filelen: None or the file length
    '''
    def getFileLen(self, url):
        filestat = tagCDSFileStat()
        ret = self.lib.CDS_GetFileStat(ctypes.c_char_p(url), ctypes.byref(filestat))
        if ret < 0:
            print 'uniview CDS_GetFileStat err: %s' % ret
            return None
        else:
            return filestat.dulFileCapacity

if __name__ == '__main__':
    lib = UNIVIEW_CDS()
    lib.initLib()
    if lib.getLibStatus():
        print lib.getLib()