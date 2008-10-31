from TimML import *

xcor = [-500,0,500,500,-500]
ycor = [-100,-100,0,100,100]
ml=Model(1,[1],[0],[20])
Constant(ml,0,1000,25)
Lake(ml,zip(xcor,ycor),22,800,2,Lmax=200,areatol=0.1)
Well(ml,0,-200,750,.1)
ml.solve(doIterations=1)
