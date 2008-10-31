'''
timmlmpl.py contains a prototype GUI for Tim based on matplotlib and Tkinter.
This file is part of the TimML library and is distributed under
the GNU LPGL. See the TimML.py file for more details.
(c) Mark Bakker, 2006
'''


import matplotlib
matplotlib.use('TkAgg')
matplotlib.rcParams['numerix'] = 'numpy' # Need to add this one
matplotlib.rcParams['xtick.labelsize'] = 8.0
matplotlib.rcParams['ytick.labelsize'] = 8.0
matplotlib.rcParams['lines.linewidth'] = 0.5

from matplotlib.numerix import arange, sin, pi
from matplotlib.axes import Subplot
from matplotlib.backends.backend_tkagg import *
from matplotlib.figure import Figure

import Tkinter as Tk
from tkMessageBox import showerror
from tkFileDialog import askopenfilename,asksaveasfilename
from tkColorChooser import askcolor
import string, os, sys
import copy

from TimMLgui import *



class Cursors:  #namespace
    HAND, POINTER, SELECT_REGION, MOVE, TRACE, CAPZONE = range(6)
cursors = Cursors()

cursord = {
    cursors.MOVE: "fleur",    
    cursors.HAND: "hand2",
    cursors.POINTER: "arrow",
    cursors.SELECT_REGION: "tcross",
    cursors.TRACE: "dotbox",
    cursors.CAPZONE: "circle",
    }

class NavigationToolbar2TkAgg(NavigationToolbar2, Tk.Frame):
    """
    Public attriubutes

      canvas   - the FigureCanvas  (gtk.DrawingArea)
      win   - the gtk.Window
    """
    def __init__(self, canvas, window):
        self.canvas = canvas
        self.window = window
        self._idle = True
        Tk.Frame.__init__(self, master=self.canvas._tkcanvas)
        NavigationToolbar2.__init__(self, canvas)
        
    def set_message(self, s):
        self.message.set(s)

    def draw_rubberband(self, event, x0, y0, x1, y1):
        height = self.canvas.figure.bbox.height()
        y0 =  height-y0
        y1 =  height-y1
        try: self.lastrect
        except AttributeError: pass
        else: self.canvas._tkcanvas.delete(self.lastrect)
        self.lastrect = self.canvas._tkcanvas.create_rectangle(x0, y0, x1, y1)

        #self.canvas.draw()

    def release(self, event):
        try: self.lastrect
        except AttributeError: pass
        else:
            self.canvas._tkcanvas.delete(self.lastrect)
            del self.lastrect

    def set_cursor(self, cursor):
        self.window.configure(cursor=cursord[cursor])
    
    def _Button(self, text, file, command):
        file = os.path.join(rcParams['datapath'], file)
        im = Tk.PhotoImage(master=self, file=file)
        b = Tk.Button(
            master=self, text=text, padx=2, pady=2, image=im, command=command)
        b._ntimage = im
        b.pack(side=Tk.LEFT)
        return b

    def _Button_nopic(self, text, command):
        #file = os.path.join(rcParams['datapath'], file)
        b = Tk.Button(
            master=self, text=text, padx=2, pady=2, command=command)
        #b._ntimage = im
        b.pack(side=Tk.LEFT)
        return b

    def _init_toolbar(self):
        xmin, xmax = self.canvas.figure.bbox.intervalx
        height, width = 50, xmax-xmin
        Tk.Frame.__init__(self, master=self.window,
                          width=width, height=height,
                          borderwidth=2)
        
        self.update()  # Make axes menu

        self.bHome = self._Button( text="Home",
                                   file='home.ppm',
                                   command=self.home)

        self.bBack = self._Button( text="Back",
                                   file='back.ppm',
                                   command = self.back)
        
        self.bForward = self._Button(text="Forward",
                                   file='forward.ppm',
                                     command = self.forward)

        self.bPan = self._Button( text="Pan",
                                   file='move.ppm',
                                  command = self.pan)

        self.bZoom = self._Button( text="Zoom",
                                   file='zoom_to_rect.ppm',
                                   command = self.zoom)


