'''
Copyright (C), 2002-2007, Mark Bakker.
Mark Bakker
Water Resources Section
Faculty of Civil Engineering and Geosciences
TU Delft
Stevingweg 1, Delft, The Netherlands

TimML is a computer program for the simulation of steady-state
multiaquifer flow with analytic elements and consists of a
library of Python scripts and FORTRAN extensions.

TimML is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

TimML is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with TimML; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307,
USA, or go to http://www.gnu.org/copyleft/lesser.html
'''

print 'TimML version 3.1.beta1'
# Import all other files
from ml import *
from mlaquifer import *
from mlconstant import *
from mluflow import *
from mlwell import *
from mllinesink import *
from mlcircareasink import *
from mllinedoublet import *
from mlinhom import *
from mlcircinhom import *
from mlutilities import *
from mlholineelements import *
from mlpolyareasink import *
from mltrace import *
from mlholinesink import *
from mllinesinkgeneral import *

