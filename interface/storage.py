from django.core.files.storage import Storage
from django.conf import settings
from pyhdfs import hdfs
import os

hdfs.setConfig(hostname='dev-node1.limijiaoyin.com', username='songwei')
oneM = 1024*1024
blockSizeTable = [oneM, oneM*2, oneM*4, oneM*8, oneM*16, oneM*32]
maxBlockSize = oneM*64

class HdfsStorage(Storage):
    def __init__(self, option=None):
        if not option:
            pass
            #option = settings.CUSTOM_STORAGE_OPTIONS

    def listdir(self, path):
        result = hdfs.listDirectory(path)
        dirs = []
        files = []
        for i in result:
            if i.fileType == 'DIRECTORY':
                dirs.append(i.path)
            else:
                files.append(i.path)
        return (dirs, files, )

    def size(self, name):
        return hdfs.getFileStatus(name).length

    def exist(self, path):
        try:
            hdfs.getFileStatus(path)
            return True
        except:
            return False

    def delete(self, name):
        hdfs.remove(name, True)

    def create(self, destpath, srcpath):
        blkSize = 0
        size = os.path.getsize(srcpath)
        for i in blockSizeTable:
            if size <= i:
                blkSize = i
                break
        else:
            blkSize = maxBlockSize
        hdfs.putFile(srcpath, destpath, overwrite=True, str(blkSize))

    def open(self, name, mode='rb'):
        pass

    def save(self, name, content):
        pass

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, mode='wb'):
        pass