#        self.bsubplot = self._Button( text="Configure Subplots", file="subplots.ppm",
#                                   command = self.configure_subplots)


        self.bsave = self._Button( text="Save", 
                                   file='filesave.ppm',
                                   command = self.save_figure)
        
        self.bTrace = self._Button( text="Trace",
                                   file='trace.ppm',
                                   command = self.traceline)

        self.bCapzone = self._Button( text="Capzone",
                                   file='capzone.ppm',
                                   command = self.capzone)
        
        self.message = Tk.StringVar(master=self)
        self._message_label = Tk.Label(master=self, textvariable=self.message)
        self._message_label.pack(side=Tk.RIGHT)
        self.pack(side=Tk.BOTTOM, fill=Tk.X)

    def mouse_move(self, event):
        #print 'mouse_move', event.button

        if not event.inaxes or not self._active:
            if self._lastCursor != cursors.POINTER:
                self.set_cursor(cursors.POINTER)
                self._lastCursor = cursors.POINTER
        else:
            if self._active=='ZOOM':
                if self._lastCursor != cursors.SELECT_REGION:
                    self.set_cursor(cursors.SELECT_REGION)
                    self._lastCursor = cursors.SELECT_REGION
                if self._xypress is not None:
                    x, y = event.x, event.y
                    lastx, lasty, a, ind, lim, trans= self._xypress[0]
                    self.draw_rubberband(event, x, y, lastx, lasty)
            elif (self._active=='PAN' and self._lastCursor != cursors.MOVE):
                self.set_cursor(cursors.MOVE)
                self._lastCursor = cursors.MOVE
            elif (self._active=='TRACE' and self._lastCursor != cursors.TRACE):
                self.set_cursor(cursors.TRACE)
                self._lastCursor = cursors.TRACE
            elif (self._active=='CAPZONE' and self._lastCursor != cursors.CAPZONE):
                self.set_cursor(cursors.CAPZONE)
                self._lastCursor = cursors.CAPZONE

        if event.inaxes and event.inaxes.get_navigate():

            try: s = event.inaxes.format_coord(event.xdata, event.ydata)
            except ValueError: pass
            except OverflowError: pass            
            else:
                if len(self.mode):
                    self.set_message('%s : %s' % (self.mode, s))
                else:
                    self.set_message(s)
        else: self.set_message(self.mode)

    def traceline(self, *args):
        'activate tracing of pathlines'
        if not getActiveModel(): return

        if self._active == 'TRACE':
            self._active = None
        else:
            self._active = 'TRACE'

        if self._idPress is not None:
            self._idPress=self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._idRelease is not None:
            self._idRelease=self.canvas.mpl_disconnect(self._idRelease)
            self.mode = ''

        if self._active:
            self._idPress = self.canvas.mpl_connect('button_press_event', self.do_trace)
            #self._idRelease = self.canvas.mpl_connect('button_release_event', self.release_zoom)
            self.mode = 'Trace pathlines'

        self.set_message(self.mode)

    def capzone(self, *args):
        'activate delineation of capture zones'
        if not getActiveModel(): return

        if self._active == 'CAPZONE':
            self._active = None
        else:
            self._active = 'CAPZONE'

        if self._idPress is not None:
            self._idPress=self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._idRelease is not None:
            self._idRelease=self.canvas.mpl_disconnect(self._idRelease)
            self.mode = ''

        if self._active:
            self._idPress = self.canvas.mpl_connect('button_press_event', self.do_capzone)
            self.mode = 'Capture zone delineation'

        self.set_message(self.mode)

    def do_trace(self,event):
        setActiveWindow()
        if event.button==1:
            if event.inaxes is not None:
                x,y = event.xdata, event.ydata
                step = getTrace('step'); tmax = getTrace('tmax'); nmax = getTrace('nmax')
                elev = getTrace('elev'); layers = getTrace('layers'); forward = getTrace('forward')
                elev = eval( '['+elev+']' )
                win = getActiveWindow()
                step = step * ( win[2] - win[0] )
                zr = []
                zt,zb = getLayerTopBottom(x,y)
                for i in range(len(layers)):
                    if layers[i]:
                        for j in range(len(elev)):
                            zr.append( zb[i] + elev[j] * (zt[i]-zb[i]) )
                xr = len(zr)*[x]; yr = len(zr)*[y]
                print 'step',step
                if forward == 0: step = -step
                doTracelines(xr,yr,zr,step,tmax,nmax)

    def do_capzone(self,event):
        setActiveWindow()
        if event.button==1:
            if event.inaxes is not None:
                x,y = event.xdata, event.ydata
                xw,yw,rw,well_layers = findWell(x,y)
                Ntraces_capzone = getTrace('ncap')
                alpha = arange(0,2*pi-1e-6,(2*pi)/Ntraces_capzone)
                step = getTrace('step'); tmax = getTrace('tmax'); nmax = getTrace('nmax')
                elev = getTrace('elev'); layers = getTrace('layers'); forward = getTrace('capzoneforward')
                elev = eval( '['+elev+']' )
                win = getActiveWindow()
                step = step * ( win[2] - win[0] )
                step = -step
                if forward: step = -step
                zr = []
                zt,zb = getLayerTopBottom(xw,yw)
                for i in range(len(well_layers)):
                    for j in range(len(elev)):
                        zr.append( zb[well_layers[i]-1] + elev[j] * (zt[well_layers[i]-1]-zb[well_layers[i]-1]) )
                for i in range(Ntraces_capzone):
                    xr = [ xw + 2*rw*cos(alpha[i]) ]  ; yr = [ yw + 2*rw*sin(alpha[i]) ]
                    xr = len(zr)*xr; yr = len(zr)*yr;
                    doTracelines(xr,yr,zr,step,tmax,nmax)
                
    def save_figure(self):
        from tkFileDialog import asksaveasfilename

        fname = asksaveasfilename(
            master=self.window,
            title='Save the figure',
            filetypes=[
            ('Portable Network Graphics','*.png'),
            ('Encapsulated Postscript File','*.eps'),
            ('Scalable Vector Graphics','*.svg'),

            ])

        if fname == "" :
            return
        else:
            bname, fext = os.path.splitext(fname)
            if fext == '': # No extension provided
                fext = '.png' # Assume png
                fname += fext
            if (fext.lower()=='.png'):
                self.canvas.print_figure(fname, dpi=300)
            elif (fext.lower()=='.eps'):
                self.canvas.print_figure(fname)
            elif (fext.lower()=='.svg'):
                self.canvas.print_figure(fname)

    def _save_figure(self):
        fs = FileDialog.SaveFileDialog(master=self.window,
                                       title='Save the figure')
        try:
            self.lastDir
        except AttributeError:
            self.lastDir = os.curdir
            
        fname = fs.go(dir_or_file=self.lastDir) # , pattern="*.png")
        if fname is None: # Cancel
            return
        
        self.lastDir = os.path.dirname(fname)
        try:
            self.canvas.print_figure(fname)
        except IOError, msg:                
            err = '\n'.join(map(str, msg))
            msg = 'Failed to save %s: Error msg was\n\n%s' % (
                fname, err)
            error_msg_tkpaint(msg)

    def set_active(self, ind):
        self._ind = ind
        self._active = [ self._axes[i] for i in self._ind ]

    def update(self):
        _focus = windowing.FocusManager()
        self._axes = self.canvas.figure.axes
        naxes = len(self._axes)
        #if not hasattr(self, "omenu"):
        #    self.set_active(range(naxes))
        #    self.omenu = AxisMenu(master=self, naxes=naxes)
        #else:
        #    self.omenu.adjust(naxes)
        NavigationToolbar2.update(self)

    def dynamic_update(self):
        'update drawing area only if idle'
        # legacy method; new method is canvas.draw_idle
        self.canvas.draw_idle()

