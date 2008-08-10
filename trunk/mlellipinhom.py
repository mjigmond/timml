'''
mlcircinhom.py contains the CircleInhom class
This file is part of the TimML library and is distributed under
the GNU LPGL. See the TimML.py file for more details.
(c) Mark Bakker, 2002
'''

from Numeric import *
import LinearAlgebra
from mlelement import *
from mathieufuncs import *

class EllipseInhom(Element):
    '''EllipInhom class
    Note that aquiferparent doesn't have a meaning for this element
    All attributes from element.
    '''
    def __init__(self,modelParent,order,aqin,aqout):
	Element.__init__(self,modelParent)
	self.modelParent.addElement(self)
	self.order = order
        self.aqin = aqin; self.aqout = aqout; self.outwardNormal = self.aqin.outwardNormal
        self.xytoetapsi = self.aqin.xytoetapsi; self.etapsitoxy = self.aqin.etapsitoxy
        assert aqin.Naquifers == aqout.Naquifers, "TimML Input error: Number of aquifers inside and outside must be equal"
        self.type = 'ellipseinhom'
	self.setCoefs()
    def __repr__(self):
	return 'EllipInhom xc,yc,order ' + str((self.xc,self.yc,self.order)) + ' with inside aquifer data ' + str(self.aqin)
    def setCoefs(self):
        self.xc = self.aqin.xc; self.yc = self.aqin.yc; self.afoc = self.aqin.afoc; self.angle = self.aqin.angle
        self.along = self.aqin.along; self.bshort = self.aqin.bshort; self.etastar = self.aqin.etastar;
        self.zc = self.aqin.zc
        self.afocOverLabIn = self.afoc / self.aqin.lab; self.afocOverLabOut = self.afoc / self.aqout.lab
        self.paramin = zeros((2*self.order+1,self.aqin.Naquifers),'d') 
        self.paramout = zeros((2*self.order+1,self.aqin.Naquifers),'d') 
        self.Nparamin = ( 2*self.order+1 ) * self.aqin.Naquifers; self.Nparamout = self.Nparamin
        # Compute control points
        self.Ncp = 2 * self.order + 1
        angles = arange( 0, 2*pi-0.01, 2*pi/self.Ncp )
        [self.xcp, self.ycp] = self.etapsitoxy(self.etastar, angles)
        self.thetacp = zeros(self.Ncp,'d')
        for i in range(self.Ncp):
            self.thetacp[i] = self.aqin.outwardNormalAngle(self.xcp[i],self.ycp[i])
        # Compute values on the edge (to scale functions)
        # STILL GOTTA DO THAT
