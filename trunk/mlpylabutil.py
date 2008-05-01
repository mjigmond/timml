from ml import *
from mltrace import *
import pylab
import string
from tkSimpleDialog import askstring
import Tkinter as Tk
from matplotlib.collections import LineCollection
from matplotlib.colors import colorConverter
from numpy import *
from numpy import min,max

CurrentModel = None
connect_id = 0

def head(i,x,y):
    return CurrentModel.head(i,x,y)

def compHeads(on,task=1):
    global connect_id
    if on:
        if task == 1:
            connect_id = pylab.connect('button_press_event', on_click)
        elif task == 2:
            connect_id = pylab.connect('button_press_event', write_text)
        elif task == 3:
            connect_id = pylab.connect('button_press_event', write_text_gray)
    else:
        if connect_id > 0:
            pylab.disconnect(connect_id)

class PlotEllipse:
    '''Class to draw ellipse interactively with three clicks:
    First click determines one end of long axis
    Moving cursor will show long axis
    Second click determines other end of long axis
    Moving cursor will change width of ellipse
    Third click finishes ellipse
    Functions get_data and get_boundary can be called upon completion
    Code is somewhat ugly, as attributes are created on-the-fly
    Calculation of boundary of ellipse makes use of elliptical coordinates
    Author: Mark Bakker, markbak@gmail.com
    '''
    def __init__(self,ax):
        self.ax = ax
        self.connect_id = pylab.connect('button_press_event', self.first_click)
    def first_click(self,event):
        # First click is first end-point of long axis
        if event.button == 1:
            if event.inaxes is not None:
                self.x0, self.y0 = event.xdata, event.ydata
                pylab.disconnect( self.connect_id )
                self.along, = self.ax.plot( (self.x0,self.x0), (self.y0,self.y0), 'k-' )  # the long axis; Note comma !
                self.connect_id1 = pylab.connect('motion_notify_event', self.first_move)
                self.connect_id2 = pylab.connect('button_press_event', self.second_click)
    def first_move(self,event):
        # Shows long axis
        if not event.inaxes: return 
        x1, y1 = event.xdata, event.ydata
        self.along.set_data( (self.x0, x1), (self.y0, y1) )
        pylab.draw()
    def second_click(self,event):
        # Second click is second end-point of long axis
        if event.button==1:
            if event.inaxes is not None:
                self.x1, self.y1 = event.xdata, event.ydata
                pylab.disconnect( self.connect_id1 )
                pylab.disconnect( self.connect_id2 )
                self.ax.lines.remove( self.along )
                self.xc = 0.5*(self.x0+self.x1); self.yc = 0.5*(self.y0+self.y1)
                self.z0 = complex(self.x0,self.y0); self.z1 = complex(self.x1,self.y1)
                self.zc = complex(self.xc,self.yc)
                self.a = 0.5 * abs( self.z1 - self.z0 )
                self.angle = arctan2( (self.y1-self.y0) , (self.x1-self.x0) )
                self.cosal = cos(self.angle); self.sinal = sin(self.angle)
                # plot ellipse
                self.ellipse, = self.ax.plot( (self.x0,self.x1), (self.y0,self.y1), 'k-' )
                self.connect_id1 = pylab.connect('motion_notify_event', self.second_move)
                self.connect_id2 = pylab.connect('button_press_event', self.third_click)
                pylab.draw()
    def second_move(self,event):
        # Shows ellipse; moving cursor changes width
        if not event.inaxes: return 
        x2, y2 = event.xdata, event.ydata
        z = complex(x2,y2)
        Z = ( 2 * z - (self.z0 + self.z1) ) / (self.z1 - self.z0)
        z = 0.5 * ( complex(0,Z.imag) * (self.z1 - self.z0) + ( self.z0 + self.z1 ) )
        self.b = abs( z - self.zc )
        if self.b > 0.9999 * self.a: self.b = 0.9999 * self.a
        self.afoc = sqrt( self.a**2 - self.b**2 )
        etastar = arccosh( self.a / self.afoc )
        theta = arange(0,2*pi+0.001,pi/50)
        [x,y] = self.etapsitoxy( etastar,theta )
        self.ellipse.set_data( x, y )
        pylab.draw()
    def etapsitoxy(self,eta,psi):
        # Helper function to convert elliptical coordinates to x,y
        xloc = self.afoc * cosh(eta) * cos(psi)
        yloc = self.afoc * sinh(eta) * sin(psi)
        x = xloc * self.cosal - yloc * self.sinal + self.xc
        y = xloc * self.sinal + yloc * self.cosal + self.yc
        return [x,y]
    def third_click(self,event):
        # Finishes ellipse
        if event.button==1:
            if event.inaxes is not None:
                x2, y2 = event.xdata, event.ydata
                z = complex(x2,y2)
                Z = ( 2 * z - (self.z0 + self.z1) ) / (self.z1 - self.z0)
                z = 0.5 * ( complex(0,Z.imag) * (self.z1 - self.z0) + ( self.z0 + self.z1 ) )
                self.b = abs( z - self.zc )
                self.afoc = sqrt( self.a**2 - self.b**2 )
                etastar = arccosh( self.a / self.afoc )
                self.etastar = etastar
                theta = arange(0,2*pi+0.001,pi/50)
                [x,y] = self.etapsitoxy( etastar,theta )
                self.ax.lines.remove( self.ellipse )
                pylab.fill( x, y, facecolor = pylab.cm.bone(0.4*pylab.rand(1)[0]+0.5), edgecolor = [.8,.8,.8] )
                pylab.draw()
                pylab.disconnect( self.connect_id1 )
                pylab.disconnect( self.connect_id2 )
    def get_data(self):
        # Returns x,y of center, length of long axis, length of short axis, and orientation of long axis
        return( self.xc, self.yc, self.a, self.b, self.angle )
    def get_boundary(self, Npoints):
        # Returns x,y for Npoints on boundary, equally spaced in elliptical coordinates
        theta = pylab.linspace( 0, 2*pi, Npoints )
        return self.etapsitoxy( self.etastar, theta )


                


