"""Convert absolute M/L/A/Z path strings (as produced by geom.py) to M/L/C/Z."""
import math, re
from arah_icon_geom import fmt

TOK = re.compile(r'[MLAZ]|-?[0-9.]+')


def _arc(x1, y1, rx, ry, large, sweep, x2, y2):
  # circular arcs only (rx == ry, no rotation)
  r = rx
  dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
  d2 = dx * dx + dy * dy
  r = max(r, math.sqrt(d2))
  sign = -1 if large == sweep else 1
  co = sign * math.sqrt(max(0, (r * r - d2) / d2)) if d2 else 0
  cxp, cyp = co * dy, -co * dx
  cx, cy = cxp + (x1 + x2) / 2, cyp + (y1 + y2) / 2
  a1 = math.atan2(y1 - cy, x1 - cx)
  a2 = math.atan2(y2 - cy, x2 - cx)
  da = a2 - a1
  if sweep and da < 0:
    da += 2 * math.pi
  elif not sweep and da > 0:
    da -= 2 * math.pi
  n = max(1, int(math.ceil(abs(da) / (math.pi / 2) - 1e-9)))
  step = da / n
  out = []
  for i in range(n):
    t1 = a1 + i * step
    t2 = t1 + step
    k = 4 / 3 * math.tan(step / 4)
    p1 = (cx + r * math.cos(t1), cy + r * math.sin(t1))
    p2 = (cx + r * math.cos(t2), cy + r * math.sin(t2))
    c1 = (p1[0] - k * r * math.sin(t1), p1[1] + k * r * math.cos(t1))
    c2 = (p2[0] + k * r * math.sin(t2), p2[1] - k * r * math.cos(t2))
    out.append((c1, c2, p2))
  return out


def convert(d):
  toks = TOK.findall(d.replace(',', ' '))
  i = 0
  out = ''
  cur = (0, 0)
  start = (0, 0)
  def num():
    nonlocal i
    v = float(toks[i]); i += 1
    return v
  while i < len(toks):
    c = toks[i]; i += 1
    if c in 'ML':
      x, y = num(), num()
      out += f'{c}{fmt(x)} {fmt(y)}'
      cur = (x, y)
      if c == 'M':
        start = cur
    elif c == 'A':
      rx, ry, rot, large, sweep, x, y = (num() for _ in range(7))
      for c1, c2, p in _arc(cur[0], cur[1], rx, ry, int(large), int(sweep), x, y):
        out += f'C{fmt(c1[0])} {fmt(c1[1])} {fmt(c2[0])} {fmt(c2[1])} {fmt(p[0])} {fmt(p[1])}'
      cur = (x, y)
    elif c == 'Z':
      out += 'Z'
      cur = start
  return out
