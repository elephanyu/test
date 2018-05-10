# coding:utf-8
import os
import sys
import ctypes
import traceback
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'packages'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'conf'))

from globals import UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, HTTP_GET_RETRY_NUM

class UNIVIEW_CDS:
    def __init__(self):
        ret = self.get_init_lib()
        if not ret:
            sys.exit()
        else:
            self._lib = ret

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

    def download(self, url):
        lasterr = ''
        for i in range(HTTP_GET_RETRY_NUM):
            if 'fid=' in url:
                piclen = int(url.split('-')[-1], 16)
            else:
                class tagCDSFileStat(ctypes.Structure):
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
                ret1 = lib.CDS_GetFileStat(ctypes.c_char_p(url), ctypes.byref(filestat))
                if ret1 < 0:
                    lasterr = 'uniview CDS_GetFileStat err'
                    continue
                else:
                    # 此处获取 piclen为0
                    piclen = filestat.dulFileCapacity
                    # piclen = 3 * 1024 * 1024
            pic_buf = ctypes.create_string_buffer('', piclen)
            ret = self._lib.CDS_ReadOnceEx(ctypes.c_char_p(url), ctypes.c_uint(0), ctypes.c_uint(piclen), pic_buf)
            if ret < 0:
                lasterr = 'uniview CDS_ReadOnceEx err：%s' % ret
                continue
            else:
                return pic_buf[0:ret]
        print 'exception occurs when get url[%s]. [%s]' % (url, lasterr)
        return None

if __name__ == '__main__':
    # get by OracleQuery's excute result
    link = ''
    if 'fid=' in link:
        url = '%s:%s%s' % (UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, link)
    else:
        url = '%s:%s/%s%s' % (UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, 'usrDirCode5178', link)
    lib = UNIVIEW_CDS()
    imageBin = lib.download(url)
    print len(imageBin)