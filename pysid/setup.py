#!/usr/bin/env python3

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

import os

RESID_PATH = "resid-0.16/"

sdl_flags = os.popen('sdl-config --cflags').read().strip().split(' ')
sdl_libs = os.popen('sdl-config --libs').read().strip().split(' ')

module_pysid = Extension('pysid',
                sources = ['pysid.cpp'],
                extra_compile_args=sdl_flags + ['-O3','-I{}'.format(RESID_PATH),'-std=c++11','-std=c++11'],
                extra_link_args=['-lresid'] + sdl_libs

              )

setup (name = 'PySID',
       version = '0.0.0',
       description = 'Python SID',
       ext_modules = [module_pysid])