##        self.matRin = zeros( (self.order+1,self.aqin.Naquifers), 'd' )  # values on inside edge
##        rolab = self.R/self.aqin.lab  # vector with all R/labin values
##        for p in range(self.order+1):
##            self.matRin[p,0] = self.R**p  # first value in row is R**p
##            self.matRin[p,1:] = scipy.special.iv(p,rolab) # other values are Ip(R/lab)
##        self.matRin = 1.0 / self.matRin
##        self.matRout = zeros( (self.order+1,self.aqout.Naquifers), 'd' )  # values on outside edge
##        rolab = self.R/self.aqout.lab  # vector with all R/labout values
##        for p in range(self.order+1):
##            self.matRout[p,0] = 1./self.R**(p)  # first value in row is 1/r**p
##            self.matRout[p,1:] = scipy.special.kn(p,rolab) # other values are Kp
##        self.matRout = 1.0 / self.matRout
    def potentialInfluence(self,aq,x,y):
        [eta,psi] = self.xytoetapsi(x,y)
        rv = zeros( (2*self.order+1,aq.Naquifers), 'd' )
     # Inside Cylinder
        if aq == self.aqin:
            if aq.type == aq.conf:
                rv[0,0] = 1.0 # p=0, cosine part (a constant)
                for q in range(1,self.aqin.Naquifers):
                    # This is slightly funny since the even term will have one power more (there really is no power 0!)
                    rv[0,q] = MathieuQe( psi, 0, self.afocOverLabIn[q-1] ) * MathieuIe( eta, 0, self.afocOverLabIn[q-1] )
                for p in range(1,self.order+1):
                    rv[2*p-1,0] = cosh( p*eta ) * cos( p*psi )
                    rv[2*p,0]   = sinh( p*eta ) * sin( p*psi )
                    for q in range(1,self.aqin.Naquifers):
                        rv[2*p-1,q] = MathieuQe( psi, p, self.afocOverLabIn[q-1] ) * MathieuIe( eta, p, self.afocOverLabIn[q-1] )  # Add Mathieu Function Here
                        rv[2*p,q]   = MathieuQo( psi, p, self.afocOverLabIn[q-1] ) * MathieuIo( eta, p, self.afocOverLabIn[q-1] )  # Add Mathieu Function Here
                # May need some correction on values from edge here
            elif aq.type == aq.semi:
                for q in range(0,self.aqin.Naquifers):
                    # This is slightly funny since the even term will have one power more (there really is no power 0!)
                    rv[0,q] = MathieuQe( psi, 0, self.afocOverLabIn[q] ) * MathieuIe( eta, 0, self.afocOverLabIn[q] )
                for p in range(1,self.order+1):
                    for q in range(0,self.aqin.Naquifers):
                        rv[2*p-1,q] = MathieuQe( psi, p, self.afocOverLabIn[q] ) * MathieuIe( eta, p, self.afocOverLabIn[q] )  # Add Mathieu Function Here
                        rv[2*p,q]   = MathieuQo( psi, p, self.afocOverLabIn[q] ) * MathieuIo( eta, p, self.afocOverLabIn[q] )  # Add Mathieu Function Here
                # May need some correction on values from edge here                
     # In aquifer outside cylinder
        elif aq == self.aqout: 
            if aq.type == aq.conf:
                rv[0,0] = eta # Flow to ellipse is possible; this is like the log term
                for q in range(1,self.aqin.Naquifers):
                    # This is slightly funny since the even term will have one power more (there really is no power 0!)
                    rv[0,q] = MathieuQe( psi, 0, self.afocOverLabOut[q-1] ) * MathieuKe( eta, 0, self.afocOverLabOut[q-1] )
                for p in range(1,self.order+1):
                    rv[2*p-1,0] = exp( -p*eta ) * cos( p*psi )
                    rv[2*p,0]   = exp( -p*eta ) * sin( p*psi )
                    for q in range(1,self.aqin.Naquifers):
                        rv[2*p-1,q] = MathieuQe( psi, p, self.afocOverLabOut[q-1] ) * MathieuKe( eta, p, self.afocOverLabOut[q-1] )  # Add Mathieu Function Here
                        rv[2*p,q]   = MathieuQo( psi, p, self.afocOverLabOut[q-1] ) * MathieuKo( eta, p, self.afocOverLabOut[q-1] )  # Add Mathieu Function Here
                 # May need some correction on values from edge here
            elif aq.type == aq.semi:
                for q in range(0,self.aqin.Naquifers):
                    # This is slightly funny since the even term will have one power more (there really is no power 0!)
                    rv[0,q] = MathieuQe( psi, 0, self.afocOverLabOut[q] ) * MathieuKe( eta, 0, self.afocOverLabOut[q] )
                for p in range(1,self.order+1):
                    for q in range(0,self.aqin.Naquifers):
                        rv[2*p-1,q] = MathieuQe( psi, p, self.afocOverLabOut[q] ) * MathieuKe( eta, p, self.afocOverLabOut[q] )  # Add Mathieu Function Here
                        rv[2*p,q]   = MathieuQo( psi, p, self.afocOverLabOut[q] ) * MathieuKo( eta, p, self.afocOverLabOut[q] )  # Add Mathieu Function Here
                 # May need some correction on values from edge here                
      # Somewhere else
        elif self.aqout.type == self.aqout.conf and aq.type == aq.conf:
            rv[0,0] = eta # Flow to ellipse is possible
            for p in range(1,self.order+1):
                rv[2*p-1,0] = exp( -p*eta ) * cos( p*psi )
                rv[2*p,0]   = exp( -p*eta ) * sin( p*psi )
            # May need some correction on values from edge here
        return rv
    def potentialInfluenceInLayer(self,aq,pylayer,x,y,z=0):
        '''Returns PotentialInfluence function in aquifer aq in pylayer as array (1 value per parameter)
        Needs to be overloaded because there is no parameter outside the functions
        Needs to be modified for inside and outside'''
        potInf = self.potentialInfluence(aq,x,y)
        rv = zeros(0,'d')
        for p in potInf:
            rv = hstack(( rv, p * aq.eigvec[pylayer,:] ))
        if aq == self.aqin:
            rv = hstack(( rv, zeros( self.Nparamout, 'd' ) ))
        else:
            rv = hstack(( zeros( self.Nparamin, 'd' ), rv )) 
        return rv
    def potentialInfluenceAllLayers(self,aq,pylayer,x,y):
        '''Returns PotentialInfluence function in aquifer aq in all layers as an array'''
        potInf = self.potentialInfluence(aq,x,y)
        rv = zeros((aq.Naquifers,0),'d')
        for p in potInf:
            rv = hstack( ( rv, p * aq.eigvec ) )
        if aq == self.aqin:
            rv = hstack(( rv, zeros( ( aq.Naquifers, self.Nparamout ), 'd' ) ))
        else:
            rv = hstack(( zeros( (aq.Naquifers,self.Nparamin), 'd' ), rv ))
        return rv
    def potentialContribution(self,aq,x,y):
        '''Returns array of potentialContribution. Needs to be overloaded cause there is inside and outside'''
        if aq == self.aqin:
            potInf = sum( self.paramin * self.potentialInfluence(aq,x,y) )
        else:
            potInf = sum( self.paramout * self.potentialInfluence(aq,x,y) )
        return potInf
    def dischargeInfluence(self,aq,x,y):
        [eta,psi] = self.xytoetapsi(x,y)   # Don't know if I need this yet
     # Store values in return value
        qeta = zeros( (2*self.order+1,aq.Naquifers), 'd' )
        qpsi = zeros( (2*self.order+1,aq.Naquifers), 'd' )
        if aq == self.aqin:  # Inside cylinder
            if aq.type == aq.conf:
                qeta[0,0] = 0.0 # p=0, cosine part (derivative of a constant)
                qpsi[0,0] = 0.0
                for q in range(1,self.aqin.Naquifers):
                    # This is slightly funny since the even term will have one power more (there really is no power 0!)
                    qeta[0,q] = MathieuQe( psi, 0, self.afocOverLabIn[q-1] ) * MathieuIeD( eta, 0, self.afocOverLabIn[q-1] )
                    qpsi[0,q] = MathieuQeD( psi, 0, self.afocOverLabIn[q-1] ) * MathieuIe( eta, 0, self.afocOverLabIn[q-1] )
                for p in range(1,self.order+1):
                    sinhcos = float(p) * sinh( p*eta ) * cos( p*psi )
                    coshsin = float(p) * cosh( p*eta ) * sin( p*psi )
                    qeta[2*p-1,0] =  sinhcos; qeta[2*p,0] = coshsin
                    qpsi[2*p-1,0] = -coshsin; qpsi[2*p,0] = sinhcos
                    for q in range(1,self.aqin.Naquifers):
                        qeta[2*p-1,q] = MathieuQe( psi, p, self.afocOverLabIn[q-1] ) * MathieuIeD( eta, p, self.afocOverLabIn[q-1] )  # Add Mathieu Function Here
                        qeta[2*p,q]   = MathieuQo( psi, p, self.afocOverLabIn[q-1] ) * MathieuIoD( eta, p, self.afocOverLabIn[q-1] )  # Add Mathieu Function Here
                        qpsi[2*p-1,q] = MathieuQeD( psi, p, self.afocOverLabIn[q-1] ) * MathieuIe( eta, p, self.afocOverLabIn[q-1] )  # Add Mathieu Function Here
                        qpsi[2*p,q]   = MathieuQoD( psi, p, self.afocOverLabIn[q-1] ) * MathieuIo( eta, p, self.afocOverLabIn[q-1] )  # Add Mathieu Function Here
                # May need some correction on values from edge here
            elif aq.type == aq.semi:
                for q in range(0,self.aqin.Naquifers):
                    # This is slightly funny since the even term will have one power more (there really is no power 0!)
                    qeta[0,q] = MathieuQe( psi, 0, self.afocOverLabIn[q] ) * MathieuIeD( eta, 0, self.afocOverLabIn[q] )
                    qpsi[0,q] = MathieuQeD( psi, 0, self.afocOverLabIn[q] ) * MathieuIe( eta, 0, self.afocOverLabIn[q] )
                for p in range(1,self.order+1):
                    for q in range(0,self.aqin.Naquifers):
                        qeta[2*p-1,q] = MathieuQe( psi, p, self.afocOverLabIn[q] ) * MathieuIeD( eta, p, self.afocOverLabIn[q] )  # Add Mathieu Function Here
                        qeta[2*p,q]   = MathieuQo( psi, p, self.afocOverLabIn[q] ) * MathieuIoD( eta, p, self.afocOverLabIn[q] )  # Add Mathieu Function Here
                        qpsi[2*p-1,q] = MathieuQeD( psi, p, self.afocOverLabIn[q] ) * MathieuIe( eta, p, self.afocOverLabIn[q] )  # Add Mathieu Function Here
                        qpsi[2*p,q]   = MathieuQoD( psi, p, self.afocOverLabIn[q] ) * MathieuIo( eta, p, self.afocOverLabIn[q] )  # Add Mathieu Function Here
                # May need some correction on values from edge here                
        elif aq == self.aqout:  # In aquifer outside cylinder
            if aq.type == aq.conf:
                # p=0 gives zero cosine part (derivative of a constant); fixed with log later
                for q in range(1,self.aqin.Naquifers):
                    # This is slightly funny since the even term will have one power more (there really is no power 0!)
                    qeta[0,q] = MathieuQe( psi, 0, self.afocOverLabOut[q-1] ) * MathieuKeD( eta, 0, self.afocOverLabOut[q-1] )
                    qpsi[0,q] = MathieuQeD( psi, 0, self.afocOverLabOut[q-1] ) * MathieuKe( eta, 0, self.afocOverLabOut[q-1] )
                for p in range(1,self.order+1):
                    expcos = float(p) * exp( -p*eta ) * cos( p*psi )
                    expsin = float(p) * exp( -p*eta ) * sin( p*psi )
                    qeta[2*p-1,0] = -expcos; qeta[2*p,0] = -expsin
                    qpsi[2*p-1,0] = -expsin; qpsi[2*p,0] =  expcos
                    for q in range(1,self.aqin.Naquifers):
                        qeta[2*p-1,q] = MathieuQe( psi, p, self.afocOverLabOut[q-1] ) * MathieuKeD( eta, p, self.afocOverLabOut[q-1] )  # Add Mathieu Function Here
                        qeta[2*p,q]   = MathieuQo( psi, p, self.afocOverLabOut[q-1] ) * MathieuKoD( eta, p, self.afocOverLabOut[q-1] )  # Add Mathieu Function Here
                        qpsi[2*p-1,q] = MathieuQeD( psi, p, self.afocOverLabOut[q-1] ) * MathieuKe( eta, p, self.afocOverLabOut[q-1] )  # Add Mathieu Function Here
                        qpsi[2*p,q]   = MathieuQoD( psi, p, self.afocOverLabOut[q-1] ) * MathieuKo( eta, p, self.afocOverLabOut[q-1] )  # Add Mathieu Function Here
                # May need some correction on values from edge here
            elif aq.type == aq.semi:
                for q in range(0,self.aqin.Naquifers):
                    # This is slightly funny since the even term will have one power more (there really is no power 0!)
                    qeta[0,q] = MathieuQe( psi, 0, self.afocOverLabOut[q] ) * MathieuKeD( eta, 0, self.afocOverLabOut[q] )
                    qpsi[0,q] = MathieuQeD( psi, 0, self.afocOverLabOut[q] ) * MathieuKe( eta, 0, self.afocOverLabOut[q] )
                for p in range(1,self.order+1):
                    for q in range(0,self.aqin.Naquifers):
                        qeta[2*p-1,q] = MathieuQe( psi, p, self.afocOverLabOut[q] ) * MathieuKeD( eta, p, self.afocOverLabOut[q] )  # Add Mathieu Function Here
                        qeta[2*p,q]   = MathieuQo( psi, p, self.afocOverLabOut[q] ) * MathieuKoD( eta, p, self.afocOverLabOut[q] )  # Add Mathieu Function Here
                        qpsi[2*p-1,q] = MathieuQeD( psi, p, self.afocOverLabOut[q] ) * MathieuKe( eta, p, self.afocOverLabOut[q] )  # Add Mathieu Function Here
                        qpsi[2*p,q]   = MathieuQoD( psi, p, self.afocOverLabOut[q] ) * MathieuKo( eta, p, self.afocOverLabOut[q] )  # Add Mathieu Function Here
                # May need some correction on values from edge here            
        elif self.aqout.type == self.aqout.conf and aq.type == aq.conf:  # Somewhere else inside confined aquifer
            # p=0 gives zero cosine part (derivative of a constant), fixed later
            for p in range(1,self.order+1):
                expcos = float(p) * exp( -p*eta ) * cos( p*psi )
                expsin = float(p) * exp( -p*eta ) * sin( p*psi )
                qeta[2*p-1,0] = -expcos; qeta[2*p,0] = -expsin
                qpsi[2*p-1,0] = -expsin; qpsi[2*p,0] =  expcos
            # May need some correction on values from edge here
        # Store values in return value
        # Let's do the ugly thing
        factor = -1.0 / ( self.afoc * sqrt( cosh(eta)**2 - cos(psi)**2 ) )
        [cosangle,sinangle] = self.outwardNormal(x,y)
