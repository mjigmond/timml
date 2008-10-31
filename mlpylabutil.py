from matplotlib.pyplot import *
from matplotlib.colors import colorConverter
from matplotlib.collections import LineCollection
from numpy import *
from mltrace import *

def pycontour( ml, xmin, xmax, nx, ymin, ymax, ny, Naquifers=1, levels = 10, color = None, \
               width = 0.5, style = '-', separate = 0, layout = 1, newfig = 1, labels = 0, labelfmt = '%1.2f', xsec = 0,
               returnheads = 0, returncontours = 0, fill = 0, size=None, pathline = False):
    '''Contours head with pylab'''
    rcParams['contour.negative_linestyle']='solid'

    rows = []   # Store every matrix in one long row

    # Determine aquifers to plot
    if Naquifers == 'all':
        Naquifers = ml.aq.Naquifers
    if type(Naquifers) == list:
        aquiferRange = list( array(Naquifers)-1 ) 
    else:
        if Naquifers <= ml.aq.Naquifers:
            aquiferRange = range(Naquifers)
        else:
            aquiferRange = range(ml.aq.Naquifers)
    Naquifers = len(aquiferRange)

    xg,yg = meshgrid( linspace( xmin, xmax, nx ), linspace( ymin, ymax, ny ) ) 
    print 'grid of '+str((nx,ny))+'. gridding in progress. hit ctrl-c to abort'

    head = zeros( ( Naquifers, ny, nx ), 'd' )
    for irow in range(ny):
        for jcol in range(nx):
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
        levdum = arange( levels[0],levels[1],levels[2] )
        levels = len(aquiferRange)*[levdum]
    elif levels == 'ask':
        levels = []
        for k in range(len(aquiferRange)):
            hmin = amin(head[k,:,:].flat)
            hmax = amax(head[k,:,:].flat)
            print 'Layer ',aquiferRange[k],' min,max: ',hmin,', ',hmax,'. Enter: hmin,hmax,step '
            h1,h2,delh = input()
            levels = levels + [ arange(h1,h2+1e-8,delh) ]
    elif type(levels) is int:
        levels = len(aquiferRange)*[levels]
    elif isinstance(levels,ndarray):
        levels = len(aquiferRange)*[levels]
        
    # Drawing separate figures for each head
    if size == None: size = (8,8)
    if separate:
        for k in range(len(aquiferRange)):
            figure( figsize=(xsize,ysize) )
            axis('scaled')
            axis( [xmin,xmax,ymin,ymax] )
            if layout: pylayout(ml)
            if fill:
                contourf( xg, yg, head[k,:,:], levels[k], colors = color[k], linewidths = width )
            else:
                contour( xg, yg, head[k,:,:], levels[k], colors = color[k], linewidths = width )
    else:
    # Drawing all heads on one figure
        if newfig:
            fig = figure( figsize=size )
##            if xsec:
##                ax1 = pylab.axes([.1,.38,.8,.55])
##                pylab.setp( ax1.get_xticklabels(), visible=False)
##            else:
##                ax = subplot(111)
##                ax.axis((xmin,xmax,ymin,ymax))
##                ax.axis('scaled')
        ax = subplot(111)
        ax.axis((xmin,xmax,ymin,ymax))
        ax.axis('scaled')
        if layout: pylayout(ml)
        for k in range(len(aquiferRange)):
            if fill:
                contourset = contourf( xg, yg, head[k,:,:], levels[k], linewidths = width, fmt=labelfmt )
            else:
                contourset = contour( xg, yg, head[k,:,:], levels[k], colors = color[k], linewidths = width, fmt=labelfmt )
                if style[k] != '-':
                    print 'mpl bug in setting line styles of collections'
##                for l in contourset.collections:
##                    if style[k] == '-':
##                        l.set_linestyle( (0, (1.0, 0.0)) )
##                    elif style[k] == '--':
##                        l.set_linestyle( (0, (6.0, 6.0)) )
##                    elif style[k] == ':':
##                        l.set_linestyle( (0, (1.0, 3.0)) )
##                    elif style[k] == '-.':
##                        l.set_linestyle( (0, (3.0, 5.0, 1.0, 5.0)) )
            if labels:
                clabel( contourset, inline = 1, fmt = labelfmt ) 
        if xsec:
            #ax1.axis('equal') # Changed from scaled to equal to get xsec to work
            #ax1.axis([xmin,xmax,ymin,ymax])
            #ax1.draw()
            print 'shared axis broken'
##            pos = ax1.get_position()
##            ax2 = pylab.axes([pos.x0,.1,pos.width,.25],sharex=ax1)
            #ax1.axis([xmin,xmax,ymin,ymax])
    draw()
    if pathline:
        ip = InteractivePathline(ml)
        gcf().canvas.mpl_connect('button_press_event',ip.press)       
    if returnheads and returncontours:
        return head,contourset
    elif returnheads:
        return xg,yg,head
    elif returncontours:
        return contourset