class TracePopup:
    def __init__(self):
        step = 0.02
        self.fields = 'Max space step \n fraction of window', 'Max travel time', 'Max number \n steps', \
        'Relative Elevation \n top=1, bottom=0. \n e.g.: 1, 0.5, 0'
        self.fieldtype = 'float','float','int','eval'
        step = getTrace('step')
        tmax = getTrace('tmax')
        nmax = getTrace('nmax')
        elev = getTrace('elev')
        self.traceVariables = [ step, tmax, nmax, elev ]
        self.popup = Tk.Toplevel()
        self.popup.title('Trace pathline')
        self.vars = []
        for i in range( len(self.fields)):
            row = Tk.Frame(self.popup)
            lab = Tk.Label( row, width=20, text = self.fields[i] )
            ent = Tk.Entry(row)
            row.pack(side=Tk.TOP,fill=Tk.X,padx=5,pady=5)
            lab.pack(side=Tk.LEFT)
            ent.pack(side=Tk.RIGHT,expand=Tk.YES,fill=Tk.X)
            if self.fieldtype[i] == 'float':
                var = Tk.DoubleVar()  # Apparantly you can only define these after the entry is created
            elif self.fieldtype[i] == 'int':
                var = Tk.IntVar()
            elif self.fieldtype[i] == 'eval':
                var = Tk.StringVar()
            ent.config( textvariable = var )
            var.set( self.traceVariables[i] )
            self.vars.append( var )
        # Direction
        forward = getTrace('forward')
        row = Tk.Frame( self.popup )
        lab = Tk.Label( row, width=20, text = 'Direction' )
        row.pack(side=Tk.TOP)
        lab.pack(side=Tk.LEFT)
        self.forward = Tk.IntVar()
        Tk.Radiobutton(row, text="Forward", variable=self.forward, value=1).pack(side=Tk.LEFT)
        Tk.Radiobutton(row, text="Backward", variable=self.forward, value=0).pack(side=Tk.LEFT)
        self.forward.set( forward )
        # Layers
        lab = Tk.Label( self.popup, text = 'Layers' )
        lab.pack(side=Tk.TOP)
        row = Tk.Frame(self.popup)
        row.pack(side=Tk.TOP)
        self.varlayers = []; self.chklayers = []
        for pick in range(0,getActiveNumberLayers(),5):
            row = Tk.Frame(self.popup)
            row.pack(side=Tk.TOP,pady=5)
            for i in range(5):
                if pick+i < getActiveNumberLayers():
                    var = Tk.IntVar()
                    chk = Tk.Checkbutton(row, text=str(pick+i+1), variable=var)
                    chk.pack(side=Tk.LEFT)
                    self.chklayers.append(chk)
                    self.varlayers.append(var)
        layers = getTrace('layers')
        for i in range(len(layers)):
            if layers[i]: self.chklayers[i].select()
        # Capzone number of trace lines
        ncap = getTrace('ncap')
        row = Tk.Frame(self.popup)
        lab = Tk.Label( row, width=20, text = 'Number of trace lines \n for capture zone' )
        ent = Tk.Entry(row)
        row.pack(side=Tk.TOP,fill=Tk.X,padx=5,pady=5)
        lab.pack(side=Tk.LEFT)
        ent.pack(side=Tk.RIGHT,expand=Tk.YES,fill=Tk.X)
        self.Ncapzone = Tk.IntVar()
        ent.config( textvariable = self.Ncapzone )
        self.Ncapzone.set( ncap )
        # Capzone direction
        capzoneforward = getTrace('capzoneforward')
        row = Tk.Frame( self.popup )
        lab = Tk.Label( row, width=20, text = 'Capzone direction' )
        row.pack(side=Tk.TOP)
        lab.pack(side=Tk.LEFT)
        self.capzoneforward = Tk.IntVar()
        Tk.Radiobutton(row, text="Forward", variable=self.capzoneforward, value=1).pack(side=Tk.LEFT)
        Tk.Radiobutton(row, text="Backward", variable=self.capzoneforward, value=0).pack(side=Tk.LEFT)
        self.capzoneforward.set( capzoneforward )
        # OK button           
        b2 = Tk.Button( self.popup, text='OK', command = self.endTrace )
        b2.bind( '<Return>', (lambda event: self.endTrace() ) )
        b2.pack(side=Tk.BOTTOM,padx=5,pady=5)
    def getTraceVariables(self):
        self.traceStep = self.vars[0].get()
        self.tracetmax = self.vars[1].get()
        self.traceNmax = self.vars[2].get()
        self.traceZelev = self.vars[3].get()
        layers = map((lambda var: var.get()), self.varlayers)
        forward = self.forward.get()
        capzoneforward = self.capzoneforward.get()
        return self.traceStep, self.tracetmax, self.traceNmax, self.traceZelev, layers, forward, capzoneforward
    def getNcapzone(self):
        return self.Ncapzone.get()
    def endTrace(self):
        step,tmax,nmax,elev,layers,forward,capzoneforward = self.getTraceVariables()
        setTrace('step',step)
        setTrace('tmax',tmax)
        setTrace('nmax',nmax)
        setTrace('elev',elev)
        setTrace('layers',layers)
        setTrace('forward',forward)
        setTrace('capzoneforward',capzoneforward)
        ncap = self.getNcapzone()
        setTrace('ncap',ncap)
        self.popup.destroy()
        

