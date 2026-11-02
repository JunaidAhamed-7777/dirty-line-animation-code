"""DIRTY LINE original animated end-title. Transparent RGBA, no external art.

Typeface: installed Nimbus Sans Narrow Bold (URW Base35); geometry is sheared,
spaced and custom-clipped. Tire tread is deterministic authored vector geometry,
not a stock texture. It is masked to DIRTY only; LINE remains clean.
"""
from pathlib import Path
import argparse,math,random,json
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops
ROOT=Path(__file__).resolve().parent
FONT='/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Bold.otf'

def ease(x):
 x=max(0,min(1,x));return 1-(1-x)**3

def word_mask(word,width,height,tracking=0):
 font=ImageFont.truetype(FONT,220)
 widths=[font.getlength(c) for c in word]
 tmp=Image.new('L',(int(sum(widths)+tracking*(len(word)-1)+80),300))
 d=ImageDraw.Draw(tmp);x=20
 for c,w in zip(word,widths):d.text((x,0),c,font=font,fill=255,stroke_width=2);x+=w+tracking
 tmp=tmp.crop(tmp.getbbox()).resize((width,height),Image.Resampling.LANCZOS)
 pad=math.ceil(height*.22)+4
 out=Image.new('L',(width+pad,height));out.paste(tmp,(0,0))
 return out.transform(out.size,Image.Transform.AFFINE,(1,.22,-.22*height,0,1,0),Image.Resampling.BICUBIC)

