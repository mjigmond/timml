# TimML #
## A multi-aquifer, analytic element model ##

TimML is a computer program for the modeling of steady-state multi-aquifer flow with analytic elements and consists of a library of Python scripts and FORTRAN extensions. TimML may be applied to an arbitrary number of aquifers and leaky layers. The head, flow, and leakage between aquifers may be computed analytically at any point in the aquifer system. The design of TimML is object-oriented and has been kept simple and flexible. New analytic elements may be added to the code without making any changes in the existing part of the code. TimML is coded in Python, a free, open-source, powerful programming language; use is made of FORTRAN extensions to improve performance. TimML is free and open-source software and is released under the GNU Lesser General Public License.

Download options include the TimML program and the manual. The manual contains full instructions on how to run TimML. The objective of the manual is to provide enough information for someone familiar with the analytic element method to use (and possibly modify) the program. Running TimML and especially modifying TimML requires some knowledge of Python. Python is very easy to learn. A number of free tutorials are available from the Python website.

TimML version 3.4 is out! TimML 3.4 has interactive graphical output that allow you to evaluate the results of your TimML model graphically and easily.

Note that since version 3.3, TimML requires installation of the matplotlib and shapely packages. Detailed installation instructions are given in the manual. TimML also runs on MacOSX. A compiled FORTRAN extension can be obtained from Mark Bakker. The FORTRAN file is available under the source tab if you want to do it yourself.

**Binary installers for 32bit and 64bit Python are available from:** https://bintray.com/mbakker7/Groundwater/