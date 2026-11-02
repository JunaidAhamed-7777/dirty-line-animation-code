"""Recovered DIRTY LINE V2 approved motion from retained tool-call history.
Pure Python: no bpy/scipy/course/camera imports. World distances are metres.
Behavioral reconstruction; recovery source formatting is not byte-identical.
"""
import math,bisect
DURATION=536/24
FINISH_X=380.0
GRAVITY=9.81
JUMP_START=11.04
JUMP_END=12.09
JUMP_DURATION=JUMP_END-JUMP_START
GROUND_Z=.036
LAUNCH_X=115.0
LANDING_X=145.0
LAUNCH_Z=.65
WHEEL_FRONT=1.07554244995*(4.24/4.4)
WHEEL_REAR=-1.22747540474*(4.24/4.4)
WHEEL_RADIUS=.3297740221*(4.24/4.4)
LANDING_PITCH=math.radians(1.2)
LANDING_ROOT_Z=GROUND_Z+WHEEL_FRONT*math.sin(LANDING_PITCH)-WHEEL_RADIUS*(math.cos(LANDING_PITCH)-1)
FLIGHT_VZ=(LANDING_ROOT_Z-LAUNCH_Z+.5*GRAVITY*JUMP_DURATION**2)/JUMP_DURATION

def ease(q):
 q=max(0.,min(1.,q));return q*q*q*(10+q*(-15+6*q))
def main_y(x):return -44+104*math.exp(-(x/155)**2)
FINISH_Y=main_y(FINISH_X)
def _gravel_raw(x):return -44+56*math.exp(-(x/170)**2)
_LINE_SLOPE=-.25
_LINE_Y=main_y(LANDING_X)-2.4

def _blend5(x,x0,x1,y0,y1,m0,m1,c0=0.,c1=0.):
 L=x1-x0;q=(x-x0)/L;a0=y0;a1=L*m0;a2=L*L*c0/2;D=y1-a0-a1-a2;V=L*m1-a1-2*a2;A=L*L*c1-2*a2
 return a0+a1*q+a2*q*q+(10*D-4*V+.5*A)*q**3+(-15*D+7*V-A)*q**4+(6*D-3*V+.5*A)*q**5

def hero_y(x):
 line=_LINE_Y+_LINE_SLOPE*(x-LANDING_X)
 if x>=205:return main_y(x)
 if x>=LANDING_X:return _blend5(x,LANDING_X,205,_LINE_Y,main_y(205),_LINE_SLOPE,derivative(main_y,205),0,second(main_y,205))
 g=_gravel_raw(x);w=ease((x+30)/120);g=g*(1-w)+line*w
 w=ease((x+220)/140)
 return main_y(x)*(1-w)+g*w

def derivative(fn,x,h=.002):return (fn(x+h)-fn(x-h))/(2*h)
def second(fn,x,h=.01):return (fn(x+h)-2*fn(x)+fn(x-h))/(h*h)

class Route:
 def __init__(self,fn,lo=-420.,hi=640.,step=.05):
  self.fn=fn;self.x=[lo+i*step for i in range(round((hi-lo)/step)+1)]
  self.y=[fn(x) for x in self.x];self.dxds=[1/math.sqrt(1+derivative(fn,x)**2) for x in self.x];self.dist=[0.]
  for i in range(1,len(self.x)):self.dist.append(self.dist[-1]+math.hypot(self.x[i]-self.x[i-1],self.y[i]-self.y[i-1]))
 def distance_at_x(self,x):
  i=max(0,min(len(self.x)-2,bisect.bisect_right(self.x,x)-1));q=(x-self.x[i])/(self.x[i+1]-self.x[i]);return self.dist[i]*(1-q)+self.dist[i+1]*q
 def at(self,d):
  i=max(0,min(len(self.dist)-2,bisect.bisect_right(self.dist,d)-1));q=(d-self.dist[i])/(self.dist[i+1]-self.dist[i]);h=self.dist[i+1]-self.dist[i];x=(2*q**3-3*q*q+1)*self.x[i]+(q**3-2*q*q+q)*h*self.dxds[i]+(-2*q**3+3*q*q)*self.x[i+1]+(q**3-q*q)*h*self.dxds[i+1]
  return (x,self.fn(x))