##### Plotting tracelines

class CompTrace:
    def __init__(self,ml,xsec=0):
        self.model = ml
        self.xsec = xsec
        self.connect_id = 0
        self.fields = 'Step size', 'Max time', 'Max steps', 'Elevation'
        self.traceVariables = [ 100.0, 1e30, 100, [ml.aq.zt[0]] ]
        self.createPopup()
    def createPopup(self):
        self.popup = Tk.Toplevel()
        self.popup.title('Trace pathline')
        vars = []
        for i in range( len(self.fields)):
            row = Tk.Frame(self.popup)
            lab = Tk.Label( row, width=10, text = self.fields[i] )
            ent = Tk.Entry(row)
            row.pack(side=Tk.TOP,fill=Tk.X)
            lab.pack(side=Tk.LEFT)
            ent.pack(side=Tk.RIGHT,expand=Tk.YES,fill=Tk.X)
            if type( self.traceVariables[i] ) is float:
                var = Tk.DoubleVar()  # Apparantly you can only define these after the entry is created
            elif type( self.traceVariables[i] ) is int:
                var = Tk.IntVar()
            elif type( self.traceVariables[i] ) is list:
                var = Tk.StringVar()
            ent.config( textvariable = var )
            var.set( self.traceVariables[i] )
            vars.append( var )
        b = Tk.Button( self.popup, text='Trace', command = (lambda v=vars: self.setTrace(v)))
        b.bind( '<Return>', (lambda event, v=vars: self.setTrace(v)) )
        b.pack(side=Tk.LEFT)
        b.focus_force()
        b2 = Tk.Button( self.popup, text='End', command = self.endTrace )
        b2.bind( '<Return>', (lambda event: self.endTrace() ) )
        b2.pack(side=Tk.RIGHT)
    def setTrace(self,vars):
        self.traceStep = vars[0].get()
        self.tracetmax = vars[1].get()
        self.traceNmax = vars[2].get()
        self.traceZelev = eval( vars[3].get() )
        if self.connect_id > 0: pylab.disconnect( self.connect_id )
        self.connect_id = pylab.connect('button_press_event', self.doTrace)
    def doTrace(self,event):
        if event.button==1:
            if event.inaxes is not None:
                xr = [event.xdata]; yr = [event.ydata]
                if type(self.traceZelev) is list or type(self.traceZelev) is tuple:
                     zr = self.traceZelev; xr = len(zr)*xr; yr = len(zr)*yr;
                else:
                    zr = [traceZelev]
                pytracelines(self.model,xr,yr,zr,self.traceStep,twoD=1,tmax=self.tracetmax,Nmax=self.traceNmax,labfrac=2.0,\
                        Hfrac=5.0,window=[-1e30,-1e30,1e30,1e30],overlay=1,color=['r','g','k'],width=0.5,xsec=self.xsec)
    def endTrace(self):
        pylab.disconnect(self.connect_id)
        self.popup.destroy()

