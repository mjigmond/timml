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

#if not hasattr(sys, 'version_info') or sys.version_info < (2,3,0,'alpha',0):
#	raise SystemExit, "Python 2.5 or later required to build TimML"


from distutils.core import setup, Extension

setup (name = "timml",
	   extra_path = 'timml',
	   version = "3.4.0.py27",
	   author="Mark Bakker",
	   author_email="mark.bakker@tudelft.nl",
	   py_modules = ["example1",
					 "inhomex",
					 "squareinhom_man1",
					 "squareinhom_man2",
                                         "percolate",
                                         "imptest",
                                         "lake_example",
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
                                         "mllake",
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
       data_files = [("Lib/site-packages/timmL",["libgcc_s_dw2-1.dll","libgfortran-3.dll","libquadmath-0.dll","besselaes.pyd","besselaes.f90","trace.ppm","capzone.ppm","back.ppm","filesave.ppm","forward.ppm","home.ppm","move.ppm","zoom_to_rect.ppm"])]
#	   ext_modules= [Extension("besselaes",["besselaes.f90","trianglemodule.c"])]
	   )
