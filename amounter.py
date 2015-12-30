#!/usr/bin/python

#########################################################
# Copyright (c) 2015 by Steve Litt
#  
# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#########################################################

# Amounter thumb drive automount program, V0.2.0
# Version 0.2.0
# See README, INSTALL, AND BUGS files.


import sys
import types
import re
import os
import subprocess
import time

def mount_base():
    return('/media/')

class Relevant_lines():
    def __init__(self, proc):
        self.proc = proc
    EOF = False
    this_line_number = 0
    this_line_text = 'init'
    def is_relevant(self):
        return self.this_line_text.strip() != ''
    def tweak(self):
        return 0
    def nextt(self):
        self.this_line_text = self.proc.stdout.readline().decode('ascii')
        if self.this_line_text == '':
            self.EOF = True
        self.this_line_number += 1
        while not self.EOF and not self.is_relevant():
            self.this_line_text = self.proc.stdout.readline().decode('ascii')
            if self.this_line_text == '':
                self.EOF = True
            self.this_line_number += 1
        self.this_line_text = self.this_line_text.strip()
        if self.EOF:
            return -99, 'basura'
        else:
            self.tweak()
            return self.this_line_number, self.this_line_text


def main():

    class Rl_inotify(Relevant_lines):
        def is_relevant(self):
            #if re.match('/dev/pts/', self.this_line_text):
            #    return False
            #if re.match('/dev/input/', self.this_line_text):
            #    return False
            #if re.match('/dev/\s', self.this_line_text):
            #    return False
            #if re.search('.org.chromium.Chromium', self.this_line_text):
            #    return False
            #if re.match('/dev/block', self.this_line_text):
            #    return True
            #if re.match('/dev/dri/', self.this_line_text):
            #    return False
            #if not re.match('/dev/disk', self.this_line_text):
            #    return False
            #if not re.match('/dev/disk/by-path', self.this_line_text):
            #    return False

            
            #if re.search('\sATTRIB\s', self.this_line_text):
            #    return False
            if re.search('\sCREATE\s', self.this_line_text):
                return True
            if re.search('\sDELETE\s', self.this_line_text):
                return True
            return False
            #return True

    def id2dev(idstring):
        fname = '/dev/disk/by-id/' + idstring
        if os.path.islink(fname):
            devname = os.path.realpath(fname)
            return(devname)
        else:
            print('nosymlink')
            return('nosymlink')

    def dev2mountpoint(dev):
        junk = re.sub('.*/', '', dev)
        mountpoint = mount_base() + junk
        return mountpoint

    def init_id_dict():
        id_dict = {}
        for f in os.listdir('/dev/disk/by-id'):
            if re.match('usb-', f):
                devname = id2dev(f)
                id_dict[f] = devname
        return id_dict


    def run_commands(commands):
        for i in range(len(commands)):
            print(commands[i])
        print('\n\n')
        
    def handle_create(idstring, id_dict):
        dev = id2dev(idstring)
        if dev != 'nosymlink':
            if re.search('\d$', dev):     # Partition devs end with a digit
                mountpoint = dev2mountpoint(dev)
                devmountpoint = re.sub('\d*$', '*', mountpoint)
                
                ## Python2 compatible version of os.makedirs(mountpoint, exist_ok=True)
                try: 
                    os.makedirs(mountpoint)
                except OSError:
                    if not os.path.isdir(mountpoint):
                        raise
                subprocess.call(['mount', dev, mountpoint], stdout = open('/dev/null', 'w'))  ## subprocess.DEVNULL IS Py3 only
                tmp = 'Your inserted thumb drive mounted {} to {}.'
                tmp = tmp.format(dev, mountpoint)
                print(tmp)
                tmp = 'BE SURE to "umount {}" before removing this thumb drive!!!'
                tmp = tmp.format(devmountpoint)
                print(tmp)
                print('\n')

                ### SAVE idstring TO DEV SYMLINK
                ### BECAUSE BY DELETE TIME IT'S ALREADY GONE
                id_dict[idstring] = dev
                

    def handle_delete(idstring, id_dict):
        if idstring in id_dict:
            dev = id_dict[idstring]
            del id_dict[idstring]
            if re.search('\d$', dev):     # Partition devs end with a digit
                mountpoint = dev2mountpoint(dev)
                if re.match('/media/', mountpoint) and re.search('/dev/sd[b-z]\d\d*', dev):
                    subprocess.call(['umount', dev], stdout = open('/dev/null', 'w'))  ## subprocess.DEVNULL IS Py3 only
                    subprocess.call(['rmdir', mountpoint], stdout = open('/dev/null', 'w'))
                    print('form: umount {}'.format(dev))
        print('\n')



    id_dict = init_id_dict()
    #for k in id_dict.keys():
        #print('{}->{}: {}'.format(k, id_dict[k], dev2mountpoint(id_dict[k])))
    #exit(1)

    proc = subprocess.Popen(['/usr/bin/inotifywait', '-m', '-r', '/dev/disk/by-id'], stdout=subprocess.PIPE, bufsize=1)
    rl = Rl_inotify(proc)


    time.sleep(0.4)
    print('')
    print('Amounter Thumb Drive Automount Program now Running.')
    print('You can now insert thumb drives and they will automount in /media.')
    print('If earlier inserted thumb drives are not mounted,')
    print('You can remove and reinsert them.')
    print('')

    (lineno, txt) = rl.nextt()
    while lineno != -99:
        print(txt)
        tmp_arr = txt.split(None, 2) # constructed to work with Py2 or Py3
        if len(tmp_arr) > 2:
            (dev, fcn, otherstuff) = tmp_arr
        elif len(tmp_arr) > 1:
            (dev, fcn) = tmp_arr
            otherstuff = 'not given'
        elif len(tmp_arr) > 0:
            (dev) = tmp_arr
            fcn = 'no function'
            otherstuff = 'not given'
        else:
            dev = 'no device'
            fcn = 'no function'
            otherstuff = 'not given'
        if fcn == 'CREATE' and otherstuff != 'not given':
            handle_create(otherstuff, id_dict)
        if fcn == 'DELETE' and otherstuff != 'not given':
            handle_delete(otherstuff, id_dict)
        
        (lineno, txt) = rl.nextt()

main()