#### End Plot Trace
    
    
def on_click(event):
    if event.button==1:
        if event.inaxes is not None:
            pylab.text(event.xdata, event.ydata, '%2.2f' % head(1,event.xdata,event.ydata) ,horizontalalignment='center' )

def write_text(event):
    # get the x and y coords, flip y from top to bottom
    x, y = event.x, event.y
    if event.button==1:
        if event.inaxes is not None:
            text_input = askstring( 'Show text', 'Enter text' )
            pylab.text(event.xdata, event.ydata, text_input, bbox={"edgecolor":"w","facecolor":"w"}, horizontalalignment='center' )

def write_text_gray(event):
    # get the x and y coords, flip y from top to bottom
    x, y = event.x, event.y
    if event.button==1:
        if event.inaxes is not None:
            text_input = askstring( 'Show text', 'Enter text' )
            pylab.text(event.xdata, event.ydata, text_input, bbox={"edgecolor":[.8,.8,.8],"facecolor":[.8,.8,.8]}, horizontalalignment='center' )


def pycontour( ml, xmin, xmax, nx, ymin, ymax, ny, Naquifers=1, levels = 10, color = None, \
               width = 0.5, style = '-', separate = 0, layout = 1, newfig = 1, labels = 0, labelfmt = '%1.3f', xsec = 0,
               returnheads = 0, returncontours = 0, fill = 0, size=None):
    '''Contours head with pylab'''
    #global CurrentModel
    #CurrentModel = ml
    # Compute grid
    xstep = float(xmax-xmin)/nx
    ystep = float(ymax-ymin)/ny
    rows = []   # Store every matrix in one long row
    if Naquifers == 'all':
        Naquifers = ml.aq.Naquifers
    if type(Naquifers) == list:
        aquiferRange = list( array(Naquifers)-1 ) 
    else:
        aquiferRange = range(Naquifers)
    Naquifers = len(aquiferRange)
    xg,yg = pylab.meshgrid( xmin + xstep*arange(nx+1),  ymin + ystep*arange(ny+1) ) 
    print 'grid of '+str((nx,ny))+'. gridding in progress. hit ctrl-c to abort'
    head = zeros( ( Naquifers, ny+1, nx+1 ), 'd' )
    for irow in range(ny+1):
        for jcol in range(nx+1):
            # Figure out aquifer first, so we can process fake aquifers; no repeated effort as aq is passed to headVector
            aq = ml.aq.findAquiferData(xg[irow,jcol], yg[irow,jcol])
            h = ml.headVector( xg[irow,jcol], yg[irow,jcol], aq )
            for k in range(len(aquiferRange)):
                if not aq.fakesemi:
                    if len(h) < aquiferRange[k]+1:
                        head[k,irow,jcol] = h[0]
                    else:
                        head[k,irow,jcol] = h[aquiferRange[k]]
                else:
                    head[k,irow,jcol] = h[aquiferRange[k]+1]
    # Contour
    # Manage colors
    if type( color ) is str:
        color = Naquifers * [color]
    elif type( color ) is list:
        Ncolor = len(color)      
        if Ncolor < Naquifers:
            color = color + Naquifers * [ color[0] ]
    elif type( color ) is type(None):
        color = ['b','r','g','m','c']
        if Naquifers > 5:
            color = int(ceil(Naquifers/5.)) * color
    # Manage line styles
    if type( style ) is str:
        style = Naquifers * [style]
    elif type( style ) is list:
        Nstyle = len(style)      
        if Nstyle < Naquifers:
            style = style + Naquifers * [ style[0] ]
    # Manage levels to draw
    if type(levels) is list:
        levdum = arange( levels[0],levels[2],levels[1] )
        levels = len(aquiferRange)*[levdum]
    elif levels == 'ask':
        levels = []
        for k in range(len(aquiferRange)):
            hmin = min(head[k,:,:].flat)
            hmax = max(head[k,:,:].flat)
            print 'Layer ',aquiferRange[k],' min,max: ',hmin,', ',hmax,'. Enter: hmin,step,hmax '
            input = raw_input(); input = string.split(input,',')
            levels = levels + [ arange(float(eval(input[0])),float(eval(input[2]))+1e-8,float(eval(input[1]))) ]
    elif type(levels) is int:
        levels = len(aquiferRange)*[levels]
    # Drawing separate figures for each head   
    if separate:
        for k in range(len(aquiferRange)):
            pylab.figure( figsize=(xsize,ysize) )
            pylab.axis('scaled')
            pylab.axis( [xmin,xmax,ymin,ymax] )
            if layout: pylayout(ml)
            if fill:
                pylab.contourf( xg, yg, head[k,:,:], levels[k], colors = color[k], linewidths = width )
            else:
                pylab.contour( xg, yg, head[k,:,:], levels[k], colors = color[k], linewidths = width )
    else:
    # Drawing all heads on one figure
        if newfig:
            if size == None: size = (8,8)
            fig = pylab.figure( figsize=size )
            if xsec:
                ax1 = pylab.axes([.1,.38,.8,.55])
                pylab.setp( ax1.get_xticklabels(), visible=False)
                fig.sca(ax1)
        if layout: pylayout(ml)
        for k in range(len(aquiferRange)):
            if fill:
                contourset = pylab.contourf( xg, yg, head[k,:,:], levels[k], linewidths = width, fmt=labelfmt )
            else:
                contourset = pylab.contour( xg, yg, head[k,:,:], levels[k], colors = color[k], linewidths = width, fmt=labelfmt )
                for l in contourset.collections:
                    if style[k] == '-':
                        l.set_linestyle( (0, (1.0, 0.0)) )
                    elif style[k] == '--':
                        l.set_linestyle( (0, (6.0, 6.0)) )
                    elif style[k] == ':':
                        l.set_linestyle( (0, (1.0, 3.0)) )
                    elif style[k] == '-.':
                        l.set_linestyle( (0, (3.0, 5.0, 1.0, 5.0)) )
            if labels:
                pylab.clabel( contourset, inline = 1, fmt = labelfmt ) 
        if xsec:
            ax1.axis('equal') # Changed from scaled to equal to get xsec to work
            ax1.axis([xmin,xmax,ymin,ymax])
            ax1.draw()
            print 'shared axis broken'
            pos = ax1.get_position()
            ax2 = pylab.axes([pos[0],.1,pos[2],.25],sharex=ax1)
    pylab.draw()
    if returnheads and returncontours:
        return head,L
    elif returnheads:
        return xg,yg,head
    elif returncontours:
        return L
    