class Title:
 def __init__(self,width=1280,height=720,ss=2):
  self.w=width;self.h=height;self.ss=ss;self.k=width/1280*ss;self.size=(width*ss,height*ss)
  self.dirty=Image.new('L',self.size);self.line=Image.new('L',self.size)
  k=self.k
  dm=word_mask('DIRTY',int(560*k),int(145*k));lm=word_mask('LINE',int(420*k),int(66*k),tracking=30)
  self.dirty.paste(dm,(int(339*k),int(234*k)));self.line.paste(lm,(int(421*k),int(395*k)))
  # Intentional clipped racing cuts at two exterior corners, not random erosion.
  dd=ImageDraw.Draw(self.dirty)
  dd.polygon([(339*k,234*k),(366*k,234*k),(339*k,261*k)],fill=0)
  self.tracks=self.make_tracks()
 def make_tracks(self):
  k=self.k;im=Image.new('L',self.size);d=ImageDraw.Draw(im);rng=random.Random(711)
  # Two diagonal contact patches: alternating chevrons with ragged fine streaks.
  for offset in (0,43):
   for x in range(315,970,19):
    y=335+offset-.17*(x-340);w=12+rng.uniform(-2,2)
    # Alternating tread blocks and a thin rib make the marks read as tires.
    d.polygon([(x*k,(y-11)*k),((x+w)*k,(y-14)*k),((x+w+7)*k,(y-1)*k),((x+3)*k,(y+2)*k)],fill=235)
    d.polygon([((x+3)*k,(y+5)*k),((x+w+7)*k,(y+2)*k),((x+w+12)*k,(y+14)*k),((x+7)*k,(y+17)*k)],fill=215)
   for j in range(9):
    yy=335+offset+rng.uniform(-15,17)
    start=rng.uniform(330,430);end=rng.uniform(850,955)
    d.line([(start*k,(yy-.17*(start-340))*k),(end*k,(yy-.17*(end-340))*k)],fill=rng.randrange(65,130),width=max(1,int(k*rng.uniform(.5,1.1))))
  return ImageChops.multiply(im,self.dirty)
 def render(self,t):
  k=self.k;out=Image.new('RGBA',self.size)
  appear=ease((t-20.60)/.19);fade=max(0,min(1,(22.32-t)/.22))
  if appear<=0 or fade<=0:return out.resize((self.w,self.h),Image.Resampling.LANCZOS)
  masks=ImageChops.lighter(self.dirty,self.line)
  # Soft, restrained shadow preserves legibility over wet reflections.
  sh=masks.filter(ImageFilter.GaussianBlur(4*k));shadow=Image.new('RGBA',self.size,(0,0,0,0));shadow.putalpha(sh.point(lambda p:int(p*.65)));out.alpha_composite(shadow,(int(3*k),int(5*k)))
  dirty=Image.new('RGBA',self.size,(240,238,222,0));dirty.putalpha(self.dirty);out.alpha_composite(dirty)
  ln=Image.new('RGBA',self.size,(240,238,222,0));ln.putalpha(self.line);out.alpha_composite(ln)
  # Racing accent: two clipped wedges and a precise terminal line.
  d=ImageDraw.Draw(out)
  for shift in (0,18):d.polygon([((355+shift)*k,406*k),((365+shift)*k,406*k),((348+shift)*k,460*k),((338+shift)*k,460*k)],fill=(240,87,31,255))
  d.polygon([(892*k,405*k),(910*k,405*k),(892*k,460*k),(874*k,460*k)],fill=(240,87,31,255))
  d.line([(430*k,479*k),(863*k,479*k)],fill=(240,87,31,220),width=max(1,int(2*k)))
  # Visible left-to-right abrasion sweep, clipped strictly to DIRTY glyphs.
  prog=ease((t-21.0)/.60)
  reveal=Image.new('L',self.size);rd=ImageDraw.Draw(reveal);edge=(320+650*prog)*k
  rd.rectangle((0,0,int(edge),self.size[1]),fill=255)
  marks=ImageChops.multiply(self.tracks,reveal)
  ink=Image.new('RGBA',self.size,(9,13,16,0));ink.putalpha(marks);out.alpha_composite(ink)
  # Entry travels only 10px; no flash, overshoot or distracting camera movement.
  yoff=int((1-appear)*10*k)
  if yoff:
   shifted=Image.new('RGBA',self.size);shifted.alpha_composite(out,(0,yoff));out=shifted
  alpha=out.getchannel('A').point(lambda p:int(p*appear*fade));out.putalpha(alpha)
  return out.resize((self.w,self.h),Image.Resampling.LANCZOS)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--width',type=int,default=1280);ap.add_argument('--height',type=int,default=720);ap.add_argument('--fps',type=int,default=24);args=ap.parse_args()
 title=Title(args.width,args.height);directory=ROOT/f'frames_{args.width}';directory.mkdir(exist_ok=True)
 first=495;last=536
 for f in range(first,last+1):title.render((f-1)/args.fps).save(directory/f'title_{f:04d}.png')
 # Review sheet uses a neutral dark background only, clearly labelled as a title test.
 times=[20.79,21.08,21.28,21.58,21.95,22.20];sheet=Image.new('RGB',(960,600),(12,18,24));sd=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  frame=title.render(t);bg=Image.new('RGBA',frame.size,(16,25,33,255));bg.alpha_composite(frame);bg=bg.convert('RGB').resize((480,270),Image.Resampling.LANCZOS);x=(i%2)*480;y=(i//2)*200
  # Crop letterboxed title area for a readable 2x3 comparison.
  thumb=bg.crop((0,45,480,225));sheet.paste(thumb,(x,y));sd.text((x+12,y+180),f'{t:.2f}s | transparent title overlay test',fill=(160,174,184))
 sheet.save(ROOT/'title-contact-sheet.jpg',quality=94)
 title.render(21.95).save(ROOT/'title-final-transparent.png')
 json.dump({'fps':args.fps,'width':args.width,'height':args.height,'first_global_frame':first,'last_global_frame':last,'overlay_start_seconds':(first-1)/args.fps,'title_reveal':[20.60,20.79],'skid_sweep':[21.0,21.6],'fade_out':[22.10,22.32],'tread_mask':'DIRTY glyphs only','watermark_safe':'No content in bottom-right watermark area','typeface':FONT,'alpha':'straight RGBA PNG'},open(ROOT/'title_manifest.json','w'),indent=2)
 print(directory)
if __name__=='__main__':main()