class Sidebar(Tk.Frame):
    def __init__(self, parent=None):
        Tk.Frame.__init__(self, parent)

class Sidebar_title(Tk.Frame):
    def __init__(self, parent=None):
        Tk.Frame.__init__(self, parent)
        separator = Tk.Frame(self,height=2, bd=1, relief=Tk.SUNKEN)
        separator.pack(fill=Tk.X, padx=5, pady=5)
        sidebar_label = Tk.Label( self, text = 'TimML Model' )
        sidebar_label.pack(side=Tk.TOP, anchor=Tk.N, padx=5)
        #separator = Tk.Frame(self,height=2, bd=1, relief=Tk.SUNKEN)
        #separator.pack(fill=Tk.X, padx=5, pady=5)
        self.modelname = Tk.StringVar()
        sidebar_modelname = Tk.Label( self, textvariable = self.modelname )
        self.modelname.set('No Model Name')
        sidebar_modelname.pack(side=Tk.TOP, anchor=Tk.N, padx=5)
        separator = Tk.Frame(self,height=2, bd=1, relief=Tk.SUNKEN)
        separator.pack(fill=Tk.X, padx=5, pady=5)
    def set_modelname(self,name):
        self.modelname.set(name)

class Sidebar_message(Tk.Frame):
    def __init__(self, parent=None):
        Tk.Frame.__init__(self, parent)
        separator = Tk.Frame(self,height=2, bd=1, relief=Tk.SUNKEN)
        separator.pack(fill=Tk.X, padx=5, pady=5)
        sidebar_label = Tk.Label( self, text = 'TimML Messages' )
        sidebar_label.pack(side=Tk.TOP, anchor=Tk.N, padx=5)
        separator = Tk.Frame(self,height=2, bd=1, relief=Tk.SUNKEN)
        separator.pack(fill=Tk.X, padx=5, pady=5)
        self.message = Tk.StringVar()
        sidebar_message = Tk.Label( self, textvariable = self.message)
        self.message.set('No Message')
        sidebar_message.pack(side=Tk.TOP, anchor=Tk.N, padx=5)
        separator = Tk.Frame(self,height=2, bd=1, relief=Tk.SUNKEN)
        separator.pack(fill=Tk.X, padx=5, pady=5)
    def set_message(self,name):
        self.message.set(name)

class Sidebar_layers(Tk.Frame):
    def __init__(self, parent=None, side=Tk.TOP, anchor=Tk.W):
        Tk.Frame.__init__(self, parent)
        lab = Tk.Label( self, text = 'Layers' )
        lab.pack(side=Tk.TOP)
        row = Tk.Frame(self)
        row.pack(side=Tk.TOP)
        self.vars = []
        for pick in range(0,getActiveNumberLayers(),3):
            row = Tk.Frame(self)
            row.pack(side=Tk.TOP,pady=5)
            for i in range(3):
                if pick+i < getActiveNumberLayers():
                    var = Tk.IntVar()
                    chk = Tk.Checkbutton(row, text=str(pick+i+1), variable=var)
                    chk.pack(side=Tk.LEFT, anchor=anchor )
                    self.vars.append(var)
                    if pick == 0 and i == 0:
                        chk.select()
    def state(self):
        return map((lambda var: var.get()), self.vars)

