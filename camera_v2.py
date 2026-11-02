"""Recovered latest V2 camera source from verified retained implementation."""
import math
from mathutils import Vector
CUTS=[.85,2.20,4.20,8.60,10.55,12.50,15.80,19.00]
def smooth(x):
 x=max(0,min(1,x));return x*x*x*(10+x*(-15+6*x))
def camera_pose(t):
 from timeline import pose,FINISH_X,FINISH_Y
 ph=pose(t);pr=pose(t,False);h=Vector(ph['position']);r=Vector(pr['position']);yaw=ph.get('path_yaw',ph['yaw']);f=Vector((math.cos(yaw),math.sin(yaw),0));n=Vector((-f.y,f.x,0))
 if t<.85:
  start=Vector(pose(0)['position']);pos=start+Vector((18,-6,.38));target=(h+r)/2+Vector((0,0,.6));lens=28
 elif t<2.20:
  q=smooth((t-.85)/1.35);target=(h+r)/2+f*1.4+Vector((0,0,.6));pos=target+f*(8-2*q)-n*(6+q)+Vector((0,0,.4+.3*q));lens=30
 elif t<4.2:
  q=smooth((t-2.75)/1.45);anchor=Vector((-177,-13,.4));follow=(h+r)/2-Vector((12,0,0));target=anchor.lerp(follow,q);pos=target+Vector((-15,-63,72));lens=32+3*q
 elif t<8.6:
  q=smooth((t-4.2)/4.4);target=h-f*1.5+Vector((0,0,.65));pos=h+f*(-7+12*q)-n*(8+.6*math.sin(q*math.pi))+Vector((0,0,.85+.45*q));lens=30+3*q
 elif t<10.55:
  q=smooth((t-8.6)/1.95);target=h+f*.2+Vector((0,0,.7));pos=h+f*(2-q)-n*(14-2*q)+Vector((0,0,3.2-1.2*q));lens=30
 elif t<12.5:
  q=smooth((t-10.55)/1.95);base=Vector(pose(max(0,t-.08))['position']);base.z=0;pos=base+f*(3-5*q)-n*7+Vector((0,0,1.05));target=h+f*.6+Vector((0,0,.55));lens=32
 elif t<15.8:
  q=smooth((t-12.5)/3.3);ry=pr.get('path_yaw',pr['yaw']);rf=Vector((math.cos(ry),math.sin(ry),0));rn=Vector((-rf.y,rf.x,0));target=(h+r)/2+rf*.2+Vector((0,0,.55));pos=r+rf*(5.1-.7*q)-rn*(3.8+.8*q)+Vector((0,0,.45+.2*q));lens=25+3*q
 elif t<19:
  q=smooth((t-15.8)/3.2);target=(h+r)/2+f*.6+Vector((0,0,.65));pos=(h+r)/2-f*(6-2*q)-n*10+Vector((0,0,5.5));lens=34
 else:
  q=smooth((t-19)/.65);target=Vector((FINISH_X,FINISH_Y,.65));pos=Vector((FINISH_X+5-2*q,FINISH_Y-14+2*q,7.2-.6*q));lens=32
 gravel=smooth((t-3.8)/.5)*(1-smooth((t-10.55)/.4));amp=.008+.014*gravel;signal=math.sin(t*2*math.pi*4.3)+.45*math.sin(t*2*math.pi*7.7+1.2)
 pos+=Vector((amp*.45*math.sin(t*31),amp*.4*math.sin(t*47),amp*signal));target+=Vector((.003*math.sin(t*23),0,.005*signal))
 if 12.09<t<12.69:
  age=t-12.09;impact=.085*math.exp(-age*9);pos.z+=impact*math.sin(age*65);pos.x+=impact*.3*math.sin(age*51)
 return pos,target,lens
