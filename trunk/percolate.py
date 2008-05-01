from TimML import *

ml = Model( 1, [1], [0], [10] )

x = linspace(-200,200,20)

for i in range(len(x)-1):
    ResLineSink(ml,x[i],0,x[i+1],0,10,10,2,bottomelev=9.5)

y = linspace(-10,-100,5)

for i in range(len(y)-1):
    HeadLineSink( ml, 0, y[i], 0, y[i-1], 7, [1] )

rf = Constant( ml, 0, -200, 12 )

p = CircAreaSink(ml,0,0,300,0)

ml.solve(doIterations=True)