class Sidebar_button(Tk.Frame):
    def __init__(self, parent, txt, cmd):
        Tk.Frame.__init__(self, parent)
        Tk.Button( self, text=txt, command=cmd, width = 12 ).pack(side=Tk.TOP,padx=5)

class Sidebar_button_mes(Tk.Frame):
    def __init__(self, parent, txt, cmd, mes):
        Tk.Frame.__init__(self, parent)
        self.cmd = cmd
        self.mes = mes
        Tk.Button( self, text=txt, command=self.action, width = 12 ).pack(side=Tk.TOP,padx=5)
    def action(self):
        self.cmd()
        set_message(self.mes)
class Sidebar_button_mes2(Tk.Frame):
    def __init__(self, parent, txt, cmd, mes1, mes2):
        Tk.Frame.__init__(self, parent)
        self.cmd = cmd
        self.mes1 = mes1
        self.mes2 = mes2
        Tk.Button( self, text=txt, command=self.action, width = 12 ).pack(side=Tk.TOP,padx=5)
    def action(self):
        set_message(self.mes1)
        self.cmd()
        set_message(self.mes2)

class Sidebar_button_plus(Tk.Frame):
    def __init__(self, parent, txt, cmd, vartxt, varinit):
        Tk.Frame.__init__(self, parent)
        Tk.Button( parent, text=txt, command=cmd, width = 12 ).pack(side=Tk.TOP,padx=5)
        lab = Tk.Label( parent, width=10, text = vartxt )
        ent = Tk.Entry( parent )
        lab.pack(side=Tk.LEFT)
        ent.pack(side=Tk.RIGHT,expand=Tk.YES,fill=Tk.X)
        self.var = Tk.IntVar()
        ent.config( textvariable = self.var )
        self.var.set( varinit )
    def get_value(self):
        return self.var.get()

class Sidebar_contour(Tk.Frame):
    def __init__(self, parent):
        Tk.Frame.__init__(self, parent)
        self.parent = parent
        Tk.Button( parent, text='Contour', command=self.contour, width = 12 ).pack(side=Tk.TOP,padx=5)
        row = Tk.Frame(parent)
        lab = Tk.Label( row, text = 'Points' )
        ent = Tk.Entry( row, width = 4 )
        row.pack(side=Tk.TOP,pady=5)
        lab.pack(side=Tk.LEFT)
        #ent.pack(side=Tk.RIGHT,expand=Tk.YES,fill=Tk.X)
        ent.pack(side=Tk.RIGHT,padx=5)
        self.var = Tk.IntVar()
        ent.config( textvariable = self.var )
        self.var.set( 40 )
        self.contour_show = None
    def get_value(self):
        return self.var.get()
    def close_contour_show(self):
        if self.contour_show != None: self.contour_show.destroy()
    def start_contouring(self):
        if self.contour_show != None: self.contour_show.destroy()
        set_message('Contouring....')
    def contour(self):
        N = self.get_value()
        self.start_contouring()
        setActiveWindow()
        setActiveHeads(N)
        hmin,hmax = getMinMaxHeads()
        if abs(hmin) < 10000:
            minmes = 'min head: %.2f'%hmin
        else:
            minmes = 'min head: %.3e'%hmin
        if abs(hmin) < 10000:
            maxmes = 'max head: %.2f'%hmax
        else:
            maxmes = 'max head: %.3e'%hmax
        set_message(minmes+'\n'+maxmes)
        self.contour_show = Sidebar_contour_show(self.parent)
        self.contour_show.pack(side=Tk.TOP)