class SmoothDistance:
 def __init__(self,keys,force_speed=None):
  self.keys=keys;self.times=[x[0] for x in keys]
  sec=[(keys[i+1][1]-keys[i][1])/(keys[i+1][0]-keys[i][0]) for i in range(len(keys)-1)]
  speed=[sec[0]]+[2/(1/sec[i-1]+1/sec[i]) for i in range(1,len(sec))]+[sec[-1]]
  for k,v in (force_speed or {}).items():speed[k]=v
  self.segments=[]
  for i in range(len(keys)-1):
   t0,d0=keys[i];t1,d1=keys[i+1];h=t1-t0;a0=d0;a1=h*speed[i];a2=0.;D=d1-a0-a1;V=h*speed[i+1]-a1
   a3=10*D-4*V;a4=-15*D+7*V;a5=6*D-3*V
   self.segments.append((t0,h,(a0,a1,a2,a3,a4,a5)))
 def __call__(self,t):
  i=max(0,min(len(self.segments)-1,bisect.bisect_right(self.times,t)-1));t0,h,a=self.segments[i];q=(t-t0)/h
  return sum(c*q**k for k,c in enumerate(a))
 def velocity(self,t):
  i=max(0,min(len(self.segments)-1,bisect.bisect_right(self.times,t)-1));t0,h,a=self.segments[i];q=(t-t0)/h
  return sum(k*a[k]*q**(k-1) for k in range(1,6))/h

main=Route(main_y);short=Route(hero_y)
HERO_X_KEYS=[(0,-260),(2.79,-145),(4.65,-75),(8.37,30),(JUMP_START,LAUNCH_X),(JUMP_END,LANDING_X),(17.67,315),(19.53,380),(DURATION,485)]
RIVAL_X_KEYS=[(0,-252),(2.79,-145),(4.65,-80),(8.37,35),(10.95,117),(12.09,152),(17.67,315.8),(19.53,379.4),(DURATION,483.4)]
_hkeys=[(t,short.distance_at_x(x)) for t,x in HERO_X_KEYS]
_flight_speed=(_hkeys[5][1]-_hkeys[4][1])/JUMP_DURATION
H=SmoothDistance(_hkeys,{4:_flight_speed,5:_flight_speed})
R=SmoothDistance([(t,main.distance_at_x(x)) for t,x in RIVAL_X_KEYS])
ROAD=[(x/2,main_y(x/2)) for x in range(-840,1161)]
GRAVEL=[(x/2,hero_y(x/2)) for x in range(-450,291)]

def _horizontal(t,hero):
 route,curve=(short,H) if hero else (main,R);x,y=route.at(curve(t));dy=derivative(route.fn,x);norm=math.sqrt(1+dy*dy)
 lane=(-1.15 if hero else 1.15)*((1-ease((t-2.0)/2.4))+ease((t-12.09)/1.5))
 return (x-dy/norm*lane,y+lane/norm)
def _velocity(t,hero,h=.002):
 a=_horizontal(t-h,hero);b=_horizontal(t+h,hero);return ((b[0]-a[0])/(2*h),(b[1]-a[1])/(2*h))
LANDING_RECOVERY_START=JUMP_END+.05
LANDING_RECOVERY_DURATION=.70

def landing_slip(t):
 q=(t-LANDING_RECOVERY_START)/LANDING_RECOVERY_DURATION
 if not 0<q<1:return 0.
 return math.radians(3.0)*math.sin(2*math.pi*q)*math.sin(math.pi*q)**2*(1-.35*q)

def _slip(t):
 q=(t-4.25)/4.55
 rally=.23*math.sin(math.pi*q)**4 if 0<q<1 else 0.
 return rally+landing_slip(t)

def _quintic_height(q,h0,h1,m0,m1,L):
 a0=h0;a1=L*m0;D=h1-a0-a1;V=L*m1-a1
 return a0+a1*q+(10*D-4*V)*q**3+(-15*D+7*V)*q**4+(6*D-3*V)*q**5
LAUNCH_VX=(LANDING_X-LAUNCH_X)/JUMP_DURATION
RAMP_SLOPE=FLIGHT_VZ/LAUNCH_VX
RAMP_START=LAUNCH_X-8.

def _ideal_ramp_height(x):
 if x<RAMP_START:return GROUND_Z
 if x<=LAUNCH_X:return _quintic_height((x-RAMP_START)/8,GROUND_Z,LAUNCH_Z,0,RAMP_SLOPE,8)
 if x<LAUNCH_X+8:
  q=(x-LAUNCH_X)/8;return LAUNCH_Z*(1-ease(q))+GROUND_Z*ease(q)
 return GROUND_Z

def ramp_slope(x):
 if x<RAMP_START:return 0.
 if x<=LAUNCH_X:
  q=(x-RAMP_START)/8;a1=0.;D=LAUNCH_Z-GROUND_Z;V=8*RAMP_SLOPE
  return (3*(10*D-4*V)*q*q+4*(-15*D+7*V)*q**3+5*(6*D-3*V)*q**4)/8
 return derivative(_ideal_ramp_height,x)

def ramp_lip_x():
 yaw=math.atan(_LINE_SLOPE);theta=-math.atan(RAMP_SLOPE*math.cos(yaw))
 return LAUNCH_X+math.cos(yaw)*(WHEEL_REAR*math.cos(theta)+WHEEL_RADIUS*math.sin(theta))

