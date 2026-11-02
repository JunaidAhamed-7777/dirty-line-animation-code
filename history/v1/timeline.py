# Historical authored revision; duplicate shared helpers and all assets are omitted.
"""DIRTY LINE22.32s deterministic grounded race motion and authored six-shot camera.
Monotone distance curves drive wheel rotation; short crest hop is time-expanded1.14s.
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
hero_keys=[(0,-105,-22),(2.79,-50,-5),(4.65,-36,3),(8.37,0,6),(10.95,33,1.5),(12.09,45,0),(17.67,95,-22),(19.53,110,-22),(20.6,143,-22),(22.32,183,-22)]
rival_keys=[(0,-99,-22),(2.79,-45,0),(4.65,-28,34),(8.37,17,41),(10.95,43,6),(12.09,50,-4.5),(17.67,95,-22),(19.53,109.43,-22),(20.6,142,-22),(22.32,182,-22)]
def key_dist(route,keys):
 out=[]
 for t,x,y in keys:
  d=route.nearest(x,y)
  if x>150:d=route.dist[-1]+x-150
  out.append((t,d))
 return out
H=Monotone(key_dist(short,hero_keys));R=Monotone(key_dist(main,rival_keys))
def ramp_contact(x):
 F=1.07554244995*(4.24/4.4);B=-1.22747540474*(4.24/4.4);r=.3297740221*(4.24/4.4)
 def h(q):return .036+.35*math.exp(-((q-33)/3.7)**2)
 theta=-math.atan2(h(x+F)-h(x+B),F-B)
 for _ in range(2):
  xf=x+F*math.cos(theta)+r*math.sin(theta);xb=x+B*math.cos(theta)+r*math.sin(theta);theta=-math.atan2(h(xf)-h(xb),(F-B)*math.cos(theta))
 z=max(h(xf)+F*math.sin(theta)-r*(math.cos(theta)-1),h(xb)+B*math.sin(theta)-r*(math.cos(theta)-1))
 return z,theta

def pose(t,hero=True):
 route,curve=(short,H) if hero else (main,R);d=curve(t);p=route.at(d);prev=route.at(curve(t-.01));nxt=route.at(curve(t+.01));tan=(nxt-prev).normalized();yaw=math.atan2(tan.y,tan.x);speed=(curve(t+.01)-curve(t-.01))/.02
 # Separated lanes on the final straight; no body intersections at the finish.
 lateral=(-1.15 if hero else 1.15)*((1-ease((t-2.79)/1.86))+ease((t-12.09)/2));p+=Vector((-tan.y,tan.x))*lateral
 slide=.42*math.sin(math.pi*max(0,min(1,(t-4.65)/3.72))) if hero and 4.65<t<8.37 else 0
 z=.03;pitch=0;root_pitch=0;roll=-slide*.15;compression=0
 if hero:
  if t<10.95:
   if p.x>24:z,root_pitch=ramp_contact(p.x)
   else:z=.03 if p.x<-45 else .036
  if 10.95<=t<=12.09:
   q=(t-10.95)/1.14;launch_z,launch_pitch=ramp_contact(33);z=.03+(launch_z-.03)*(1-q)+4*.5*q*(1-q);root_pitch=launch_pitch*(1-q)+math.radians(1)*math.sin(math.pi*q)
  if t>12.09:pitch=math.radians(1.5)*math.cos((t-12.09)*16)*math.exp(-(t-12.09)*8)
  compression=.03*math.exp(-((t-12.15)/.09)**2)-.015*math.exp(-((t-12.34)/.12)**2)
  pitch+=math.radians(2.5)*math.exp(-((t-3.8)/.5)**2)
 aa=route.at(d-.5);bb=route.at(d);cc=route.at(d+.5);h1=math.atan2((bb-aa).y,(bb-aa).x);h2=math.atan2((cc-bb).y,(cc-bb).x);curve_angle=(h2-h1+math.pi)%(2*math.pi)-math.pi
 steering=math.atan(2.3*curve_angle)-slide*.8
 return {'position':(p.x,p.y,z),'compression':compression,'yaw':yaw+slide,'pitch':pitch,'root_pitch':root_pitch,'roll':roll,'steer':steering,'distance':d,'speed':speed,'jump':10.95<t<12.09 if hero else False}

def camera_pose(t):
 h=Vector(pose(t)['position']);r=Vector(pose(t,False)['position'])
 if t<.93:
  a=pose(t)['yaw'];f=Vector((math.cos(a),math.sin(a),0));side=Vector((-f.y,f.x,0));target=h+f*.8+side*(-.55)+Vector((0,0,.43));pos=h+f*2.8+side*(-3.6)+Vector((0,0,.72));lens=43
 elif t<2.79:
  q=ease(t/2.79);target=(h+r)/2+Vector((0,0,.55));pos=target+Vector((12,-9,.35)).lerp(Vector((9.5,-12.5,.8)),q);lens=42+q
 elif t<4.65:
  target=(h+r)/2+Vector((8,2,0));pos=target+Vector((-8,-31,37));lens=32
 elif t<8.37:
  q=ease((t-4.65)/3.72);target=h+Vector((0,0,.7));pos=h+Vector((-6,-10,1.1)).lerp(Vector((8,-11,2.2)),q);lens=44+4*q
 elif t<12.555:
  q=ease((t-8.37)/2.58);target=Vector((12,18,1)).lerp(Vector((37,3,1)),q);pos=Vector((25,-28,16)).lerp(Vector((40,-17,3.7)),q);lens=38
  hold=ease((t-11.6)/.955);target=target.lerp(Vector((46,-1,.8)),hold);pos=pos.lerp(Vector((39,-17,3.2)),hold)
 elif t<17.67:
  target=(h+r)/2+Vector((1,0,.7));pos=target+Vector((8,-10,1.4));lens=43
 else:
  target=Vector((112,-22,.7));pos=Vector((112,-48,23));lens=64
 if 12.09<=t<12.69:
  e=math.exp(-(t-12.09)*8);pos+=Vector((.08*math.sin(t*71),.04*math.cos(t*83),.10*math.sin(t*61)))*e
 return pos,target,lens
