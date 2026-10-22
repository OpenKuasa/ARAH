"""Arah "Pin Kompas" geometry. All shapes in a 1024x1024 design canvas.

Exposes functions that return SVG/Android-compatible path strings (M, L, A, Z only),
optionally transformed by scale s and offset (tx, ty): p' = p*s + t.
"""
import math

# ---- Tunables ---------------------------------------------------------------
CX = 512.0          # pin axis
HEAD_CY = 440.0     # centre of pin head
HEAD_R = 280.0      # radius of pin head
TIP_Y = 830.0       # bottom tip of pin
TIP_R = 40.0        # roundness of the tip

ARROW_ANGLE = 10.0  # degrees clockwise (0 = straight up)
ARROW_TIP = (0.0, -172.0)     # relative to head centre, before rotation
ARROW_WING = (150.0, 118.0)   # right wing (left is mirrored)
ARROW_NOTCH = (0.0, 40.0)
ARROW_ROUND_TIP = 18.0
ARROW_ROUND_WING = 22.0
ARROW_ROUND_NOTCH = 12.0
ARROW_SHIFT_X = 0.0           # optical offsets after bbox-centring in the head
ARROW_SHIFT_Y = 0.0


def fmt(v):
  s = f'{v:.2f}'.rstrip('0').rstrip('.')
  return '0' if s in ('-0', '') else s


class T:
  def __init__(self, s=1.0, tx=0.0, ty=0.0):
    self.s, self.tx, self.ty = s, tx, ty

  def p(self, x, y):
    return f'{fmt(x * self.s + self.tx)},{fmt(y * self.s + self.ty)}'

  def r(self, r):
    return fmt(r * self.s)


def pin_path(t=T(), reverse=False):
  """Teardrop pin: circle head + tangent lines to a rounded tip."""
  d = TIP_Y - HEAD_CY
  # tip rounding: circle of radius TIP_R tangent to both tangent lines, centred on axis
  # angle between axis and tangent line
  # tangent lines from a virtual sharp tip at (CX, TIP_Y_sharp) to head circle.
  # Solve for sharp-tip so that the rounded tip's lowest point is TIP_Y.
  # rounded circle centre at distance TIP_R/sin(a) above sharp tip; lowest point = centre + TIP_R
  # iterate
  sharp = TIP_Y
  for _ in range(50):
    dd = sharp - HEAD_CY
    a = math.asin(HEAD_R / dd)
    c_y = sharp - TIP_R / math.sin(a)
    low = c_y + TIP_R
    sharp += TIP_Y - low
  dd = sharp - HEAD_CY
  a = math.asin(HEAD_R / dd)
  c_y = sharp - TIP_R / math.sin(a)
  # tangent point on head circle (right side): direction from head centre at angle a from horizontal
  # The tangent line makes angle a with the axis. Tangent point angle from centre: (90deg - a) below horizontal? compute:
  # point on circle where radius is perpendicular to line from sharp tip.
  phi = math.pi / 2 - a  # angle from +x axis measured downward (y grows down)
  hx = CX + HEAD_R * math.cos(math.pi / 2 - phi + 0)  # placeholder, recomputed below
  # Correct: tangent point P satisfies (P-C).(P-S)=0. Angle of P from C, measured from the downward axis, = 90deg - a... use theta from +y axis
  theta = math.pi / 2 - a  # angle between downward axis and CP
  # but CP·(P-S)=0 -> angle between CS(downward) and CP is acos(R/d)
  theta = math.acos(HEAD_R / dd)
  hxr = CX + HEAD_R * math.sin(theta)
  hy = HEAD_CY + HEAD_R * math.cos(theta)
  hxl = CX - HEAD_R * math.sin(theta)
  # tip circle tangent points: on tip circle where radius perpendicular to line
  txr = CX + TIP_R * math.sin(theta)
  ty = c_y + TIP_R * math.cos(theta)
  txl = CX - TIP_R * math.sin(theta)
  R, r = t.r(HEAD_R), t.r(TIP_R)
  if not reverse:
    # clockwise in screen coords (sweep=1): start top-left tangent... go: right head tangent -> tip -> left tangent -> big arc over the top
    return (f'M{t.p(hxr, hy)}L{t.p(txr, ty)}A{r},{r} 0 0,1 {t.p(txl, ty)}'
            f'L{t.p(hxl, hy)}A{R},{R} 0 1,1 {t.p(hxr, hy)}Z')
  return (f'M{t.p(hxr, hy)}A{R},{R} 0 1,0 {t.p(hxl, hy)}L{t.p(txl, ty)}'
          f'A{r},{r} 0 0,0 {t.p(txr, ty)}Z')


def _rot(pt):
  a = math.radians(ARROW_ANGLE)
  x, y = pt
  return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))


def _arrow_pts():
  tip, wr, notch = ARROW_TIP, ARROW_WING, ARROW_NOTCH
  wl = (-wr[0], wr[1])
  pts = {k: _rot(v) for k, v in {'tip': tip, 'wr': wr, 'notch': notch, 'wl': wl}.items()}
  xs = [p[0] for k, p in pts.items() if k != 'notch']
  ys = [p[1] for k, p in pts.items() if k != 'notch']
  bx, by = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
  return {k: (CX + v[0] - bx + ARROW_SHIFT_X, HEAD_CY + v[1] - by + ARROW_SHIFT_Y)
          for k, v in pts.items()}


