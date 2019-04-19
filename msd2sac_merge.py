## convert the miniseed-files/seed-files into sac-files, and merge 
## 2019/04/19
#

import os, glob, shutil
os.putenv("SAC_DISPLAY_COPYRIGHT", '0')
import subprocess
from obspy.core import *


def merge(net, sta, year, jday, chn):
    p  = subprocess.Popen(['sac'], stdin=subprocess.PIPE)
    s  = "wild echo off \n"
    s += "r *.%s.* \n" %chn                  
    s += "merge g z o a \n"
    s += "w %s.%s.%s.%s.%s.SAC \n" %(net, sta, year, jday, chn)
    s += "q \n"
    p.communicate(s.encode())

def slice_stream(fname, begin, end, ts, out_path):
    p  = subprocess.Popen(['sac'], stdin=subprocess.PIPE)
    s  = "wild echo off \n"
    s += "cuterr fillz \n"
    s += "cut b %s %s \n" %(begin, end)
    s += "r %s \n" %fname
    s += "ch b 0 \n"
    s += "ch nzhour %s nzmin %s nzsec %s nzmsec %s \n" %(ts.hour,
                                                         ts.minute,
                                                         ts.second,
                                                         ts.microsecond/1000)
    s += "ch nzyear %s nzjday %s \n" %(ts.year, ts.julday)
    s += "w %s \n" %out_path
    s += "q \n"
    p.communicate(s.encode())


out_path0  = '/mnt/bashi_fs/sac_data'
src_dirs   = sorted(glob.glob('/mnt/bashi_fs/ppk_data/2*/N*/*/*/*'))

for src_dir in src_dirs:
    os.chdir(src_dir)
    print('entering {}'.format(src_dir))
    print(src_dir)
    # miniseed/seed to sac
    print('read seed/miniseed files, convert to SAC')
    msd_files = sorted(glob.glob('*.miniseed'))
    if len(msd_files) == 0:print('missing trace!');continue
    for msd_file in msd_files:
        subprocess.call(['mseed2sac',msd_file])
    todel = glob.glob('*SAC')
    # merge
    p = subprocess.Popen(['sac'],stdin=subprocess.PIPE)
    s = "wild echo off \n"
    for chn in ['BHZ','BHY','BHX','HHX','HHY','HHZ']:
        sac_files = sorted(glob.glob('*.%s.*.SAC'%chn))
        if len(sac_files)==0:continue 
        #YS.N5..HHX.D.2018.064.083423.SAC
        net,sta,_,chn,qq,year,jday,secs,sac = sac_files[0].split('.')
        print('merge %s.%s.%s.%s'%(net,sta,chn,jday))
        
        s += "r *.%s.*SAC \n" %(chn)
        s += "merge g z o a \n"
        s += "w %s.%s.%s.%s.%s.SAC \n" %(net,sta, year, jday, chn)
    s += "q \n"
    p.communicate(s.encode())

    for fname in todel:
        os.unlink(fname)

    # archive into /sac_data
    # print('archive into sac_data')
    # archive (mkdir + mv )
    date = UTCDateTime('%s,%s'%(year, jday))
    mon,day = str(date.month).zfill(2), str(date.day).zfill(2)
    out_path = os.path.join(out_path0, sta, year, mon, day) 
    print('archive into {}'.format(out_path))
    if not os.path.exists(out_path):
       os.makedirs(out_path)
    for sac_file in glob.glob('*SAC'):
        if os.path.exists(os.path.join(out_path, sac_file)):
           continue
        shutil.move(sac_file, out_path)