class InteractivePathline:
    def __init__(self,ml):
        self.ml = ml
    def press(self,event):
        if event.inaxes is None: return
        a = gca().axis()
        step = (a[1] - a[0]) / 100.0
        aq = self.ml.aq.findAquiferData(event.xdata,event.ydata)
        pytracelines( self.ml, [event.xdata], [event.ydata], [0.5*(aq.zt[0]+aq.zb[0])], step, Nmax=200 )
   

def pylayout( ml, color = 'k', overlay = 1, width = 0.5, style = 1 ):
    if overlay:
        ioff()
        ax = axis()
        p = []
        for e in ml.elementList:
            a = e.layout()
            nterms = len(a)
            for i in range(0,nterms,3):
                if a[i] > 1:
                    if e.aquiferParent.fakesemi and e.pylayers[0] == 0: # In top layer (the fake layer) of fake semi
                        plot( a[i+1], a[i+2], color = [.8,.8,.8] )
                    else:
                        if style == 1:
                            plot( a[i+1], a[i+2], color, linewidth = width )
                        elif style == 2:
                            fill( a[i+1], a[i+2], facecolor = color, edgecolor = color )
                elif a[i] == 1:
                    plot( a[i+1], a[i+2], color+'o', markersize=3 ) 
##                    p = p + [a[i+1], a[i+2], color ]
##        eval(str('plot'+str(tuple(p))))
        intensity = linspace(0.7,0.9,len(ml.aq.inhomList))
#        for inhom in ml.aq.inhomList:
#            corners = inhom.layout()
#            fill( corners[0], corners[1], facecolor = [.8,.8,.8], edgecolor = [.8,.8,.8])
        for (col,inhom) in zip(intensity,ml.aq.inhomList):
            corners = inhom.layout()
            fill( corners[0], corners[1], facecolor = cm.bone(col), edgecolor = [.8,.8,.8])
        axis(ax)
        draw()
        ion()
    else:
        for e in ml.elementList:
            a = e.layout()
            nterms = len(a)
            for i in range(0,nterms,3):
                if a[i] > 0:
                    plot( a[i+1], a[i+2], color )
        intensity = linspace(0.7,0.9,len(ml.aq.inhomList))
        if len(ml.aq.inhomList)==1: intensity = [intensity] # silly, as linspace should always return list
        for (col,inhom) in zip(intensity,ml.aq.inhomList):
            corners = inhom.layout()
            fill( corners[0], corners[1], facecolor = cm.bone(col), edgecolor = [.8,.8,.8])


def pytracelines(ml,xlist,ylist,zlist,step,twoD=1,tmax=1e30,Nmax=200,labfrac=2.0,\
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
        if len(xlist) > 5:
            color = int(ceil(ml.aq.Naquifers/5.)) * [color]
    if not overlay:
        fig = figure()
        subplot(111)
    if overlay:
        fig = gcf()
        fig.sca( fig.axes[0] )
        ax = axis()
    ioff()
    for i in range(len(xlist)):
        x = xlist[i]; y = ylist[i]; z = zlist[i]
        [xyz,t,stop,pylayers] = traceline(ml,x,y,z,step,tmax,Nmax,labfrac=labfrac,Hfrac=Hfrac,window=window)
        # plot plane view
        if xsec:
            fig = gcf()
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
#                plot( xyz[istart:j+1,0], xyz[istart:j+1,1], style+color[pylayers[istart]], linewidth=width)
#                if xsec:
#                    fig.sca( fig.axes[1] )
#                    plot( xyz[istart:j+1,0], xyz[istart:j+1,2], style+color[pylayers[istart]], linewidth=width)
#                    fig.sca( fig.axes[0] )
#                istart = j
#            elif j == Nsteps:
#                plot( xyz[istart:,0], xyz[istart:,1], style+color[pylayers[istart]], linewidth=width)
#                if xsec:
#                    fig.sca( fig.axes[1] )
#                    plot( xyz[istart:,0], xyz[istart:,2], style+color[pylayers[istart]], linewidth=width)
#                    fig.sca( fig.axes[0] )
    if overlay:
        fig = gcf()
        fig.sca( fig.axes[0] )
        axis(ax)
    if xsec:
        fig.axes[1].set_ylim(ml.aq.zb[-1],ml.aq.zt[0])
    draw()
    ion()
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
        fig = figure( figsize=size )
    if fill:
        contourset = contourf( hor, vert, head[:,:], levels, linewidths = width, fmt=labelfmt )
    else:
        contourset = contour( hor, vert, head[:,:], levels, colors = color, linewidths = width, fmt=labelfmt )
        if style != '-':
            print 'mpl bug in setting line styles of collections'
##        for l in contourset.collections:
##            if style == '-':
##                l.set_linestyle( (0, (1.0, 0.0)) )
##            elif style == '--':
##                l.set_linestyle( (0, (6.0, 6.0)) )
##            elif style == ':':
##                l.set_linestyle( (0, (1.0, 3.0)) )
##            elif style == '-.':
##                l.set_linestyle( (0, (3.0, 5.0, 1.0, 5.0)) )
        if labels:
            clabel(contourset,fmt=labelfmt)
    draw()
    if returnheads and returncontours:
        return head,L
    elif returnheads:
        return xg,yg,head
    elif returncontours:
        return L
