from TimML import *

ml = Model3D([40,30,20,10,0])

uf = Uflow(ml,0.01,0)

rf = Constant(ml,200,0,50)

xp = [-100,100,100,-100,-100]
yp = [-100,-100,100,100,-100]
for i in range(len(xp)-1):
    LineDoubletImp(ml,xp[i],yp[i],xp[i+1],yp[i+1],order=5,layers=[1,2])

w = Well(ml,0,0,400,.1)

# pycontour(ml,-300,300,200,-200,200,200,[1,4],[16,1,60],xsec=1)
# pytracelines(ml,4*[-200],4*[25],[5,15,25,35],2,Nmax=400,xsec=1)