##        # Alternative
##        comdis = zeros(len(qeta[:,0]),'D')
##        comdis.real = -qeta[:,0]
##        comdis.imag = qpsi[:,0]
##        omega = complex(eta,psi)
##        comdisxy = comdis * exp( - complex(0,1.0) * self.angle ) / (self.afoc * sinh(omega) )
##        print 'alternative qx,qy',comdisxy.real,-comdisxy.imag
##        print 'term ',exp( - complex(0,1.0) * self.angle ) / (self.afoc * sinh(omega) )
##        print 'factor*complex(cos,sin) ',factor*complex(cosangle,sinangle)
        
        qx = factor * ( qeta * cosangle - qpsi * sinangle );
        qy = factor * ( qeta * sinangle + qpsi * cosangle );
        # Fix first term if confined aquifer and appropriate
        if aq.type == aq.conf:
            if aq == self.aqout or (aq != self.aqin and self.aqout.type == self.aqout.conf):
                W = - exp( -complex(0,1) * self.angle ) / (self.afoc * sinh( complex(eta,psi) ) )
                qx[0,0] = W.real
                qy[0,0] = -W.imag
        return [qx,qy]
    def dischargeInfluenceRad(self,aq,x,y):
        [eta,psi] = self.xytoetapsi(x,y)
        # Store values in return value
        qeta = zeros( (2*self.order+1,aq.Naquifers), 'd' )
        if aq == self.aqin:  # Inside cylinder
            qeta[0,0] = 0.0 # p=0, cosine part (derivative of a constant)
            for q in range(1,self.aqin.Naquifers):
                # This is slightly funny since the even term will have one power more (there really is no power 0!)
                qeta[0,q] = MathieuQe( psi, 0, self.afocOverLabIn[q-1] ) * MathieuIeD( eta, 0, self.afocOverLabIn[q-1] )
            for p in range(1,self.order+1):
                sinhcos = float(p) * sinh( p*eta ) * cos( p*psi )
                coshsin = float(p) * cosh( p*eta ) * sin( p*psi )
                qeta[2*p-1,0] =  sinhcos; qeta[2*p,0] = coshsin
                for q in range(1,self.aqin.Naquifers):
                    qeta[2*p-1,q] = MathieuQe( psi, p, self.afocOverLabIn[q-1] ) * MathieuIeD( eta, p, self.afocOverLabIn[q-1] )  # Add Mathieu Function Here
                    qeta[2*p,q]   = MathieuQo( psi, p, self.afocOverLabIn[q-1] ) * MathieuIoD( eta, p, self.afocOverLabIn[q-1] )  # Add Mathieu Function Here
            # May need some correction on values from edge here
        elif aq == self.aqout:  # In aquifer outside cylinder
            # p=0 gives zero cosine part (derivative of a constant)
            for q in range(1,self.aqin.Naquifers):
                # This is slightly funny since the even term will have one power more (there really is no power 0!)
                qeta[0,q] = MathieuQe( psi, 0, self.afocOverLabOut[q-1] ) * MathieuKeD( eta, 0, self.afocOverLabOut[q-1] )
            for p in range(1,self.order+1):
                expcos = float(p) * exp( -p*eta ) * cos( p*psi )
                expsin = float(p) * exp( -p*eta ) * sin( p*psi )
                qeta[2*p-1,0] = -expcos; qeta[2*p,0] = -expsin
                for q in range(1,self.aqin.Naquifers):
                    qeta[2*p-1,q] = MathieuQe( psi, p, self.afocOverLabOut[q-1] ) * MathieuKeD( eta, p, self.afocOverLabOut[q-1] )  # Add Mathieu Function Here
                    qeta[2*p,q]   = MathieuQo( psi, p, self.afocOverLabOut[q-1] ) * MathieuKoD( eta, p, self.afocOverLabOut[q-1] )  # Add Mathieu Function Here
            # May need some correction on values from edge here
        else:  # Somewhere else
            # p=0 gives zero cosine part (derivative of a constant)
            for p in range(1,self.order+1):
                expcos = float(p) * exp( -p*eta ) * cos( p*psi )
                expsin = float(p) * exp( -p*eta ) * sin( p*psi )
                qeta[2*p-1,0] = -expcos; qeta[2*p,0] = -expsin
            # May need some correction on values from edge here
        factor = -1.0 / ( self.afoc * sqrt( cosh(eta)**2 - cos(psi)**2 ) )
        return factor * qeta
    def dischargeInfluenceRadInLayer(self,aq,pylayer,x,y):
        '''Returns dischargeInfluenceRadInLayer function in aquifer aq in pylayer as list (1 value per parameter)
        Needs to be overloaded because there is no parameter outside the functions
        Needs to be modified for inside and outside'''
        disInf = self.dischargeInfluenceRad(aq,x,y)
        rv = []
        for d in disInf:
            rv = rv + list(d * aq.eigvec[pylayer,:])
        if aq != self.aqin:
            dump = rv.pop(0)  # Get rid of very first term (always zero)
        return rv
    def dischargeInfluenceRadAllLayers(self,aq,dumlayer,x,y):
        '''Returns dischargeInfluenceRadAllLayers function in aquifer aq as an array
        Needs to be overloaded because there is no parameter outside the functions
        Needs to be modified for inside and outside'''
        disInf = self.dischargeInfluenceRad(aq,x,y)
        rv = zeros((aq.Naquifers,0),'d')
        for d in disInf:
            rv = hstack( ( rv, d*aq.eigvec ) )
        if aq != self.aqin:
            rv = rv[:,1:]  # Take off first column (parameter always zero)
        return rv
    def dischargeInfluenceAllLayers(self,aq,dumlayer,x,y):
        '''Returns dischargeInfluenceAllLayers function in aquifer aq as an array
        Needs to be overloaded because there is no parameter outside the functions
        Needs to be modified for inside and outside'''
        [disx,disy] = self.dischargeInfluence(aq,x,y)
        rvx = zeros((aq.Naquifers,0),'d')
        rvy = zeros((aq.Naquifers,0),'d')
        for d in disx:
            rvx = hstack( ( rvx, d*aq.eigvec ) )
        for d in disy:
            rvy = hstack( ( rvy, d*aq.eigvec ) )
        if aq == self.aqin:
            rvx = hstack(( rvx, zeros( ( aq.Naquifers, self.Nparamout ), 'd' ) ))
            rvy = hstack(( rvy, zeros( ( aq.Naquifers, self.Nparamout ), 'd' ) ))
        else:
            rvx = hstack(( zeros( (aq.Naquifers,self.Nparamin), 'd' ), rvx ))
            rvy = hstack(( zeros( (aq.Naquifers,self.Nparamin), 'd' ), rvy ))
        return [rvx,rvy]
    def dischargeContribution(self,aq,x,y):
        '''Returns matrix with two rowvectors of dischargeContributions Qx and Qy.
        Needs to be overloaded cause there is inside and outside'''
        disInf = self.dischargeInfluence(aq,x,y)
        if aq == self.aqin:
            disxInf = sum( self.paramin * disInf[0] )
            disyInf = sum( self.paramin * disInf[1] )
        else:
            disxInf = sum( self.paramout * disInf[0] )
            disyInf = sum( self.paramout * disInf[1] )
        return array([disxInf,disyInf])
    def getMatrixRows(self,elementList):
        rows=[]
        # Jump in potential
        for i in range(self.Ncp):  # Hardcoded for same number of aquifers in and out
            rowin = zeros((self.aqin.Naquifers,0),'d'); rowout = zeros((self.aqin.Naquifers,0),'d')  # Zero columns!
            for e in elementList:
                rowpart = e.getMatrixCoefficients(self.aqin,self.ldum,self.xcp[i],self.ycp[i],\
                                lambda el,aq,ldum,x,y:el.potentialInfluenceAllLayers(aq,ldum,x,y))
                if size(rowpart) > 0: rowin = hstack(( rowin, rowpart ))
            for e in elementList:
                rowpart = e.getMatrixCoefficients(self.aqout,self.ldum,self.xcp[i],self.ycp[i],\
                                lambda el,aq,ldum,x,y:el.potentialInfluenceAllLayers(aq,ldum,x,y))
                if size(rowpart) > 0: rowout = hstack(( rowout, rowpart ))
            row = self.aqout.Tcol * rowin - self.aqin.Tcol * rowout
            row = hstack( ( row,
                self.aqin.Tcol * self.aqout.Tcol * ( self.aqout.hstar - self.aqin.hstar ) + \
                self.aqin.Tcol * self.modelParent.potentialVectorCol(self.xcp[i],self.ycp[i],self.aqout) - \
                self.aqout.Tcol * self.modelParent.potentialVectorCol(self.xcp[i],self.ycp[i],self.aqin) ) )
            rows = rows + row.tolist()
        # Jump in radial discharge
        for i in range(self.Ncp):  # Hardcoded for same number of aquifers in and out
            rowin = zeros((self.aqin.Naquifers,0),'d'); rowout = zeros((self.aqin.Naquifers,0),'d')  # Zero columns!
            for e in elementList:
                rowqxqy = e.getMatrixCoefficients(self.aqin,self.ldum,self.xcp[i],self.ycp[i],\
                                lambda el,aq,ldum,x,y:el.dischargeInfluenceAllLayers(aq,ldum,x,y))
                if size(rowqxqy) > 0:
                    rowpart = rowqxqy[0] * cos( self.thetacp[i] ) + rowqxqy[1] * sin( self.thetacp[i] )
                    rowin = hstack(( rowin, rowpart ))
            for e in elementList:
                rowqxqy = e.getMatrixCoefficients(self.aqout,self.ldum,self.xcp[i],self.ycp[i],\
                                lambda el,aq,ldum,x,y:el.dischargeInfluenceAllLayers(aq,ldum,x,y))
                if size(rowqxqy) > 0:
                    rowpart = rowqxqy[0] * cos( self.thetacp[i] ) + rowqxqy[1] * sin( self.thetacp[i] )
                    rowout = hstack(( rowout, rowpart ))
            row = rowin - rowout
            row = hstack(( row,
                self.modelParent.dischargeNormVectorCol(self.xcp[i],self.ycp[i],self.thetacp[i],self.aqout) -\
                self.modelParent.dischargeNormVectorCol(self.xcp[i],self.ycp[i],self.thetacp[i],self.aqin) ))
            rows = rows + row.tolist()
        return rows
    def getMatrixCoefficients(self,aq,pylayer,x,y,func):
        return func(self,aq,pylayer,x,y)
    def takeParameters(self,xsol,icount):
        par = xsol[icount : icount + (2*self.order+1)*self.aqin.Naquifers]
        self.paramin = self.paramin + reshape(par,(2*self.order+1,self.aqin.Naquifers))
        icount = icount + (2*self.order+1)*self.aqin.Naquifers
        par = xsol[icount : icount + (2*self.order+1)*self.aqin.Naquifers]
        self.paramout = self.paramout + reshape(par,(2*self.order+1,self.aqin.Naquifers))
        icount = icount + (2*self.order+1)*self.aqin.Naquifers
        return icount
    def check(self):
        for i in range(self.Ncp):
            print 'Control point '+str(i)
            print 'head inside:  '+str(self.modelParent.headVector(self.xcp[i],self.ycp[i],self.aqin))
            print 'head outside: '+str(self.modelParent.headVector(self.xcp[i],self.ycp[i],self.aqout))
            print 'Qrad inside:  '+str(self.modelParent.dischargeNormVector(self.xcp[i],self.ycp[i],self.thetacp[i],self.aqin))
            print 'Qrad outside: '+str(self.modelParent.dischargeNormVector(self.xcp[i],self.ycp[i],self.thetacp[i],self.aqout))
        print 'Note: no condition on radial flow in bottom aquifer of last control point'
    def layout(self):
        return [0]
    def parSum(self):
        return sum( sum(abs(self.paramin)) ) + sum( sum(abs(self.paramout)) )
    def approxError(self,fac=4.0):
        angles = arange( 0, 2*pi-0.01, 2*pi/(fac*self.Ncp) )
        [x,y] = self.etapsitoxy(self.etastar, angles)
        xmidplus = 0.5 * ( x + hstack(( x[1:],x[0] )) ); xmidmin = hstack(( xmidplus[-1], xmidplus[:-1] ))
        ymidplus = 0.5 * ( y + hstack(( y[1:],y[0] )) ); ymidmin = hstack(( ymidplus[-1], ymidplus[:-1] ))
        lengths = sqrt( (xmidplus-xmidmin)**2 + (ymidplus-ymidmin)**2 )
        errortot = 0.0; Qrerrortot = 0.0
        errormax = -1e6; Qrerrormax = -1e6
        Qtot = 0.0
        for i in range(len(x)):
            hin = self.modelParent.headVector(x[i],y[i],self.aqin)[0]
            hout = self.modelParent.headVector(x[i],y[i],self.aqout)[0]
            an = self.aqin.outwardNormalAngle(x[i],y[i])
            Qrin = self.modelParent.dischargeNormVector(x[i],y[i],an,self.aqin)[0]
            Qrout = self.modelParent.dischargeNormVector(x[i],y[i],an,self.aqout)[0]
            errortot = errortot + abs(hin-hout); Qrerrortot = Qrerrortot + abs(Qrin-Qrout)
            errormax = max( errormax, abs(hin-hout) ); Qrerrormax = max( Qrerrormax, abs(Qrin-Qrout))
            Qtot = Qtot + Qrout * lengths[i]
        print Qtot
        erroravg = errortot / len(x); Qrerroravg = Qrerrortot / len(x)
        return [erroravg,errormax,Qrerroravg,Qrerrormax]
    def minmaxHead(self,Nterms=4):
        angles = arange( 0, 2*pi-0.01, 2*pi/(Nterms*self.Ncp) )
        [x,y] = self.etapsitoxy(self.etastar, angles)
        hmin = 1e6; hmax = -1e6
        for i in range(len(x)):
            h = self.modelParent.headVector(x[i],y[i],self.aqin)[0]
            hmin = min(h,hmin); hmax = max(h,hmax)
        return [hmin,hmax]
    def nearElement(self,pyLayer,xyz1,xyz2,step,idir):
        changed = 0; stop = 0; xyznew = zeros(3,'d')
        [eta1,psi1] = self.aqin.xytoetapsi(xyz1[0],xyz1[1])
        [eta2,psi2] = self.aqin.xytoetapsi(xyz2[0],xyz2[1])
        if ( eta1 < self.etastar and eta2 > self.etastar  ) or ( eta1 > self.etastar and eta2 < self.etastar ):
            # intersecting ellipse
            (x1,y1) = xyz1[0:2]; (x2,y2) = xyz2[0:2]
            # Rotate and scale to circle
            Z1 = ( complex(x1,y1) - self.zc ) * complex( cos(self.angle), -sin(self.angle) )
            Z2 = ( complex(x2,y2) - self.zc ) * complex( cos(self.angle), -sin(self.angle) )
            x1 = Z1.real/self.along; y1 = Z1.imag/self.bshort
            x2 = Z2.real/self.along; y2 = Z2.imag/self.bshort
            a = (x2-x1)**2 + (y2-y1)**2
            b = 2.0 * ( (x2-x1) * x1 + (y2-y1) * y1 )
            c = x1**2 + y1**2 - 1.0
            u1 = ( -b - sqrt(b**2 - 4.0*a*c) ) / (2.0*a)
            u2 = ( -b + sqrt(b**2 - 4.0*a*c) ) / (2.0*a)
            if u1 > 0:
                u = u1 * 1.000001 # Go just beyond circle
            else:
                u = u2 * 1.000001 # Go just beyond circle
            xn = x1 + u * (x2-x1); yn = y1 + u * (y2-y1)

            # Transfer back
            xn = xn * self.along; yn = yn * self.bshort
            Zn = complex(xn,yn) * complex( cos(self.angle), sin(self.angle) ) + self.zc
            horstepold = sqrt( (xyz1[0]-xyz2[0])**2 + (xyz1[1]-xyz2[1])**2 )
            horstepnew = sqrt( (xyz1[0]-Zn.real)**2 + (xyz1[1]-Zn.imag)**2 )
            znew = xyz1[2] + horstepnew / horstepold * ( xyz2[2] - xyz1[2] )           
            xyznew = array([Zn.real,Zn.imag,znew],'d')
            changed = 1
        return [changed, stop, xyznew]
    def bisection(self,hstarmin,hstarmax,Nterms=4,tol=1e-6):
        self.aqin.hstar = hstarmin
        self.modelParent.solve()
        [hmin,dum] = self.minmaxHead(Nterms); hmin = hmin - hstarmin
        self.aqin.hstar = hstarmax
        self.modelParent.solve()
        [hmax,dum] = self.minmaxHead(Nterms); hmax = hmax - hstarmax
        print 'hmin,hmax ',hmin,hmax
        if hmin * hmax > 0:
            print 'value not between min and max'
            return
        while min( abs(hmin), abs(hmax) ) > tol:
            hstarnew = 0.5 * (hstarmin + hstarmax)
            self.aqin.hstar = hstarnew
            self.modelParent.solve()
            [hnew,dum] = self.minmaxHead(Nterms); hnew = hnew - hstarnew
            if hnew * hmin < 0:
                hstarmax = hstarnew
                hmax = hnew
            else:
                hstarmin = hstarnew
                hmin = hnew
            print 'hstarmin,hstarmax,hmin,hmax ',hstarmin,hstarmax,hmin,hmax
        if abs(hmin) < abs(hmax):
            return hstarmin
        else:
            return hstarmax
    def distanceSquaredToElement(self,x,y):  # Still rough, at it computes it for a circle
        '''Returns distance squared to element. Used for deciding tracing step'''
        dis = sqrt( ( x - self.xc )**2 + ( y - self.yc ) **2 )
        if self.along > dis:  # inside circle
            dissq = 0.0
        else:
            dissq = ( dis - self.along ) **2
        return dissq

