#!/usr/bin/python3
import sys
import os
import string
import subprocess

path_arr = os.path.realpath(sys.argv[0]).split('/')
path_arr.pop()
path_arr = '/'.join(path_arr)

print(path_arr)

os.chdir(path_arr)

subprocess.call(['./amounter.py'])
