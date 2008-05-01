from TimML import *
ml=Model(3,[2,6,4],[140,80,0],[165,120,60],[2000,20000],n=[0.3,0.25,0.3],nll=[0.2,0.25])
rf=Constant(ml,20000,20000,175,[1])
p=CircAreaSink(ml,10000,10000,15000,0.0002,[1])
w1=Well(ml,10000,8000,3000,.3,[2],'well 1')
w2=Well(ml,12000,8000,5000,.3,[3],'well 2')
w3=Well(ml,10000,4600,5000,.3,[2,3],'maq well')
#
HeadLineSink(ml, 9510,  19466, 12620, 17376, 170,[1])
HeadLineSink(ml, 12620, 17376, 12753, 14976, 168,[1])
HeadLineSink(ml, 12753, 14976, 13020, 12176, 166,[1])
HeadLineSink(ml, 13020, 12176, 15066, 9466,  164,[1])
HeadLineSink(ml, 15066, 9466,  16443, 7910,  162,[1])
HeadLineSink(ml, 16443, 7910,  17510, 5286,  160,[1])
HeadLineSink(ml, 17510, 5286,  17600, 976,   158,[1])
#
HeadLineSink(ml, 356,   6976,  4043,  7153, 174,[1])
HeadLineSink(ml, 4043,  7153,  6176,  8400, 171,[1])
HeadLineSink(ml, 6176,  8400,  9286,  9820, 168,[1])
HeadLineSink(ml, 9286,  9820,  12266, 9686, 166,[1])
HeadLineSink(ml, 12266, 9686,  15066, 9466, 164,[1])
#
HeadLineSink(ml, 1376,  1910,  4176,  2043, 170,[1])
HeadLineSink(ml, 4176,  2043,  6800,  1553, 166,[1])
HeadLineSink(ml, 6800,  1553,  9953,  2086, 162,[1])
HeadLineSink(ml, 9953,  2086,  14043, 2043, 160,[1])
HeadLineSink(ml, 14043, 2043,  17600, 976 , 158,[1])
#

def matlab_trace_example1():
    an = arange(0,2*pi,pi/5.0)
    matlabtracelines(ml,w1.xw+cos(an),w1.yw+sin(an),100*ones(len(an)),-100,'/mark/timmlscripts/example1tracew1.m',Nmax=500)
    matlabtracelines(ml,w2.xw+cos(an),w2.yw+sin(an),30*ones(len(an)),-100,'/mark/timmlscripts/example1tracew2.m',Nmax=500)
    matlabtracelines(ml,w3.xw+cos(an),w3.yw+sin(an),100*ones(len(an)),-100,'/mark/timmlscripts/example1tracew3.m',tmax=200*365,Nmax=200)

##def pylab_trace_example1():
##    an = arange(0,2*pi,pi/5.0)
##    pytracelines(ml,w1.xw+cos(an),w1.yw+sin(an),100*ones(len(an)),-100,Nmax=500)
##    pytracelines(ml,w2.xw+cos(an),w2.yw+sin(an),30*ones(len(an)),-100,Nmax=500)
##    pytracelines(ml,w3.xw+cos(an),w3.yw+sin(an),100*ones(len(an)),-100,tmax=200*365,Nmax=200)