class Sidebar_contour_show(Tk.Frame):
    def __init__(self, parent):
        Tk.Frame.__init__(self, parent)
        # Make layer widget
        Tk.Frame(self,height=2, bd=1, relief=Tk.SUNKEN).pack(fill=Tk.X, padx=5, pady=5)
        self.layers = Sidebar_layers( self, side=Tk.TOP )
        self.layers.pack( side=Tk.TOP )
        Tk.Frame(self,height=2, bd=1, relief=Tk.SUNKEN).pack(fill=Tk.X, padx=5, pady=5)
        # Specify number of contour lines
        lab = Tk.Label( self, text = '# Contours' ).pack( side = Tk.TOP )
        row = Tk.Frame(self)
        but = Tk.Button( row, text='Show', command=self.show_contour_numlines )
        ent = Tk.Entry( row, width = 4 )
        row.pack(side=Tk.TOP,pady=5)
        but.pack(side=Tk.LEFT,padx=5)
        ent.pack(side=Tk.RIGHT,padx=5)
        self.var_numlines = Tk.IntVar()
        ent.config( textvariable = self.var_numlines )
        self.var_numlines.set( 10 )
        Tk.Frame(self,height=2, bd=1, relief=Tk.SUNKEN).pack(fill=Tk.X, padx=5, pady=5)
        # Specify level
        Tk.Label( self, text = 'Contours Levels' ).pack( side = Tk.TOP )
        fields = ['min','max','int']
        self.cont_vars = []
        for i in range( len(fields)):
            row = Tk.Frame(self,width=12)
            lab = Tk.Label( row, text = fields[i], anchor = Tk.W )
            ent = Tk.Entry(row,width=8)
            row.pack(side=Tk.TOP,fill=Tk.X,padx=5)
            lab.pack(side=Tk.LEFT)
            ent.pack(side=Tk.RIGHT)
            var = Tk.DoubleVar()  # Apparantly you can only define these after the entry is created
            ent.config( textvariable = var )
            self.cont_vars.append( var )
        but = Tk.Button( self, text='Show', width = 12, command=self.show_contour_minmaxstep )
        but.pack(side=Tk.TOP,padx=5)
        Tk.Frame(self,height=2, bd=1, relief=Tk.SUNKEN).pack(fill=Tk.X, padx=5, pady=5)
        Tk.Button( self, text='Label Contour', command=self.label_contours, width=12 ).pack(side=Tk.TOP)
    def get_numlines(self):
        return self.var_numlines.get()
    def get_layers(self):
        return self.layers.state()
    def get_minmaxstep(self):
        min = self.cont_vars[0].get()
        max = self.cont_vars[1].get()
        step = self.cont_vars[2].get()
        return min,max,step
    def show_contour_numlines(self):
        showlay = self.get_layers()
        lay = []
        for i in range( len(showlay) ):
            if showlay[i]: lay.append( i )
        numlines = self.get_numlines()
        showContours( lay, numlines )
    def show_contour_minmaxstep(self):
        showlay = self.get_layers()
        lay = []
        for i in range( len(showlay) ):
            if showlay[i]: lay.append( i )
        min,max,step = self.get_minmaxstep()
        print arange(min,max,step)
        showContours( lay, arange(min,max,step) )
    def label_contours(self):
        labelContours()



def set_message(mes):
    getActiveGui().messagebox.set_message(mes)

def notdone():  
    showerror('Not implemented', 'Not yet available')

def openfile():
    file = askopenfilename(title='Open TimML model',
           filetypes=[('TimML Python script','*.py'),('TimML solution','*.sol'),])
    modelpath,modelfile = os.path.split(file)   
    modelname,modelext = string.split(modelfile,'.')
    if sys.path[-1] != modelpath: sys.path.append( modelpath )  # Add directory to model path
    if getActiveModel() != None:
        clearmodel()
    if modelext == 'py':
        exec 'from '+modelname+' import *'
        getActiveGui().toptitle.set_modelname(modelname)
    elif modelext == 'sol':
        notdone()
    else:
        notdone()
    layoutmodel_extend()
    getActiveGui().contourbutton.close_contour_show()
    set_message('Model loaded')

def savefile():
    file = asksaveasfilename( title='Save TimML model', filetypes=[('TimML solution','*.sol'),] )
    print file

def contourcolor():
    color = askcolor( title='Contour color' )
    print color

def createPopup(fields,initialvalues,buttons,labfuncs):
    popup = Tk.Toplevel()
    popup.title('Contour')
    vars = []
    for i in range( len(fields)):
        row = Tk.Frame(popup)
        lab = Tk.Label( row, width=10, text = fields[i] )
        ent = Tk.Entry(row)
        row.pack(side=Tk.TOP,fill=Tk.X)
        lab.pack(side=Tk.LEFT)
        ent.pack(side=Tk.RIGHT,expand=Tk.YES,fill=Tk.X)
        if type( initialvalues[i] ) is float:
            var = Tk.DoubleVar()  # Apparantly you can only define these after the entry is created
        elif type( initialvalues[i] ) is int:
            var = Tk.IntVar()
        elif type( initialvalues[i] ) is list:
            var = Tk.StringVar()
        ent.config( textvariable = var )
        var.set( initialvalues[i] )
        vars.append( var )
    for i in range( len(buttons) ):
        b = Tk.Button( popup, text=buttons[i], command = (labfuncs[i]))
        b.bind( '<Return>', labfuncs[i] )
        b.pack(side=Tk.LEFT)
        b.focus_force()

def contourpopup():
    createPopup(['min','max'],[3.0,5.0],['Contour','Stop'],[(lambda : 'Hello'),(lambda : popup.detroy())] )


