# coding:utf-8
# author：elephanyu
import os
import sys
import ctypes
import traceback
# 包含库目录，便于加载库
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'packages'))
# 包含配置目录，便于读取配置
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'conf'))
# 导入存储ip和port配置
from globals import UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, HTTP_GET_RETRY_NUM

class UNIVIEW_CDS:
	# 初始化库文件
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
	
	# 下载函数
    def download(self, url):
        lasterr = ''
        for i in range(HTTP_GET_RETRY_NUM):
            # 带fid的文件路径
			if 'fid=' in url:
                piclen = int(url.split('-')[-1], 16)
            else:
				# 不带fid的文件路径
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
    link = '/20180322/6101007005/3/2/20180322194058000859721_1.jpg'
	# link = '/usrDirCode5178/20180330/6101004027/01/2/K_610100402700_01_2_20180330101412615_1.jpg?dev=cdvserver2&fid=792839-17-6716200000-A77F71-23704'
	# 合成完成路径
    if 'fid=' in link:
        url = '%s:%s%s' % (UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, link)
    else:
        url = '%s:%s/%s%s' % (UNIVIEW_STORAGE_IP, UNIVIEW_STORAGE_PORT, 'usrDirCode5178', link)
    lib = UNIVIEW_CDS()
    imageBin = lib.download(url)
    print len(imageBin)
	
	
'''
typedef struct tagCDSFileStatEx
{
    /** 文件名称，全路径 */
    char szFileName[CDS_FILE_PATH_LEN];
    /** 文件大小*/
    unsigned long long dulFileCapacity;
    /** 文件创建时间 */
    int lCTime;
    /** 文件最后更新时间*/
    int lMTime;
    /** 文件状态，参见MAS_FILE_STAT_TYPE_E */
    unsigned int ulStat;
    /** 目录索引编号 */
    unsigned long long dulDirId;
    /** 文件操作类型，参见MAS_FILE_OP_TYPE_E */
    unsigned long ulOpStat;
    /** 文件所在ND的IP地址*/
    char szNdAddr[CDS_IPADDR_LEN];
    /**文件所在ND 的编码*/
    char szNdCode[CDS_CODE_LEN];
    /** 文件所在资源路径*/
    char szRespath[CDS_FILE_PATH_LEN];
}CDS_FILE_STAT_EX_S;
'''