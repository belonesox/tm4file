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
import json
import atomic_transformation as at 
# import pyfastcopy
import exif

from plum.exceptions import UnpackError

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
    scmd = f'''ffmpeg -i '{src}' -pix_fmt yuv420p -loglevel error -stats -hide_banner -vcodec h264_nvenc -qp 0 -acodec copy -f avi '{dst}' '''
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

    def __init__(self, recode=None, exif=None, #lightmeta=None, 
                    noimage=False):
        """Set up and parse command line options"""
        usage = "Usage: %prog [options] <source directory>"

        self.homedir = os.getcwd()
        self.recode = recode
        self.exif = exif
        self.lightmeta = None #lightmeta
        self.noimage =  noimage
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

                if self.noimage and ext.lower() in img_ext:
                    continue

                if ext.lower() in img_ext:
                    dfsdfdsf  =1 

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

                    right_time_datetime = time.localtime(right_time)    
                    lightmeta_ok = False
                    newfilename = os.path.join(self.homedir, filename)

                    def remove_dt_prefix(fname):
                        prefixes_ = [
                           ('%Y-%m-%d %H.%M.%S', 19), 
                           ('%Y-%m-%d-%H-%M-%S', 19), 
                           ('%Y-%m-%d', 10)
                        ]    
                        
                        for pref, n in prefixes_:
                            try:
                                startprefix = fname[:n]
                                date_ = time.strptime(startprefix, pref) 
                                return fname[n:]
                            except:
                                pass    

                        return fname                                                

                    # if self.lightmeta:
                    #     try:
                    #         startprefix = filename[:10]
                    #         date_ = time.strptime(startprefix, '%Y-%m-%d') 
                    #         lightmeta_ok = True
                    #     except:
                    #         pass    

                    # if not lightmeta_ok:                                
                    if (self.exif or self.lightmeta) and ext.lower() in img_ext:
                        with open(filepath, 'rb') as image_file:
                            try:
                                img_ = exif.Image(image_file)    
                                all_atrs = img_.list_all()
                                dt_at = None
                                for dt_at in ['datetime_original', 'datetime_digitized', 'datetime']:
                                    if dt_at in all_atrs:                    
                                        right_time_datetime = time.strptime(img_[dt_at], '%Y:%m:%d %H:%M:%S')
                                        break

                            except UnpackError as ex_:
                                ddd = 1
                                pass        

                    if (self.exif or self.lightmeta) and ext.lower() in video_ext:
                        scmd = f'ffprobe -v quiet "{filepath}"  -print_format json -show_entries stream=index,codec_type:format_tags=creation_time'
                        process = subprocess.Popen(scmd, shell=True, stdout=subprocess.PIPE)
                        process.wait()
                        json_str_, _ = process.communicate()
                        d = json.loads(json_str_)   
                        if 'format' in d:
                            fmt_ = d["format"]
                            if "tags" in fmt_:
                                tags_ = fmt_["tags"]
                                if "creation_time" in tags_:
                                    ct_ = tags_["creation_time"][:19]                 
                                    right_time_datetime = time.strptime(ct_, '%Y-%m-%dT%H:%M:%S')

                    newfilename = os.path.join(self.homedir,
                        time.strftime("%Y-%m-%d-%H-%M-%S", right_time_datetime) +
                        remove_dt_prefix(name) + ext)
                   
                    rdp_ = remove_dt_prefix(name)
                    newf_ = time.strftime("%Y-%m-%d-%H-%M-%S", right_time_datetime)
                    if rdp_:
                        newf_ += '-' + rdp_
                    newfilename = os.path.join(self.homedir, newf_ + ext)
                    newfilename = newfilename.lower()                         

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


