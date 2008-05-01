import Tkinter as Tk
from numpy import *
import pylab
from matplotlib.colors import rgb2hex,colorConverter
from matplotlib.collections import LineCollection

ActiveTimmlModel = None
ActiveAxis = None
ActiveCanvas = None
ActiveHeads = None
ActiveX = None
ActiveY = None
ActiveWindow = None
ActiveSettings = None
ActiveContours = None

def setActiveAxis(ax):
    global ActiveAxis
    ActiveAxis = ax

def getActiveAxis():
    global ActiveAxis
    return ActiveAxis

def setActiveWindow():
    global ActiveWindow
    global ActiveAxis
    x1,x2 = ActiveAxis.get_xlim()
    y1,y2 = ActiveAxis.get_ylim()
    ActiveWindow = (x1,y1,x2,y2)

def getActiveWindow():
    global ActiveWindow
    return ActiveWindow

def setActiveHeads(N):
    global ActiveTimmlModel
    global ActiveWindow
    global ActiveHeads, ActiveX, ActiveY
    x1,y1,x2,y2 = ActiveWindow
    nx,ny = N,N
    x = pylab.linspace(x1,x2,nx+1)
    y = pylab.linspace(y1,y2,ny+1)
    ActiveX = x
    ActiveY = y
    ActiveHeads = zeros((ActiveTimmlModel.aq.Naquifers,ny+1,nx+1),'d')
    for i in range(nx+1):
        for j in range(ny+1):
            aq = ActiveTimmlModel.aq.findAquiferData( x[i], y[j] )
            h = ActiveTimmlModel.headVector( x[i], y[j], aq )
            if not aq.fakesemi:
                ActiveHeads[:,j,i] = h
            else:
                ActiveHeads[:,j,i] = h[1:]

def getMinMaxHeads():
    global ActiveHeads
    if ActiveHeads != None:
        Naq = shape(ActiveHeads)[0]
        minh = []
        maxh = []
        for i in range( Naq ):
            minh = minh + [ min(ActiveHeads[i,:,:].flat) ]
            maxh = maxh + [ max(ActiveHeads[i,:,:].flat) ]
        minh = min(minh)
        maxh = max(maxh)
    else: minh,maxh = 0,0
    return minh,maxh

def getActiveHeads():
    global ActiveHeads
    return ActiveHeads

def findWell(x,y):
    global ActiveTimmlModel
    dsqmin = 1e30
    for e in ActiveTimmlModel.collectionDict['well']:
        dsq = e.distanceSquaredToElement(x,y)
        if dsq < dsqmin:
            dsqmin = dsq
            rv = e
    return rv.xw,rv.yw,rv.rw,rv.layers

def showContours(layers,numlines):
    global ActiveHeads, ActiveX, ActiveY
    global ActiveAxis, ActiveSettings, ActiveCanvas
    global ActiveContours
    setActiveWindow()
    win = getActiveWindow()
    ActiveAxis.set_autoscale_on(False)
    for i in layers:
        ActiveContours = ActiveAxis.contour( ActiveX, ActiveY, ActiveHeads[i,:,:], numlines, colors=ActiveSettings.get_color('Contour',i) )
    ActiveAxis.set_xlim(win[0],win[2])
    ActiveAxis.set_ylim(win[1],win[3])
    ActiveCanvas.draw()

def labelContours():
    global ActiveContours, ActiveAxis, ActiveSettings
    ActiveAxis.clabel( ActiveContours, inline = 1, fontsize = ActiveSettings.contour_label_size, fmt = ActiveSettings.contour_label_fmt  )
    ActiveCanvas.draw()