def _fillet(prev, cur, nxt, r):
  """Return (p_in, p_out, radius, sweep) for rounding corner cur."""
  def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    l = math.hypot(dx, dy)
    return dx / l, dy / l
  u1 = unit(cur, prev)
  u2 = unit(cur, nxt)
  cosang = u1[0] * u2[0] + u1[1] * u2[1]
  ang = math.acos(max(-1, min(1, cosang)))
  dist = r / math.tan(ang / 2)
  p_in = (cur[0] + u1[0] * dist, cur[1] + u1[1] * dist)
  p_out = (cur[0] + u2[0] * dist, cur[1] + u2[1] * dist)
  # turn direction: cross of (cur-prev) x (nxt-cur)
  v1 = (cur[0] - prev[0], cur[1] - prev[1])
  v2 = (nxt[0] - cur[0], nxt[1] - cur[1])
  cross = v1[0] * v2[1] - v1[1] * v2[0]
  sweep = 1 if cross > 0 else 0
  return p_in, p_out, r, sweep


def _poly(points, radii, t, sharp=()):
  """Closed polygon with filleted corners. sharp: indices kept sharp."""
  n = len(points)
  out = []
  for i in range(n):
    prev, cur, nxt = points[i - 1], points[i], points[(i + 1) % n]
    if i in sharp or radii[i] <= 0:
      out.append(('L', cur))
    else:
      p_in, p_out, r, sweep = _fillet(prev, cur, nxt, radii[i])
      out.append(('L', p_in))
      out.append(('A', p_out, r, sweep))
  s = ''
  first = True
  for item in out:
    if item[0] == 'L':
      s += ('M' if first else 'L') + t.p(*item[1])
    else:
      s += f'A{t.r(item[2])},{t.r(item[2])} 0 0,{item[3]} {t.p(*item[1])}'
    first = False
  return s + 'Z'


def arrow_full(t=T(), reverse=False):
  p = _arrow_pts()
  pts = [p['tip'], p['wr'], p['notch'], p['wl']]
  radii = [ARROW_ROUND_TIP, ARROW_ROUND_WING, ARROW_ROUND_NOTCH, ARROW_ROUND_WING]
  if reverse:
    pts = pts[::-1]
    radii = radii[::-1]
  return _poly(pts, radii, t)


def arrow_left(t=T()):
  """Left (lit, pure white) half: tip -> notch along spine -> left wing."""
  p = _arrow_pts()
  pts = [p['tip'], p['notch'], p['wl']]
  return _half(pts, t, side='l')


def arrow_right(t=T()):
  p = _arrow_pts()
  pts = [p['tip'], p['wr'], p['notch']]
  return _half(pts, t, side='r')


def _half(pts, t, side):
  # Round only the outer corners; the spine stays straight so halves meet cleanly.
  # To round the tip/notch on the outer side only we use the full arrow's fillet points.
  p = _arrow_pts()
  full = [p['tip'], p['wr'], p['notch'], p['wl']]
  radii = [ARROW_ROUND_TIP, ARROW_ROUND_WING, ARROW_ROUND_NOTCH, ARROW_ROUND_WING]
  f = [_fillet(full[i - 1], full[i], full[(i + 1) % 4], radii[i]) for i in range(4)]
  tip_in, tip_out, rt, st = f[0]     # tip_in on left edge (from wl), tip_out on right edge
  wr_in, wr_out, rw, sw = f[1]
  n_in, n_out, rn, sn = f[2]         # n_in on right edge, n_out on left edge
  wl_in, wl_out, rw2, sw2 = f[3]
  # split the tip arc and notch arc at their midpoints on the spine.
  def arcmid(a, b, cur, r):
    # point on fillet arc closest to corner along the bisector
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = mx - cur[0], my - cur[1]
    l = math.hypot(dx, dy)
    # centre of fillet lies along bisector at distance r/sin(half angle)
    ux, uy = dx / l, dy / l
    u1 = (a[0] - cur[0], a[1] - cur[1])
    la = math.hypot(*u1)
    half = math.atan2(r, la)  # angle between edge and line to centre
    dc = math.hypot(la, r)
    c = (cur[0] + ux * dc, cur[1] + uy * dc)
    return (c[0] - ux * r, c[1] - uy * r)
  tip_m = arcmid(tip_in, tip_out, full[0], rt)
  n_m = arcmid(n_in, n_out, full[2], rn)
  R = lambda r: t.r(r)
  if side == 'r':
    return (f'M{t.p(*tip_m)}A{R(rt)},{R(rt)} 0 0,{st} {t.p(*tip_out)}L{t.p(*wr_in)}'
            f'A{R(rw)},{R(rw)} 0 0,{sw} {t.p(*wr_out)}L{t.p(*n_in)}'
            f'A{R(rn)},{R(rn)} 0 0,{sn} {t.p(*n_m)}Z')
  return (f'M{t.p(*n_m)}A{R(rn)},{R(rn)} 0 0,{sn} {t.p(*n_out)}L{t.p(*wl_in)}'
          f'A{R(rw2)},{R(rw2)} 0 0,{sw2} {t.p(*wl_out)}L{t.p(*tip_in)}'
          f'A{R(rt)},{R(rt)} 0 0,{st} {t.p(*tip_m)}Z')


def pin_bbox():
  return (CX - HEAD_R, HEAD_CY - HEAD_R, CX + HEAD_R, TIP_Y)