##class SettingsPopup:
##    def __init__(self):
##        self.popup = Tk.Toplevel()
##        self.popup.title('Colors')
##        
##        row = Tk.Frame(self.popup)
##        lab = Tk.Label( row, width=10, text = 'Layout' )
##        self.labcol = Tk.Label( row, width = 5, bg=getColor('Layout') )
##        row.pack(side=Tk.TOP,fill=Tk.X,padx=5,pady=5)
##        lab.pack(side=Tk.LEFT)
##        self.labcol.pack( side=Tk.RIGHT, padx=5 )
##        ent.pack(side=Tk.RIGHT)
##        self.var = Tk.IntVar()
##        ent.config( textvariable = self.var )
##        self.var.set( 1 )
##        b = Tk.Button( self.popup, text='Change Color', command = self.changecolor )
##
##
##        
##        row = Tk.Frame(self.popup)
##        lab = Tk.Label( row, width=10, text = 'Layer' )
##        self.labcol = Tk.Label( row, width = 5, bg=getColor('Contour',0) )
##        ent = Tk.Entry(row, width = 4)
##        ent.bind( '<Return>', (lambda event: self.initial_color() ) )
##        row.pack(side=Tk.TOP,fill=Tk.X,padx=5,pady=5)
##        lab.pack(side=Tk.LEFT)
##        self.labcol.pack( side=Tk.RIGHT, padx=5 )
##        ent.pack(side=Tk.RIGHT)
##        self.var = Tk.IntVar()
##        ent.config( textvariable = self.var )
##        self.var.set( 1 )
##        b = Tk.Button( self.popup, text='Change Color', command = self.changecolor )
##        #b.bind( '<Return>', (lambda event: self.grid() ) )
##        b.pack(side=Tk.LEFT,padx=5,pady=5)
##        #b.focus_force()
##        self.b2 = Tk.Button( self.popup, text='OK', command = self.popup.destroy )
##        #b2.bind( '<Return>', (lambda event: self.endTrace() ) )
##        self.b2.pack(side=Tk.RIGHT,padx=5)
##    def changecolor(self):
##        color = askcolor( title='Change Color' )
##        lay = self.getLayer()
##        setColor( color[1], 'Contour', lay-1 )
##        self.labcol.config( bg = color[1] )
##        self.b2.focus_force()
##    def initial_color(self):
##        lay = self.getLayer()
##        self.labcol.config( bg = getColor('Contour',lay-1) )
##    def getLayer(self):
##        lay = self.var.get()
##        return lay


# Some code so that you know what button is pressend

class SimpleCallback:
    def __init__(self, callback, number):
            self.__callback = callback
            self.number = number
    def __call__(self):
            return self.__callback (self.number)


## Test implementation to give a list of all colors; does not work properly
class SettingsPopup:
    def __init__(self):
        self.popup = Tk.Toplevel()
        self.popup.title('Colors')
        row = Tk.Frame(self.popup)
        lab = Tk.Label( row, width=10, text = 'Layout' ).pack( side = Tk.LEFT, padx = 5 )
        self.butlay = Tk.Button( row, width = 4, command = self.changecolorlayout, bg=getColor('Layout')  )
        row.pack( side = Tk.TOP )
        self.butlay.pack( side = Tk.RIGHT, padx = 5, pady = 5 )
        nlay = getActiveNumberLayers()
        self.butcontlist = []; self.buttracelist = []
        lab = Tk.Label( self.popup, width=10, text = 'Contour lines' ).pack( side = Tk.TOP, padx = 5, pady = 5 )
        row = Tk.Frame(self.popup)
        lab = Tk.Label( row, width=5, text = 'Layer ' ).pack( side = Tk.LEFT, padx = 5 )
        lab = Tk.Label( row, width=8, text = 'Trace' ).pack( side = Tk.RIGHT, padx = 5 )
        lab = Tk.Label( row, width=8, text = 'Contour' ).pack( side = Tk.RIGHT, padx = 5 )
        row.pack( side = Tk.TOP )
        for i in range(nlay):
            row = Tk.Frame(self.popup)
            lab = Tk.Label( row, width=5, text = 'Layer '+str(i+1) ).pack( side = Tk.LEFT, padx = 5 )
            callbacktrace = SimpleCallback( self.changecolortrace, i )
            but1 = Tk.Button( row, width = 8, command = callbacktrace, bg=getColor('Trace',i)  )
            callbackcontour = SimpleCallback( self.changecolorcontour, i )
            but2 = Tk.Button( row, width = 8, command = callbackcontour, bg=getColor('Contour',i)  )
            row.pack( side = Tk.TOP )
            but1.pack( side = Tk.RIGHT, padx = 5 )
            but2.pack( side = Tk.RIGHT, padx = 5 )
            self.buttracelist.append(but1)
            self.butcontlist.append(but2)
        self.b2 = Tk.Button( self.popup, text='OK', command = self.popup.destroy )
        #b2.bind( '<Return>', (lambda event: self.endTrace() ) )
        self.b2.pack(side=Tk.TOP,padx=5,pady=5)
    def changecolorlayout(self):
        color = askcolor( title='Change Color' )
        setColor( color[1], 'Layout' )
        self.butlay.config( bg = color[1] )
        self.b2.focus_force()
    def changecolorcontour(self,i):
        color = askcolor( title='Change Color' )
        setColor( color[1], 'Contour', i )
        self.butcontlist[i].config( bg = color[1] )
        self.b2.focus_force()
    def changecolortrace(self,i):
        color = askcolor( title='Change Color' )
        setColor( color[1], 'Trace', i )
        self.buttracelist[i].config( bg = color[1] )
        self.b2.focus_force()
