#!/usr/bin/env python
# To use:
#	   python setup.py build
#	   python setup.py install
#	   python setup.py install --prefix=...
#	   python setup.py bdist --format=wininst
#	   python setup.py bdist --format=rpm
#	   python setup.py sdist --formats=gztar,zip

# This setup script authored by Philippe Le Grand, June 13th 2005

import sys

if not hasattr(sys, 'version_info') or sys.version_info < (2,3,0,'alpha',0):
	raise SystemExit, "Python 2.4 or later required to build TimML"


from distutils.core import setup, Extension

setup (name = "TimML",
	   extra_path = 'TimML',
	   version = "3.2.py24",
	   url="http://www.bakkerhydro.org/timml",
	   author="Mark Bakker",
	   author_email="markbak@gmail.com",
	   py_modules = ["example1",
					 "inhomex",
					 "squareinhom_man1",
					 "squareinhom_man2",
                                         "percolate",
                                         "imptest",
					 "ml",
					 "mlinhom",
					 "mlaquifer",
					 "mlcircareasink",
					 "mlcircinhom",
					 "mlconstant",
					 "mlelement",
                                         "mlellipinhom",
					 "mlholineelements",
					 "mlholinesink",
					 "mllinedoublet",
					 "mllinesink",
					 "mllinesinkgeneral",
                                         "mllinedoubletimp",
					 "mlpolyareasink",
                                         "mlpylabutil",
					 "mltrace",
					 "mluflow",
					 "mlutilities",
					 "mlwell",
                                         "TimMLgui",
                                         "TimMLmpl",
					 "TimML"],
# This trick might be original; I haven't found it anywhere.
# The precompiled Fortran library is passed as a data file,
# so that dist does not try and recompile on the destination machine
       data_files = [("Lib/site-packages/TimML",["besselaes.pyd","besselaes.f90","trace.ppm","capzone.ppm","back.ppm","filesave.ppm","forward.ppm","home.ppm","move.ppm","zoom_to_rect.ppm"])]
#	   ext_modules= [Extension("besselaes",["besselaes.f90","trianglemodule.c"])]
	   )
