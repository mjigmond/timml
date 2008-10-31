from TimML import *
ml=Model(2,[1,2],[18,0],[30,12],[2000])
xylist = [(500,-500),(500,500),(-500,500),(-500,-500)]
inhom = PolygonInhom(ml,2,[10,.2],[20,0],[30,10],[5000],xylist)
MakeInhomSide(ml, xylist, inhom, ml.aq, 7, closed = True)
uf=Uflow(ml,0.02,45)
rf = Constant(ml,0,0,15,[1])



