"""Small column-vector rigid transform toolkit (angles in degrees)."""
import math

def identity(): return [[float(i==j) for j in range(4)] for i in range(4)]

def mul(a,b): return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

def chain(*xs):
    m=identity()
    for x in xs:m=mul(m,x)
    return m

def translation(x,y,z):
    m=identity();m[0][3]=x;m[1][3]=y;m[2][3]=z;return m

def scale(x,y=None,z=None):
    if y is None:y=z=x
    m=identity();m[0][0]=x;m[1][1]=y;m[2][2]=z;return m

def rotate(axis,degrees):
    a=math.radians(degrees);c=math.cos(a);s=math.sin(a);m=identity()
    i,j={'x':(1,2),'y':(2,0),'z':(0,1)}[axis]
    m[i][i]=m[j][j]=c;m[i][j]=-s;m[j][i]=s;return m

def quaternion(m):
    t=sum(m[i][i] for i in range(3))
    if t>0:
        s=math.sqrt(t+1)*2
        q=((m[2][1]-m[1][2])/s,(m[0][2]-m[2][0])/s,(m[1][0]-m[0][1])/s,s/4)
    else:
        i=max(range(3),key=lambda k:m[k][k]);j=(i+1)%3;k=(i+2)%3
        s=math.sqrt(1+m[i][i]-m[j][j]-m[k][k])*2
        q=[0.]*4;q[i]=s/4;q[j]=(m[j][i]+m[i][j])/s;q[k]=(m[k][i]+m[i][k])/s;q[3]=(m[k][j]-m[j][k])/s
    norm=math.sqrt(sum(x*x for x in q));return tuple(x/norm for x in q)

def from_pose(pos,q):
    x,y,z,w=q;m=identity()
    m[0][:3]=[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)]
    m[1][:3]=[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)]
    m[2][:3]=[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]
    for i in range(3):m[i][3]=pos[i]
    return m

def slerp(a,b,t):
    dot=sum(x*y for x,y in zip(a,b))
    if dot<0:b=tuple(-x for x in b);dot=-dot
    if dot>0.9995:q=tuple(x+(y-x)*t for x,y in zip(a,b))
    else:
        theta=math.acos(max(-1,min(1,dot)))
        q=tuple((math.sin((1-t)*theta)*x+math.sin(t*theta)*y)/math.sin(theta) for x,y in zip(a,b))
    n=math.sqrt(sum(x*x for x in q));return tuple(x/n for x in q)
