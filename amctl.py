#!/usr/bin/python
import sys
import os
import string
import subprocess

path_arr = os.path.realpath(sys.argv[0]).split('/')
path_arr.pop()
path_str = '/'.join(path_arr)

print(path_str)
print('Running in directory {}'.format(path_str))

os.chdir(path_str)

subprocess.call(['./amounter.py'])
