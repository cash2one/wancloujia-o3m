from django.core.files.storage import Storage, FileSystemStorage
from django.conf import settings
from pyhdfs import hdfs
import os

oneM = 1024*1024
blockSizeTable = [oneM, oneM*2, oneM*4, oneM*8, oneM*16, oneM*32]
maxBlockSize = oneM*64

class hdfs_storage(FileSystemStorage):   #(Storage):
    def __init__(self, option=None):
        if not option:
            pass
            #option = settings.CUSTOM_STORAGE_OPTIONS

    def listdir(self, path):
        result = hdfs.listDirectory(path.encode('utf8'))
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
            hdfs.getFileStatus(path.encode('utf8'))
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
        hdfs.putFile(srcpath, destpath, overwrite=True, blocksize=str(blkSize))

    def block(self, path, offset, length):
        return hdfs.readFile(path, str(offset), str(length))

    def enum_file(self, path, offset, step_length=1024*128):
        class hdfs_readstream_enumable:
            def __init__(self, path, offset=0, step_length=1024*1024):
                dfs = hdfs_storage()
                size = dfs.size(path)
                self.size = size
                self.path = path
                self.dfs = dfs
                self.remain = size - offset
                self.step_length = step_length
                self.offset = offset
            def __iter__(self):
                return self
            def next(self):
                if self.remain <= 0:
                    raise StopIteration()
                for i in range(3):
                    result = self.dfs.block(self.path, self.offset, self.step_length)
                    break
                self.offset += self.step_length
                self.remain -= self.step_length
                return result
        result = hdfs_readstream_enumable(path, offset, step_length)
        return result