def pylayout( ml, color = 'k', overlay = 1, width = 0.5, style = 1 ):
    if overlay:
        pylab.ioff()
        ax = pylab.axis()
        p = []
        for e in ml.elementList:
            a = e.layout()
            nterms = len(a)
            for i in range(0,nterms,3):
                if a[i] > 1:
                    if e.aquiferParent.fakesemi and e.pylayers[0] == 0: # In top layer (the fake layer) of fake semi
                        pylab.plot( a[i+1], a[i+2], color = [.8,.8,.8] )
                    else:
                        if style == 1:
                            pylab.plot( a[i+1], a[i+2], color, linewidth = width )
                        elif style == 2:
                            pylab.fill( a[i+1], a[i+2], facecolor = color, edgecolor = color )
                elif a[i] == 1:
                    pylab.plot( a[i+1], a[i+2], color+'o', markersize=3 ) 
##                    p = p + [a[i+1], a[i+2], color ]
##        eval(str('pylab.plot'+str(tuple(p))))
        intensity = pylab.linspace(0.7,0.9,len(ml.aq.inhomList))
#        for inhom in ml.aq.inhomList:
#            corners = inhom.layout()
#            pylab.fill( corners[0], corners[1], facecolor = [.8,.8,.8], edgecolor = [.8,.8,.8])
        for (col,inhom) in zip(intensity,ml.aq.inhomList):
            corners = inhom.layout()
            pylab.fill( corners[0], corners[1], facecolor = pylab.cm.bone(col), edgecolor = [.8,.8,.8])
        pylab.axis(ax)
        pylab.draw()
        pylab.ion()
    else:
        for e in ml.elementList:
            a = e.layout()
            nterms = len(a)
            for i in range(0,nterms,3):
                if a[i] > 0:
                    pylab.plot( a[i+1], a[i+2], color )
        intensity = pylab.linspace(0.7,0.9,len(ml.aq.inhomList))
        if len(ml.aq.inhomList)==1: intensity = [intensity] # silly, as linspace should always return list
        for (col,inhom) in zip(intensity,ml.aq.inhomList):
            corners = inhom.layout()
            pylab.fill( corners[0], corners[1], facecolor = pylab.cm.bone(col), edgecolor = [.8,.8,.8])


