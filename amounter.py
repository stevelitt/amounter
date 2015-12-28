#!/usr/bin/python3
import sys
import types
import re
import os
import subprocess

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


def inotify_test():

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
                print('About to perform: os.makedirs({}, exist_ok=True)'.format(mountpoint))
                os.makedirs(mountpoint, exist_ok=True)
                print('About to perform: mount {} {}'.format(dev, mountpoint))
                subprocess.call(['mount', dev, mountpoint], stdout = subprocess.DEVNULL)

                ### SAVE idstring TO DEV SYMLINK
                ### BECAUSE BY DELETE TIME IT'S ALREADY GONE
                id_dict[idstring] = dev
                

    def handle_delete(idstring, id_dict):
        print('dia1')
        if idstring in id_dict:
            print('dia2')
            dev = id_dict[idstring]
            del id_dict[idstring]
            if re.search('\d$', dev):     # Partition devs end with a digit
                mountpoint = dev2mountpoint(dev)
                print('dia3 mountpoint={} and dev={}'.format(mountpoint, dev))
                if re.match('/media/', mountpoint) and re.search('/dev/sd[b-z]\d\d*', dev):
                    print('dia4')
                    print('About to perform: umount {}'.format(dev))
                    subprocess.call(['umount', dev], stdout = subprocess.DEVNULL)
                    print('About to perform: rmdir {}'.format(mountpoint))
                    subprocess.call(['rmdir', mountpoint], stdout = subprocess.DEVNULL)



    id_dict = init_id_dict()
    #for k in id_dict.keys():
        #print('{}->{}: {}'.format(k, id_dict[k], dev2mountpoint(id_dict[k])))
    #exit(1)

    proc = subprocess.Popen(['/usr/bin/inotifywait', '-m', '-r', '/dev/disk/by-id'], stdout=subprocess.PIPE, bufsize=1)
    rl = Rl_inotify(proc)



    (lineno, txt) = rl.nextt()
    while lineno != -99:
        print(txt)
        tmp_arr = txt.split(maxsplit=2)
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
        
        #print('dev={}'.format(dev))
        #print('fcn={}'.format(fcn))
        #print('otherstuff={}'.format(otherstuff))
        #print('')
        (lineno, txt) = rl.nextt()
inotify_test()