def doTracelines(xstart,ystart,zstart,step,tmax,Nmax):
    global ActiveAxis, ActiveCanvas, ActiveTimmlModel, ActiveSettings
    setActiveWindow()
    win = getActiveWindow()
    ActiveAxis.set_autoscale_on(False)
    width = 0.5
    color = []
    for j in range(getActiveNumberLayers()):
        color.append( ActiveSettings.get_color('Trace',j) )
        color[j] = colorConverter.to_rgba( color[j] )
    for i in range( len(xstart) ):
        xyz, time, reason, pylayers = ActiveTimmlModel.\
            traceline(xstart[i],ystart[i],zstart[i],step,tmax,Nmax,tstart=0.0,window=win,labfrac = 2.0, Hfrac = 2.0)
        trace_color = []
        for j in range(len(xyz)-1):  # Number of segments one less than number of points
            trace_color.append( color[ pylayers[j] ] )
        points = zip( xyz[:,0], xyz[:,1] )
        segments = zip( points[:-1], points[1:] )
        LC = LineCollection(segments, colors = trace_color)
        LC.set_linewidth(width)
        ActiveAxis.add_collection(LC)
        #ActiveAxis.plot( xyz[:,0], xyz[:,1], 'b' )
    ActiveAxis.set_xlim(win[0],win[2])
    ActiveAxis.set_ylim(win[1],win[3])
    ActiveCanvas.draw()

def setActiveCanvas(c):
    global ActiveCanvas
    ActiveCanvas = c

def getActiveCanvas():
    global ActiveCanvas
    return ActiveCanvas

def setActiveModel(ml):
    global ActiveTimmlModel
    ActiveTimmlModel = ml

def getActiveModel():
    global ActiveTimmlModel
    return ActiveTimmlModel

def getActiveNumberLayers():
    global ActiveTimmlModel
    if ActiveTimmlModel == None:
        return 5
    else:
        return ActiveTimmlModel.aq.Naquifers

def getLayerTopBottom(x,y):
    global ActiveTimmlModel
    aq = ActiveTimmlModel.aq.findAquiferData(x,y)
    return aq.zt,aq.zb

def solvemodel():
    global ActiveTimmlModel
    ActiveTimmlModel.solve()

def layoutmodel_extend():
    global ActiveTimmlModel
    global ActiveAxis
    ActiveAxis.set_autoscale_on(True)
    timmlgui_pylayout( ActiveTimmlModel, getColor('Layout') )
    c = getActiveCanvas()
    c.draw()

def layoutmodel():
    global ActiveTimmlModel
    global ActiveAxis
    ActiveAxis.set_autoscale_on(False)
    timmlgui_pylayout( ActiveTimmlModel, getColor('Layout') )
    c = getActiveCanvas()
    c.draw()

def clearmodel():
    ax = getActiveAxis()
    ax.clear()
    c = getActiveCanvas()
    c.draw()

class ContourPopup:
    def __init__(self):
        self.ml = getActiveModel()
        self.ax = getActiveAxis()
        self.title = 'Contour'
        self.fields = 'Grid x', 'Grid y', 'Max steps', 'Elevation'
        self.traceVariables = [ 50, 50, 100, [self.ml.aq.zt[0]] ]
        self.createPopup()
    def createPopup(self):
        self.popup = Tk.Toplevel()
        self.popup.title(self.title)
        self.vars = []
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
            self.vars.append( var )
        b = Tk.Button( self.popup, text='Grid', command = self.grid )
        b.bind( '<Return>', (lambda event: self.grid() ) )
        b.pack(side=Tk.LEFT,padx=5)
        b.focus_force()
        
        b2 = Tk.Button( self.popup, text='End', command = self.endTrace )
        b2.bind( '<Return>', (lambda event: self.endTrace() ) )
        b2.pack(side=Tk.RIGHT,padx=5)
    def grid(self):
        xmin,xmax = self.ax.get_xlim()
        ymin,ymax = self.ax.get_ylim()
        nx = self.vars[0].get()
        ny = self.vars[1].get()
        x = pylab.linspace(xmin,xmax,nx+1)
        y = pylab.linspace(ymin,ymax,ny+1)
        h = zeros((ny+1,nx+1),'d')
        for i in range(nx+1):
            for j in range(ny+1):
                h[j,i] = self.ml.head( 1, x[i], y[j] )
        self.ax.contour( x, y, h )
        c = getActiveCanvas()
        c.draw()
    def getValues(self):
        self.nx = self.vars[0].get()
        self.ny = self.vars[1].get()
        self.traceNmax = self.vars[2].get()
        self.traceZelev = eval( self.vars[3].get() )
    def doTrace(self,event):
        pass
    def endTrace(self):
        print 'See you later'
        self.popup.destroy()