def pytracelines(ml,xrange,yrange,zrange,step,twoD=1,tmax=1e30,Nmax=20,labfrac=2.0,\
                    Hfrac=5.0,window=[-1e30,-1e30,1e30,1e30],overlay=1,color=['r','g','k'],width=0.5,style='-',xsec=0):
    '''Routine for plotting multiple tracelines using pylab'''
    if type( color ) is str:
        color = ml.aq.Naquifers * [color]
    elif type( color ) is list:
        Ncolor = len(color)      
        if Ncolor < ml.aq.Naquifers:
            color = color + ml.aq.Naquifers * [ color[0] ]
    elif type( color ) is type(None):
        color = ['b','r','g','m','c']
        if len(xrange) > 5:
            color = int(ceil(ml.aq.Naquifers/5.)) * [color]
    if not overlay:
        fig = pylab.figure()
        pylab.subplot(111)
    if overlay:
        fig = pylab.gcf()
        fig.sca( fig.axes[0] )
        ax = pylab.axis()
    pylab.ioff()
    for i in range(len(xrange)):
        x = xrange[i]; y = yrange[i]; z = zrange[i]
        [xyz,t,stop,pylayers] = traceline(ml,x,y,z,step,tmax,Nmax,labfrac=labfrac,Hfrac=Hfrac,window=window)
        # plot plane view
        if xsec:
            fig = pylab.gcf()
            fig.sca( fig.axes[0] )
#        pylayers = ml.inWhichPyLayers( xyz[:,0], xyz[:,1], xyz[:,2] )
        istart = 0
        Nsteps = len(xyz[:,0]) - 1
        for j in range(len(color)):
            color[j] = colorConverter.to_rgba( color[j] )
        trace_color = []
        for j in range(len(xyz)-1):  # Number of segments one less than number of points
            trace_color.append( color[ pylayers[j] ] )
        if twoD == 1:
            points = zip( xyz[:,0], xyz[:,1] )
        elif twoD == 2:
            points = zip( xyz[:,0], xyz[:,2] )
        segments = zip( points[:-1], points[1:] )
        LC = LineCollection(segments, colors = trace_color)
        LC.set_linewidth(width)
        fig.axes[0].add_collection(LC)
        if xsec:
            points = zip( xyz[:,0], xyz[:,2] )
            segments = zip( points[:-1], points[1:] )
            LC = LineCollection(segments, colors = trace_color)
            LC.set_linewidth(width)
            fig.axes[1].add_collection(LC)
