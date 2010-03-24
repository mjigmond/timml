from TimML import *

ml=Model(2,[10,20],[2,0],[3,1],[2000])

xylist1 = [(500,0),(500,500),(-500,500),(-500,0)]
xylist2 = [(-500,0),(-500,-500),(500,-500),(500,0)]
xylist3 = [(-500,0),(500,0)]

inhom1 = PolygonInhom(ml,2,[100,2],[2,0],[3,1],[20000],xylist1)
inhom2 = PolygonInhom(ml,2,[2,2],[2,0],[3,1],[2000],xylist2)

MakeInhomPolySide(ml, xylist1, 8, closed = False)
MakeInhomPolySide(ml, xylist2, 8, closed = False)
MakeInhomPolySide(ml, xylist3, 8, closed = False)

uf=Uflow(ml,0.02,45)

rf = Constant(ml,0,0,15,[1])


