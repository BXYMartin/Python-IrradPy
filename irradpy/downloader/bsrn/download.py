#!/usr/bin/env python
# encoding: utf-8

import ftplib
import os
import traceback
from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed


class FtpDownloader(object):
    PATH_TYPE_UNKNOWN = -1
    PATH_TYPE_FILE = 0
    PATH_TYPE_DIR = 1

    def __init__(self, host, user=None, passwd=None, port=21, timeout=10):
        self.conn = ftplib.FTP(
            host=host,
            user=user,
            passwd=passwd,
            timeout=timeout
        )
        print(self.conn.getwelcome())

    def dir(self, *args):
        '''
        by defualt, ftplib.FTP.dir() does not return any value.
        Instead, it prints the dir info to the stdout.
        So we re-implement it in FtpDownloader, which is able to return the dir info.
        '''
        info = []
        cmd = 'LIST'
        for arg in args:
            if arg:
                cmd = cmd + (' ' + arg)
        print('\rHost %s: Getting Directory Info %s' % (self.conn.host, cmd), end="")
        self.conn.retrlines(cmd, lambda x: info.append(x.strip().split()))
        return info

    def syncIndex(self, meta_data):
        for site in meta_data:
            path = os.path.join('.', site["code"].lower())
            dir_info = self.dir(path)
            file_info = []
            for info in dir_info:
                attr = info[0]
                name = info[-1]
                if attr.startswith('-'):
                    print(attr)
                    file_info.append()

    def tree(self, rdir=None, init=True):
        '''
        recursively get the tree structure of a directory on FTP Server.
        args:
            rdir - remote direcotry path of the FTP Server.
            init - flag showing whether in a recursion.
        '''
        if init and rdir in ('.', None):
            rdir = self.conn.pwd()
        tree = []
        tree.append((rdir, self.PATH_TYPE_DIR))

        dir_info = self.dir(rdir)

        for info in dir_info:
            attr = info[0]  # attribute
            name = info[-1]
            if rdir.endswith("/"):
                path = rdir + name
            else:
                path = rdir + "/" + name
            if attr.startswith('-'):
                tree.append((path, self.PATH_TYPE_FILE))
            elif attr.startswith('d'):
                if (name == '.' or name == '..'):  # skip . and ..
                    continue
                tree.extend(self.tree(rdir=path,init=False))  # recurse
            else:
                tree.append(path, self.PATH_TYPE_UNKNOWN)

        return tree

    def downloadFile(self, rfile, lfile):
        '''
        download a file with path %rfile on a FTP Server and save it to locate
        path %lfile.
        '''
        ldir = os.path.dirname(lfile)
        if not os.path.exists(ldir):
            os.makedirs(ldir)
        n = 5
        i = 0
        while i < n:
            i = i + 1
            try:
                size = self.conn.size(rfile)
                if os.path.exists(lfile):
                    if os.path.getsize(lfile) == size:
                        print('Host %s: Skipping Existing File %s on %s' % (
                                self.conn.host,
                                lfile,
                                rfile
                            ))
                        return True
                    else:
                        print('Host %s: Detected Corrupted File %s on %s with %dKB/%dKB' % (
                                self.conn.host,
                                lfile,
                                rfile,
                                os.path.getsize(lfile)/1024,
                                size/1024
                            ))
                widgets = ['Downloading %s: ' % rfile, Percentage(), ' ', Bar(marker='#',left='[',right=']'), ' ', ETA(), ' ', FileTransferSpeed()]
                pbar = ProgressBar(widgets=widgets, maxval=size)
                pbar.start()
                f = open(lfile, 'wb')

                def file_write(data):
                    f.write(data)
                    pbar.update(pbar.currval + len(data))
                self.conn.retrbinary('RETR %s' % rfile, file_write)
                f.close()
                pbar.update()
                pbar.finish()
                return True
            except Exception:
                print('%d Attempt %s on %s' % (i, lfile, rfile))
        print('Host %s: Download Failed %s on %s' % (self.conn.host, lfile, rfile))
        traceback.print_exc()
        raise RuntimeError('Connection Error')

    def treeStat(self, tree):
        numDir = 0
        numFile = 0
        numUnknown = 0
        for path, pathType in tree:
            if pathType == self.PATH_TYPE_DIR:
                numDir += 1
            elif pathType == self.PATH_TYPE_FILE:
                numFile += 1
            elif pathType == self.PATH_TYPE_UNKNOWN:
                numUnknown += 1
        return numDir, numFile, numUnknown

    def downloadDir(self, rdir='.', ldir='.', tree=None,
                    errHandleFunc=None, verbose=True):
        '''
        download a direcotry with path %rdir on a FTP Server and save it to
        locate path %ldir.
        args:
            tree - the tree structure return by function FtpDownloader.tree()
            errHandleFunc - error handling function when error happens in
                downloading one file, such as a function that writes a log.
                By default, the error is print to the stdout.
        '''
        if not tree:
            tree = self.tree(rdir=rdir, init=True)
        numDir, numFile, numUnknown = self.treeStat(tree)
        if verbose:
            print('Host %s: Tree Statistic:' % self.conn.host)
            print('%d Directories, %d Files, %d unknown type' % (
                numDir,
                numFile,
                numUnknown
            ))

        if not os.path.exists(ldir):
            os.makedirs(ldir)
        ldir = os.path.abspath(ldir)

        numDownOk = 0
        numDownErr = 0
        for rpath, pathType in tree:
            lpath = os.path.join(ldir, rpath.strip('/').strip('\\'))
            if pathType == self.PATH_TYPE_DIR:
                if not os.path.exists(lpath):
                    os.makedirs(lpath)
            elif pathType == self.PATH_TYPE_FILE:
                try:
                    self.downloadFile(rpath, lpath)
                    numDownOk += 1
                except Exception as err:
                    numDownErr += 1
                    if errHandleFunc:
                        errHandleFunc(err, rpath, lpath)
                    elif verbose:
                        print('An Error Occurred When Downloading '\
                              'Remote File %s' % rpath)
                        traceback.print_exc()
                if verbose:
                    print('Host %s: %d/%d/%d(OK/Error/Total) Files Downloaded' % (
                        self.conn.host,
                        numDownOk,
                        numDownErr,
                        numFile
                    ))
            elif pathType == self.PATH_TYPE_UNKNOWN:
                if verbose:
                    print('Unknown Type Remote Path Got: %s' % rpath)

        if verbose:
            print('Host %s Directory %s Download Finished:' % (
                self.conn.host, rdir
            ))
            print('%d Directories, %d(%d Failed) Files, %d Unknown Type.' % (
                numDir,
                numFile,
                numDownErr,
                numUnknown
            ))
        return numDir, numFile, numUnknown, numDownErr