# Still experimental

class EllipseLake(EllipseInhom):
    '''EllipInhom class
    Note that aquiferparent doesn't have a meaning for this element
    All attributes from element.
    '''
    def __init__(self,modelParent,order,aqin,aqout,Q):
	EllipseInhom.__init__(self,modelParent,order,aqin,aqout)
        self.Q = Q
    def __repr__(self):
	return 'EllipLake xc,yc,Q,order ' + str((self.xc,self.yc,self.Q,self.order)) + ' with inside aquifer data ' + str(self.aqin)
    def getMatrixRows(self,elementList):
        rows=[]
        # Jump in potential
        for i in range(self.Ncp):  # Hardcoded for same number of aquifers in and out
            rowin = zeros((self.aqin.Naquifers,0),'d'); rowout = zeros((self.aqin.Naquifers,0),'d')  # Zero columns!
            for e in elementList:
                rowpart = e.getMatrixCoefficients(self.aqin,self.ldum,self.xcp[i],self.ycp[i],\
                                lambda el,aq,ldum,x,y:el.potentialInfluenceAllLayers(aq,ldum,x,y))
                if size(rowpart) > 0: rowin = hstack(( rowin, rowpart ))
            for e in elementList:
                rowpart = e.getMatrixCoefficients(self.aqout,self.ldum,self.xcp[i],self.ycp[i],\
                                lambda el,aq,ldum,x,y:el.potentialInfluenceAllLayers(aq,ldum,x,y))
                if size(rowpart) > 0: rowout = hstack(( rowout, rowpart ))
            row = self.aqout.Tcol * rowin - self.aqin.Tcol * rowout
            row = hstack( ( row,
                self.aqin.Tcol * self.aqout.Tcol * ( self.aqout.hstar - self.aqin.hstar ) + \
                self.aqin.Tcol * self.modelParent.potentialVectorCol(self.xcp[i],self.ycp[i],self.aqout) - \
                self.aqout.Tcol * self.modelParent.potentialVectorCol(self.xcp[i],self.ycp[i],self.aqin) ) )
            rows = rows + row.tolist()
        # Jump in radial discharge
        for i in range(self.Ncp):  # Hardcoded for same number of aquifers in and out
            rowin = zeros((self.aqin.Naquifers,0),'d'); rowout = zeros((self.aqin.Naquifers,0),'d')  # Zero columns!
            for e in elementList:
                rowqxqy = e.getMatrixCoefficients(self.aqin,self.ldum,self.xcp[i],self.ycp[i],\
                                lambda el,aq,ldum,x,y:el.dischargeInfluenceAllLayers(aq,ldum,x,y))
                if size(rowqxqy) > 0:
                    rowpart = rowqxqy[0] * cos( self.thetacp[i] ) + rowqxqy[1] * sin( self.thetacp[i] )
                    rowin = hstack(( rowin, rowpart ))
            for e in elementList:
                rowqxqy = e.getMatrixCoefficients(self.aqout,self.ldum,self.xcp[i],self.ycp[i],\
                                lambda el,aq,ldum,x,y:el.dischargeInfluenceAllLayers(aq,ldum,x,y))
                if size(rowqxqy) > 0:
                    rowpart = rowqxqy[0] * cos( self.thetacp[i] ) + rowqxqy[1] * sin( self.thetacp[i] )
                    rowout = hstack(( rowout, rowpart ))
            row = rowin - rowout
            row = hstack(( row,
                self.modelParent.dischargeNormVectorCol(self.xcp[i],self.ycp[i],self.thetacp[i],self.aqout) -\
                self.modelParent.dischargeNormVectorCol(self.xcp[i],self.ycp[i],self.thetacp[i],self.aqin) ))
            rows = rows + row.tolist()
        return rows
    def bisection(self,hstarmin,hstarmax):
        self.aqin.hstar = hstarmin
        self.modelParent.solve()
        [dum,hmin] = self.minmaxHead(); hmin = hmin - hstarmin
        self.aqin.hstar = hstarmax
        self.modelParent.solve()
        [dum,hmax] = self.minmaxHead(); hmax = hmax - hstarmax
        print 'hmin,hmax ',hmin,hmax
        if hmin * hmax > 0:
            print 'value not between min and max'
            return
        for i in range(5):
            hstarnew = 0.5 * (hstarmin + hstarmax)
            self.aq.hstar = hstarnew
            self.modelParent.solve()
            [dum,hnew] = self.minmaxHead(); hnew = hnew - hstarnew
            if hnew * hmin < 0:
                hstarmax = hstarnew
                hmax = hnew
            else:
                hstarmin = hstarnew
                hmin = hnew
            print 'hstarmin,hstarmax,hmin,hmax ',hstarmin,hstarmax,hmin,hmax
    def distanceSquaredToElement(self,x,y):  # Still rough, at it computes it for a circle
        '''Returns distance squared to element. Used for deciding tracing step'''
        dis = sqrt( ( x - self.xc )**2 + ( y - self.yc ) **2 )
        if self.along > dis:  # inside circle
            dissq = 0.0
        else:
            dissq = ( dis - self.along ) **2
        return dissq