def ramp_height(x):
 lip=ramp_lip_x()
 if x<=lip:return _ideal_ramp_height(x)
 if x>=lip+4:return GROUND_Z
 return max(GROUND_Z,_blend5(x,lip,lip+4,_ideal_ramp_height(lip),GROUND_Z,ramp_slope(lip),0.,-.10,0.))

def profile_height(x,y=0,gravel=False):return ramp_height(x) if gravel else .03

def ramp_contact(x,yaw=0.,theta=None,flat=False):
 if theta is None:theta=-math.atan(ramp_slope(x)*math.cos(yaw))
 base=GROUND_Z if flat else _ideal_ramp_height(x)
 candidates=[base]
 for f in [WHEEL_FRONT,WHEEL_REAR]:
  wx=x+math.cos(yaw)*(f*math.cos(theta)+WHEEL_RADIUS*math.sin(theta))
  ground=GROUND_Z if flat else ramp_height(wx)
  candidates.append(ground+f*math.sin(theta)-WHEEL_RADIUS*(math.cos(theta)-1))
 z=candidates[0]
 for a in candidates[1:]:z=.5*(z+a+math.sqrt((z-a)**2+1e-12))
 return z,theta

def _calibrate_launch():
 global RAMP_SLOPE,FLIGHT_VZ,LAUNCH_ROOT_Z
 yaw=math.atan(_LINE_SLOPE);lo=.10;hi=.25
 for _ in range(48):
  RAMP_SLOPE=(lo+hi)/2
  z=ramp_contact(LAUNCH_X,yaw)[0]
  vz=(z-ramp_contact(LAUNCH_X-.0001,yaw)[0])/.0001*LAUNCH_VX
  need=(LANDING_ROOT_Z-z+.5*GRAVITY*JUMP_DURATION**2)/JUMP_DURATION
  if vz<need:lo=RAMP_SLOPE
  else:hi=RAMP_SLOPE
 LAUNCH_ROOT_Z=ramp_contact(LAUNCH_X,yaw)[0]
 FLIGHT_VZ=(LANDING_ROOT_Z-LAUNCH_ROOT_Z+.5*GRAVITY*JUMP_DURATION**2)/JUMP_DURATION
_calibrate_launch()

def pose(t,hero=True):
 x,y=_horizontal(t,hero);vx,vy=_velocity(t,hero);speed=math.hypot(vx,vy);path_yaw=math.atan2(vy,vx);slip=_slip(t) if hero else 0.;yaw=path_yaw+slip
 dt=.006;va=_velocity(t-dt,hero);vb=_velocity(t+dt,hero);ax=(vb[0]-va[0])/(2*dt);ay=(vb[1]-va[1])/(2*dt);k=(vx*ay-vy*ax)/max(speed**3,1e-9)
 steer=math.atan((2.224 if hero else 2.413)*k)-.82*slip
 z=GROUND_Z;root_pitch=0.;pitch=0.;compression=0.;roll=-.06*slip-(.18*landing_slip(t) if hero else 0.)
 jump=bool(hero and JUMP_START<t<JUMP_END)
 if hero:
  if t<JUMP_START:
   z,root_pitch=ramp_contact(x,path_yaw)
  elif t<=JUMP_END:
   tau=t-JUMP_START;z=LAUNCH_ROOT_Z+FLIGHT_VZ*tau-.5*GRAVITY*tau*tau
   q=tau/JUMP_DURATION;root_pitch=(-math.atan(RAMP_SLOPE*math.cos(path_yaw)))*(1-ease(q))+LANDING_PITCH*ease(q)
  else:
   tau=t-JUMP_END
   root_pitch=LANDING_PITCH*math.exp(-tau*11)*(1+11*tau)
   z,_=ramp_contact(x,path_yaw,root_pitch,flat=True)
  pitch=math.radians(1.6)*math.exp(-((t-3.4)/.55)**2)
  if t>JUMP_END:
   tau=t-JUMP_END
   compression=.055*(1-math.exp(-tau*45))*math.exp(-tau*8)*math.cos(tau*18)
   pitch+=math.radians(1.1)*math.sin(tau*18)*math.exp(-tau*8)
  roll+=-.015*math.sin(t*17)*math.sin(math.pi*max(0,min(1,(t-4.2)/5)))**2 if 4.2<t<9.2 else 0
 return {'position':(x,y,z),'compression':compression,'yaw':yaw,'path_yaw':path_yaw,'pitch':pitch,'root_pitch':root_pitch,'roll':roll,'steer':steer,'distance':(H if hero else R)(t),'speed':speed,'jump':jump,'velocity':(vx,vy),'curvature':k,'slip':slip}

def route_bounds():return {'road_x':[-420,580],'road_y':[-44,60],'gravel_x':[-225,145],'finish':(FINISH_X,FINISH_Y),'launch':(LAUNCH_X,hero_y(LAUNCH_X),LAUNCH_Z),'landing':(LANDING_X,hero_y(LANDING_X),GROUND_Z)}
