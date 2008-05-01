from TimML import *
ml=Model(1,[1],[0],[10],[])
p=PolygonInhom(ml,2,[2,4],[5,0],[10,4],[100],\
  [(20,0),(50,0),(50,50),(0,40),(0,10)])
AquiferSystemInhomogeneity(ml,[(20,0),(50,0),(50,25),(50,50),(25,45),(0,40),(0,25),(0,10),(10,5)],p,ml.aq)
rf = Constant(ml,100,100,50,[1])
w = Well(ml,20,20,100,.1,[2])
