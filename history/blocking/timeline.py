# Historical authored revision; duplicate shared helpers and all assets are omitted.
"""Deterministic 20-second race blocking; no vehicle asset assumptions.
Distance curves are monotone Hermite, wheels follow travelled distance.
The 9.7–12s jump is a deliberate ~2.7x cinematic time expansion of a
0.84s ballistic hop (~0.86m rise), not a weightless 2.3s physical flight.
"""
import math,bisect
from mathutils import Vector
from course import ROAD,GRAVEL

def ease(x):
 x=max(0,min(1,x));return x*x*(3-2*x)
class Route:
 def __init__(self,pts):
  self.points=pts;self.dist=[0]
  for a,b in zip(pts,pts[1:]):self.dist.append(self.dist[-1]+(b-a).length)
 def at(self,d):
  i=max(0,min(len(self.dist)-2,bisect.bisect_right(self.dist,d)-1));q=(d-self.dist[i])/(self.dist[i+1]-self.dist[i]);return self.points[i].lerp(self.points[i+1],q)
 def nearest(self,x,y):
  p=Vector((x,y));best=(1e30,0)
  for i,(a,b) in enumerate(zip(self.points,self.points[1:])):
   v=b-a;q=max(0,min(1,(p-a).dot(v)/v.length_squared));err=(p-(a+q*v)).length_squared
   if err<best[0]:best=(err,self.dist[i]+q*v.length)
  return best[1]
class Monotone:
 def __init__(self,keys):
  self.x=[k[0] for k in keys];self.y=[k[1] for k in keys];d=[(self.y[i+1]-self.y[i])/(self.x[i+1]-self.x[i]) for i in range(len(keys)-1)];self.m=[d[0]]+[0 if d[i-1]*d[i]<=0 else 2/(1/d[i-1]+1/d[i]) for i in range(1,len(d))]+[d[-1]]
 def __call__(self,t):
  i=max(0,min(len(self.x)-2,bisect.bisect_right(self.x,t)-1));h=self.x[i+1]-self.x[i];q=(t-self.x[i])/h
  return (2*q**3-3*q*q+1)*self.y[i]+(q**3-2*q*q+q)*h*self.m[i]+(-2*q**3+3*q*q)*self.y[i+1]+(q**3-q*q)*h*self.m[i+1]
main=Route(ROAD)
a=min(range(len(ROAD)),key=lambda i:(ROAD[i]-Vector((-45,0))).length_squared)
b=min(range(len(ROAD)),key=lambda i:(ROAD[i]-Vector((45,0))).length_squared)
short=Route(ROAD[:a]+GRAVEL+ROAD[b+1:])
hero_keys=[(0,-105,-22),(3,-50,-5),(5,-29,4),(9,17,4),(9.7,24,3),(12,45,0),(16,97,-22),(17.5,114,-22),(18.5,140,-22),(20,175,-22)]
rival_keys=[(0,-99,-22),(3,-45,0),(5,-27,35),(9,30,32),(12,55,-8),(16,97,-22),(17.5,113,-22),(18.5,138,-22),(20,174,-22)]
def key_dist(route,keys):
 out=[]
 for t,x,y in keys:
  d=route.nearest(x,y)
  if x>150:d=route.dist[-1]+x-150
  out.append((t,d))
 return out
H=Monotone(key_dist(short,hero_keys));R=Monotone(key_dist(main,rival_keys))
def pose(t,hero=True):
 route,curve=(short,H) if hero else (main,R);d=curve(t);p=route.at(d);prev=route.at(curve(t-.01));nxt=route.at(curve(t+.01));tan=(nxt-prev).normalized();yaw=math.atan2(tan.y,tan.x);speed=(curve(t+.01)-curve(t-.01))/.02
 # Separated lanes on the final straight; no body intersections at the finish.
 lateral=(-1.15 if hero else 1.15)*ease((t-12)/2);p+=Vector((-tan.y,tan.x))*lateral
 slide=.32*math.sin(math.pi*max(0,min(1,(t-5)/4))) if hero and 5<t<9 else 0
 z=.03;pitch=0;roll=-slide*.15;compression=0
 if hero:
  if t<9.7:
   z+=.62*math.exp(-((p.x-24)/4.2)**2);pitch=-math.radians(12)*ease((t-9.35)/.35)
  if 9.7<=t<=12:
   q=(t-9.7)/2.3;z+=.62*(1-q)+4*.86*q*(1-q);pitch=math.radians(-12+23*q)
  if t>12:pitch=math.radians(11)*math.cos((t-12)*16)*math.exp(-(t-12)*8)
  compression=.11*math.exp(-((t-12.06)/.09)**2)-.045*math.exp(-((t-12.25)/.12)**2)
  pitch+=math.radians(2.5)*math.exp(-((t-3.8)/.5)**2)
 return {'position':(p.x,p.y,z),'compression':compression,'yaw':yaw+slide,'pitch':pitch,'roll':roll,'steer':-slide*.8,'distance':d,'speed':speed,'jump':9.7<t<12 if hero else False}

def camera_pose(t):
 h=Vector(pose(t)['position']);r=Vector(pose(t,False)['position'])
 if t<3:
  target=(h+r)/2+Vector((0,0,.65));pos=target+Vector((6,-9,1.1));lens=40
 elif t<5:
  target=Vector((0,9,0));pos=Vector((-6,-62,76));lens=34
 elif t<9:
  target=h+Vector((0,0,.7));pos=h+Vector((8,-11,2.1));lens=48
 elif t<12:
  target=h+Vector((1,0,.65));pos=h+Vector((8,-14,3.2));lens=45
 elif t<16:
  target=h+Vector((1,0,.6));pos=h+Vector((6,-9,1.4));lens=43
 else:
  target=Vector((112,-22,.7));pos=Vector((112,-39,6.5));lens=42
 # One damped landing impact; no arbitrary shaking through the entire film.
 if 12<=t<12.6:
  e=math.exp(-(t-12)*8);pos+=Vector((.08*math.sin(t*71),.04*math.cos(t*83),.10*math.sin(t*61)))*e
 return pos,target,lens