def timmlgui_pylayout( ml, col = 'k', width = 0.5, style = 1 ):
    global ActiveAxis
    ax = ActiveAxis
    p = []
    # element layout
    for e in ml.elementList:
        a = e.layout()
        nterms = len(a)
        for i in range(0,nterms,3):
            if a[i] > 1:
                if style == 1:
                    ax.plot( a[i+1], a[i+2], color = col, linewidth = width )
                elif style == 2:
                    ax.fill( a[i+1], a[i+2], facecolor = col, edgecolor = color )
            elif a[i] == 1:
                ax.plot( a[i+1], a[i+2], color = col, markerfacecolor = col, markeredgecolor = col, marker = 'o', markersize=3 )
    # inhomogeneity layout
    intensity = pylab.linspace(0.7,0.9,len(ml.aq.inhomList))
    for (col,inhom) in zip(intensity,ml.aq.inhomList):
        corners = inhom.layout()
        ax.fill( corners[0], corners[1], facecolor = pylab.cm.bone(col), edgecolor = [.8,.8,.8])

class TimmlSettings:
    def __init__(self):
        self.color_dict = {}
        colorlist = [(0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 0.5, 0.0), (0.75, 0, 0.75), (0.0, 0.75, 0.75)]
        colorlisthex = []
        for c in colorlist:
            colorlisthex.append( rgb2hex(c) )
        self.color_dict['Contour'] = 20*colorlisthex
        self.color_dict['Trace'] = 20*colorlisthex
        self.color_dict['Layout'] = rgb2hex( [0.,0.,0.] )
        self.contour_label_fmt = '%1.2f'
        self.contour_label_size = 8
        self.trace_dict = {}
        self.trace_dict['step'] = 0.02
        self.trace_dict['tmax'] = 1e30
        self.trace_dict['nmax'] = 100
        self.trace_dict['elev'] = '0.5'
        self.trace_dict['layers'] = [1]
        self.trace_dict['forward'] = 1
        self.trace_dict['capzoneforward'] = 0
        self.trace_dict['ncap'] = 10
    def get_color(self,c,index=None):
        if index == None:
            return self.color_dict[c]
        else:
            return self.color_dict[c][index]
    def set_color(self,color,c,index=None):
        if index == None:
            self.color_dict[c] = color
        else:
            self.color_dict[c][index] = color
    def set_contour_label_fmt(self,s):
        self.contour_label_fmt = s
    def set_contour_label_size(self,size):
        self.contour_label_size = size
    def get_contour_label_fmt(self):
        return self.contour_label_fmt
    def get_contour_label_size(self):
        return self.contour_label_size
    def set_trace(self,type,value):
        self.trace_dict[type] = value
    def get_trace(self,type):
        return self.trace_dict[type]
        

def setActiveSettings():
    global ActiveSettings
    ActiveSettings = TimmlSettings()

def getActiveSettings():
    global ActiveSettings
    return ActiveSettings

def setColor(color,c,index=None):
    global ActiveSettings
    ActiveSettings.set_color( color, c, index )

def getColor(c,index=None):
    global ActiveSettings
    return ActiveSettings.get_color( c, index )

def setContourLabelFormat(fmt):
    global ActiveSettings
    ActiveSettings.set_contour_label_fmt(fmt)

def setContourLabelSize(size):
    global ActiveSettings
    ActiveSettings.set_contour_label_size(size)

def getContourLabelFormat():
    global ActiveSettings
    return ActiveSettings.get_contour_label_fmt()

def getContourLabelSize():
    global ActiveSettings
    return ActiveSettings.get_contour_label_size()

def setTrace(type,value):
    global ActiveSettings
    ActiveSettings.set_trace( type, value )

def getTrace(type):
    global ActiveSettings
    return ActiveSettings.get_trace(type)
