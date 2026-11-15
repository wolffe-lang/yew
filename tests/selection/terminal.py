"""Small strict ASCII-fixture VT reader and SGR event decoder, no dependencies.

Only the escape families emitted by these fixtures are accepted. It is not
a general terminal emulator; fixture text must be one-cell characters.
"""
import re


def sgr_events(data):
    """Preserve the received button and all three standard modifier bits."""
    events = []
    for m in re.finditer(rb'\x1b\[<([0-9]+);([0-9]+);([0-9]+)([Mm])', data):
        cb, x, y = map(int, m.group(1, 2, 3))
        if not x or not y:
            raise ValueError('zero SGR coordinate')
        mods = cb & 24
        events.append({'button': cb & ~28, 'mods': mods, 'x': x, 'y': y,
                       'release': m.group(4) == b'm', 'raw': m.group().hex()})
    return events


class VT:
 def __init__(self):
  self.x=self.y=0;self.fg=self.bg=('default',);self.a=set();self.cells={}
 def style(self):return (self.fg,self.bg,tuple(sorted(self.a)))
 def put(self,ch):
  self.cells[self.y,self.x]=(ch,self.style());self.x+=1
 def sgr(self,ns):
  i=0
  while i<len(ns):
   n=ns[i];i+=1
   if n==0:self.fg=self.bg=('default',);self.a=set()
   elif n in (1,2,3,4,5,7,8,9):self.a.add(n)
   elif n==22:self.a-=set((1,2))
   elif n in (23,24,25,27,28,29):self.a.discard(n-20)
   elif 30<=n<=37:self.fg=('index',n-30)
   elif 40<=n<=47:self.bg=('index',n-40)
   elif 90<=n<=97:self.fg=('index',n-90+8)
   elif 100<=n<=107:self.bg=('index',n-100+8)
   elif n==39:self.fg=('default',)
   elif n==49:self.bg=('default',)
   elif n in (38,48):
    typ=ns[i];i+=1
    if typ==5:color=('index',ns[i]);i+=1
    elif typ==2:color=('rgb',*ns[i:i+3]);i+=3
    else:raise ValueError(('color type',typ))
    if n==38:self.fg=color
    else:self.bg=color
 def feed(self,data):
  s=data.decode('utf-8','replace');i=0
  while i<len(s):
   c=s[i];i+=1
   if c=='\x1b':
    if s[i]=='[':
     i+=1;j=i
     while i<len(s) and not '@'<=s[i]<='~':i+=1
     if i==len(s):raise ValueError('truncated CSI')
     args=s[j:i];f=s[i];i+=1
     private=args.startswith('?') or args.startswith('>') or args.startswith('<')
     nums=[int(x) if x else 0 for x in args.split(';')] if not private and re.fullmatch('[0-9;]*',args) else []
     n=nums[0] if nums else 0
     if f in ('H','f') and not private:
      self.y=(n or 1)-1;self.x=((nums[1] if len(nums)>1 else 1) or 1)-1
     elif f=='m':self.sgr(nums or [0])
     elif f=='A' and not private:self.y=max(0,self.y-(n or 1))
     elif f=='B' and not private:self.y+=n or 1
     elif f=='C' and not private:self.x+=n or 1
     elif f=='D' and not private:self.x=max(0,self.x-(n or 1))
     elif f=='G' and not private:self.x=(n or 1)-1
     elif f=='d' and not private:self.y=(n or 1)-1
     elif f=='J' and n in (2,3):self.cells={}
     elif f=='K' and not private:
      bounds=range(80) if n==2 else range(0,self.x+1) if n==1 else range(self.x,80)
      for x in bounds:self.cells[self.y,x]=(' ',self.style())
     elif f in ('h','l','u','c','n','q','t') or private:pass
     elif f=='J':
      for y in range(self.y,24):
       for x in range(self.x if y==self.y else 0,80):self.cells[y,x]=(' ',self.style())
     else:raise ValueError(('unsupported CSI',args,f))
    elif s[i] in (']','P'):
     i+=1
     while i<len(s) and s[i]!='\x07' and s[i:i+2]!='\x1b\\':i+=1
     i+=1 if i<len(s) and s[i]=='\x07' else 2
    elif s[i] in ('(',')'):i+=2
    elif s[i] in ('7','8','='):i+=1
    else:raise ValueError(('unsupported escape',s[i:i+4]))
   elif c=='\r':self.x=0
   elif c=='\n':self.y+=1
   elif c=='\b':self.x=max(0,self.x-1)
   elif ord(c)>=32:self.put(c)
 def rows(self):return [''.join(self.cells.get((y,x),(' ',None))[0] for x in range(80)) for y in range(24)]
