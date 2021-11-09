"""Main module."""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Time 4 Files

  Copy all files from given directory,
  trying extract creation time,
  and append this time info to
"""

import sys
import os
import optparse
import time
import shutil
import datetime
import atomic_transformation as at 
import pyfastcopy


class CTError(Exception):
    def __init__(self, errors):
        self.errors = errors

try:
    O_BINARY = os.O_BINARY
except:
    O_BINARY = 0
READ_FLAGS = os.O_RDONLY | O_BINARY
WRITE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY
BUFFER_SIZE = 8*1024*1024

def copyfile(src, dst):
    try:
        fin = os.open(src, READ_FLAGS)
        stat = os.fstat(fin)
        fout = os.open(dst, WRITE_FLAGS, stat.st_mode)
        for x in iter(lambda: os.read(fin, BUFFER_SIZE), ""):
            os.write(fout, x)
        wtf = 1
        pass    
    finally:
        try: os.close(fin)
        except: pass
        try: os.close(fout)
        except: pass

import subprocess
import shlex

def recode_video(src, dst):
    scmd = f'''ffmpeg -i '{src}' -pix_fmt yuv420p  -vcodec h264_nvenc -qp 0 -acodec copy -f avi '{dst}' '''
    try:
        print(scmd)
        subprocess.run(shlex.split(scmd), shell=False, stderr=sys.stderr, stdout=sys.stdout)
    except subprocess.CalledProcessError as ex_:
        return False
    return True

video_ext = set(['.mts', '.avi', '.mp4', '.mov', '.ts'])
audio_ext = set([ '.wav', '.mp3' ])
img_ext = set(['.jpg', '.png', '.tiff' ])


class Time4Files(object):
    """
    Main class for all commands
    """
    version__ = "01.02"

    def __init__(self, recode=None):
        """Set up and parse command line options"""
        usage = "Usage: %prog [options] <source directory>"

        self.homedir = os.getcwd()
        self.recode = recode
        self.known_extensions = video_ext | audio_ext | img_ext 

        pass    

    def process(self, source_directory):
        """
        Main entry point.
        Process command line options, call appropriate logic.
        """
        if not os.path.exists(source_directory):
            print('Directory "%s" not exists ' % source_directory)
            sys.exit(0)

        #os.chdir(source_directory)
        for root, _dirnames, filenames in os.walk(source_directory):
            for filename in filenames:
                name, ext = os.path.splitext(filename)
                if ext.lower() in self.known_extensions:
                    filepath = os.path.join(root, filename)
                    ctime = os.stat(filepath).st_ctime
                    mtime = os.stat(filepath).st_mtime
                    _dt = datetime.datetime.fromtimestamp(mtime)
                    if _dt.year>time.localtime().tm_year:
                        _dt = _dt.replace(year=time.localtime().tm_year)
                        mtime = time.mktime(_dt.timetuple())
                        
                    right_time = min(ctime, mtime )
                    if self.recode and ext.lower() in video_ext:
                        ext = '.avi'

                    newfilename = os.path.join(self.homedir,
                        time.strftime("%Y-%m-%d-%H-%M-%S-", time.localtime(right_time)) +
                        name + ext)

                    def _do(target, source):
                        """
                          simple copying
                        """
                        print("start:", source, "->", target)
                        try:
                            if self.recode and ext.lower() in video_ext:
                                recode_video(source, target)
                            else:        
                                shutil.copyfile(source, target)
                        except:
                            print("Troubles!!!!!!")
                        print("end:", source, "->", target)
                        return True

                    at.transaction(newfilename, filepath, _do)

        os.chdir(self.homedir)