##    def initial_color(self):
##        lay = self.getLayer()
##        self.labcol.config( bg = getColor('Contour',lay-1) )
    def getLayer(self):
        lay = self.var.get()
        return lay

class ContourLabelPopup:
    def __init__(self):
        self.popup = Tk.Toplevel()
        self.popup.title('Contour Labels')
        # Format
        row = Tk.Frame(self.popup)
        lab = Tk.Label( row, width=10, text = 'Label format' )
        ent = Tk.Entry(row, width = 8)
        row.pack(side=Tk.TOP,fill=Tk.X,padx=5,pady=5)
        lab.pack(side=Tk.LEFT)
        ent.pack(side=Tk.RIGHT)
        self.format = Tk.StringVar()
        ent.config( textvariable = self.format )
        self.format.set( getContourLabelFormat() )
        # Font size
        row = Tk.Frame(self.popup)
        lab = Tk.Label( row, width=10, text = 'Font size' )
        ent = Tk.Entry(row, width = 8)
        row.pack(side=Tk.TOP,fill=Tk.X,padx=5,pady=5)
        lab.pack(side=Tk.LEFT)
        ent.pack(side=Tk.RIGHT)
        self.size = Tk.IntVar()
        ent.config( textvariable = self.size )
        self.size.set( getContourLabelSize() )
        # OK button
        b = Tk.Button( self.popup, text='OK', command = self.ok ).pack(side=Tk.TOP)
    def ok(self):
        format = self.format.get()
        setContourLabelFormat(format)
        size = self.size.get()
        setContourLabelSize(size)        
        self.popup.destroy()
    
def makemenu(win):
    top = Tk.Menu(win)                                # win=top-level window
    win.config(menu=top)                           # set its menu option
    
    file = Tk.Menu(top, tearoff=0)
    file.add_command(label='Open',  command=openfile,  underline=0)
##    file.add_command(label='Save',  command=savefile, underline=0)
##    file.add_command(label='Export',command=notdone, underline=0)
    file.add_command(label='Quit',  command=win.quit, underline=0)
    top.add_cascade(label='File',   menu=file,        underline=0)

##    tools = Tk.Menu(top, tearoff=0)
##    tools.add_command(label='Solve',   command=solvemodel,  underline=0)
##    tools.add_command(label='Contour', command=notdone,  underline=0)
##    tools.add_command(label='Test',    command=contourpopup,  underline=0)
##    #tools.add_separator()
##    top.add_cascade(label='Tools',     menu=tools,        underline=0)

    settings = Tk.Menu(top, tearoff=0)
    settings.add_command(label='Colors',   command=SettingsPopup,  underline=0)
    settings.add_command(label='Contour labels',   command=ContourLabelPopup,  underline=0)
    settings.add_command(label='Tracing',   command=TracePopup,  underline=0)
    top.add_cascade(label='Settings',     menu=settings,        underline=0)
    
class start:
    def __init__(self,model=None):
        root = Tk.Tk()
        root.wm_title("TimML")
        fig = Figure(figsize=(8,6), dpi=100)
        ax = fig.add_axes( (0.1, 0.1, 0.8, 0.8) )
        ax.set_aspect('equal')
        setActiveAxis(ax)

        self.sidebar = Sidebar( root )
        self.sidebar.pack( side=Tk.RIGHT, fill=Tk.Y)
        self.toptitle = Sidebar_title( self.sidebar )
        self.toptitle.pack( side=Tk.TOP )
        self.messagebox = Sidebar_message( self.sidebar )
        self.messagebox.pack( side=Tk.BOTTOM )
        def set_message(mes):
            self.messagebox.set_message(mes)
        self.solvebutton = Sidebar_button_mes2( self.sidebar, 'Solve', solvemodel, 'Solving...', 'Solution complete' )
        self.solvebutton.pack( side=Tk.TOP )
        self.clearbutton = Sidebar_button( self.sidebar, 'Clear Plot', clearmodel )
        self.clearbutton.pack( side=Tk.TOP )
        self.layoutbutton = Sidebar_button( self.sidebar, 'Layout', layoutmodel )
        self.layoutbutton.pack( side=Tk.TOP )
        self.contourbutton = Sidebar_contour( self.sidebar )
        self.contourbutton.pack( side=Tk.TOP )
        setActiveSettings()

        # a tk.DrawingArea
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.show()
        canvas.get_tk_widget().pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)

        toolbar = NavigationToolbar2TkAgg( canvas, root )
        toolbar.update()
        canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        setActiveCanvas(canvas)
        makemenu(root)
        setActiveGui(self)
        if model != None:
            setActiveModel(model)
            layoutmodel_extend()

ActiveGui = None
def setActiveGui(gui):
    global ActiveGui
    ActiveGui = gui

def getActiveGui():
    global ActiveGui
    return ActiveGui

if __name__ == '__main__':
    start()
    Tk.mainloop()