#        for j in range( 1,len(xyz[:,0]) ):
#            if pylayers[j] != pylayers[istart]:
#                pylab.plot( xyz[istart:j+1,0], xyz[istart:j+1,1], style+color[pylayers[istart]], linewidth=width)
#                if xsec:
#                    fig.sca( fig.axes[1] )
#                    pylab.plot( xyz[istart:j+1,0], xyz[istart:j+1,2], style+color[pylayers[istart]], linewidth=width)
#                    fig.sca( fig.axes[0] )
#                istart = j
#            elif j == Nsteps:
#                pylab.plot( xyz[istart:,0], xyz[istart:,1], style+color[pylayers[istart]], linewidth=width)
#                if xsec:
#                    fig.sca( fig.axes[1] )
#                    pylab.plot( xyz[istart:,0], xyz[istart:,2], style+color[pylayers[istart]], linewidth=width)
#                    fig.sca( fig.axes[0] )
    if overlay:
        fig = pylab.gcf()
        fig.sca( fig.axes[0] )
        pylab.axis(ax)
    if xsec:
        fig.axes[1].set_ylim(ml.aq.zb[-1],ml.aq.zt[0])
    pylab.draw()
    pylab.ion()
    return

def pyvertcontour( ml, x1, y1, x2, y2, nx, zmin, zmax, nz, levels = 10, color = None, \
               width = 0.5, style = '-', newfig = 1, labels = 0, labelfmt = '%1.3f',
               returnheads = 0, returncontours = 0, fill = 0, size=None):
    '''Contours head with pylab'''
    #global CurrentModel
    #CurrentModel = ml
    # Compute grid
    xg = linspace(x1,x2,nx)
    yg = linspace(y1,y2,nx)
    zg = linspace(zmin,zmax,nz)
    horlength = sqrt( (x2-x1)**2 + (y2-y1)**2 )
    hor, vert = meshgrid( linspace( 0, horlength, nx ), zg )
    print 'grid of '+str((nx,nz))+'. gridding in progress. hit ctrl-c to abort'
    head = zeros( ( nz, nx ), 'd' )
    for irow in range(nz):
        for jcol in range(nx):
            # Figure out aquifer first, so we can process fake aquifers; no repeated effort as aq is passed to headVector
            head[irow,jcol] = ml.head3D( xg[jcol], yg[jcol], zg[irow] )
    # Contour
    # Manage levels to draw
    if type(levels) is list:
        levels = arange( levels[0],levels[2]+1e-8,levels[1] )
    elif levels == 'ask':
        hmin = min(head)
        hmax = max(head)
        print 'min,max: ',hmin,', ',hmax,'. Enter: hmin,step,hmax '
        input = raw_input(); input = string.split(input,',')
        levels = arange(float(eval(input[0])),float(eval(input[2]))+1e-8,float(eval(input[1])))
    # Drawing all heads on one figure
    if newfig:
        if size == None: size = (8,8)
        fig = pylab.figure( figsize=size )
    if fill:
        contourset = pylab.contourf( hor, vert, head[:,:], levels, linewidths = width, fmt=labelfmt )
    else:
        contourset = pylab.contour( hor, vert, head[:,:], levels, colors = color, linewidths = width, fmt=labelfmt )
        for l in contourset.collections:
            if style == '-':
                l.set_linestyle( (0, (1.0, 0.0)) )
            elif style == '--':
                l.set_linestyle( (0, (6.0, 6.0)) )
            elif style == ':':
                l.set_linestyle( (0, (1.0, 3.0)) )
            elif style == '-.':
                l.set_linestyle( (0, (3.0, 5.0, 1.0, 5.0)) )
        if labels:
            pylab.clabel(contourset,fmt=labelfmt)
    pylab.draw()
    if returnheads and returncontours:
        return head,L
    elif returnheads:
        return xg,yg,head
    elif returncontours:
        return L
