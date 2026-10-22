"""Build all Arah "Pin Kompas" icon/logo assets (docs/arah-brand, iOS, Android, Qt) from arah_icon_geom.py.

Usage: python3 tools/python/arah_icon_build.py [docs preview android ios qt]
Needs rsvg-convert and ImageMagick (magick) on PATH, plus macOS iconutil. Android colour values
live in android/app/src/main/res/values/colors.xml (edited by hand); the SF Symbol is written by
arah_icon_symbol.py."""
import base64, json, os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import arah_icon_geom as geom
from arah_icon_geom import T, fmt

os.environ['PATH'] = '/opt/homebrew/bin:' + os.environ['PATH']
WT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
import tempfile
TMP = tempfile.mkdtemp(prefix='arah_icon_')
os.makedirs(TMP, exist_ok=True)

TEAL = '#0f8b7e'
TEAL_A, TEAL_B = '#14a593', '#0b6f65'
BEIGE = '#f4f1ea'
WHITE = '#ffffff'
SHADE = '#cfe5df'
AMBER = '#f8b42e'
DARK = '#121212'

X0, Y0, X1, Y1 = geom.pin_bbox()
PIN_W, PIN_H = X1 - X0, Y1 - Y0


def fit(box_cx, box_cy, height):
  """Transform placing the pin bbox centred at (box_cx, box_cy) with given height."""
  s = height / PIN_H
  return T(s, box_cx - (X0 + X1) / 2 * s, box_cy - (Y0 + Y1) / 2 * s)


def grad(t, gid='g', a=TEAL_A, b=TEAL_B):
  return (f'<linearGradient id="{gid}" x1="0" y1="{fmt(Y0 * t.s + t.ty)}" x2="0" '
          f'y2="{fmt(Y1 * t.s + t.ty)}" gradientUnits="userSpaceOnUse">'
          f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')


def mark_paths(t, pin_fill='url(#g)', left=WHITE, right=SHADE):
  return (f'<path fill="{pin_fill}" d="{geom.pin_path(t)}"/>\n'
          f'<path fill="{left}" d="{geom.arrow_left(t)}"/>\n'
          f'<path fill="{right}" d="{geom.arrow_right(t)}"/>')


def mono_path(t):
  # Pin outline with the arrow as a hole (reverse winding, works with nonzero fill).
  return geom.pin_path(t) + geom.arrow_full(t, reverse=True)


# Icon placement in a 1024 canvas: pin is 68% of the canvas tall, bbox-centred.
ICON_PIN_H = 0.68 * 1024


def icon_svg(bg=BEIGE, rounded=True, size=1024, pin_a=TEAL_A, pin_b=TEAL_B,
             left=WHITE, right=SHADE, inset=0.0, shadow=False):
  """Full icon. inset: fraction of canvas left transparent around the plate (desktop icons)."""
  plate = size * (1 - 2 * inset)
  off = size * inset
  t = fit(size / 2, size / 2, ICON_PIN_H / 1024 * plate)
  rx = plate * 0.2237 if rounded else 0
  filt = ''
  fattr = ''
  if shadow:
    filt = (f'<filter id="s" x="-10%" y="-10%" width="120%" height="125%">'
            f'<feGaussianBlur in="SourceAlpha" stdDeviation="{fmt(size * 0.012)}"/>'
            f'<feOffset dy="{fmt(size * 0.01)}" result="b"/>'
            f'<feComponentTransfer><feFuncA type="linear" slope="0.3"/></feComponentTransfer>'
            f'<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    fattr = ' filter="url(#s)"'
  bgr = (f'<rect x="{fmt(off)}" y="{fmt(off)}" width="{fmt(plate)}" height="{fmt(plate)}" '
         f'rx="{fmt(rx)}" fill="{bg}"{fattr}/>' if bg else '')
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
          f'viewBox="0 0 {size} {size}"><defs>{grad(t, a=pin_a, b=pin_b)}{filt}</defs>\n{bgr}\n'
          f'{mark_paths(t, left=left, right=right)}\n</svg>\n')


def mark_svg(pad=24):
  w, h = PIN_W + 2 * pad, PIN_H + 2 * pad
  t = T(1, pad - X0, pad - Y0)
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(w)}" height="{fmt(h)}" '
          f'viewBox="0 0 {fmt(w)} {fmt(h)}"><defs>{grad(t)}</defs>\n{mark_paths(t)}\n</svg>\n')


def mark_mono_svg(pad=24, color='#000000'):
  w, h = PIN_W + 2 * pad, PIN_H + 2 * pad
  t = T(1, pad - X0, pad - Y0)
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(w)}" height="{fmt(h)}" '
          f'viewBox="0 0 {fmt(w)} {fmt(h)}">\n<path fill="{color}" d="{mono_path(t)}"/>\n</svg>\n')


def wordmark_svg(color=TEAL):
  # Geometric heavy lowercase "arah": strokes with round caps. x-height 200, stroke 58.
  w = 58
  d = ('M171,200m-71,0a71,71 0 1,0 142,0a71,71 0 1,0 -142,0'  # a bowl (centre 171-71=100)
       ' M171,129V271'
       ' M273,271V129 M273,206A77,77 0 0 1 350,129'               # r
       ' M584,200m-142,0a71,71 0 1,0 142,0a71,71 0 1,0 -142,0'
       ' M584,129V271'
       ' M686,-1V271 M686,271V200A71,71 0 0 1 828,200V271')       # h
  # fix bowl of first a: centre (100,200)
  d = d.replace('M171,200m-71,0', 'M29,200').replace('M584,200m-142,0', 'M442,200')
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="897" height="370" viewBox="-20 -50 897 370">\n'
          f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" '
          f'stroke-linejoin="round"/>\n</svg>\n')


def write(path, text):
  os.makedirs(os.path.dirname(path), exist_ok=True)
  with open(path, 'w') as f:
    f.write(text)


def png(svg_text_or_path, out, w, h=None, extra=()):
  h = h or w
  if not os.path.exists(svg_text_or_path):
    p = os.path.join(TMP, 'tmp.svg')
    write(p, svg_text_or_path)
  else:
    p = svg_text_or_path
  subprocess.run(['rsvg-convert', '-w', str(w), '-h', str(h), p, '-o', out], check=True)
  if extra:
    subprocess.run(['magick', out, *extra, '-define', 'png:exclude-chunks=date,time', out], check=True)


# ----------------------------------------------------------------------------
def build_docs():
  d = os.path.join(WT, 'docs/arah-brand')
  write(os.path.join(d, 'arah-icon.svg'), icon_svg())
  write(os.path.join(d, 'arah-mark.svg'), mark_svg())
  write(os.path.join(d, 'arah-mark-mono.svg'), mark_mono_svg())
  write(os.path.join(d, 'arah-wordmark.svg'), wordmark_svg())


def b64png(path):
  return 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode()


def build_preview():
  d = os.path.join(WT, 'docs/arah-brand')
  icon = os.path.join(d, 'arah-icon.svg')
  items = []
  for s in (1024, 180, 60, 29):
    o = os.path.join(TMP, f'pv_icon_{s}.png')
    png(icon, o, s)
    items.append((o, s))
  mk = os.path.join(TMP, 'pv_mark.png')
  png(os.path.join(d, 'arah-mark.svg'), mk, 186, 220)
  mono = os.path.join(TMP, 'pv_mono.png')
  png(os.path.join(d, 'arah-mark-mono.svg'), mono, 186, 220)
  mono_w = os.path.join(TMP, 'pv_mono_w.png')
  write(os.path.join(TMP, 'mono_w.svg'), mark_mono_svg(color='#ffffff'))
  png(os.path.join(TMP, 'mono_w.svg'), mono_w, 20, 24)
  mono_w_big = os.path.join(TMP, 'pv_mono_w_big.png')
  png(os.path.join(TMP, 'mono_w.svg'), mono_w_big, 48, 57)
  wm = os.path.join(TMP, 'pv_wm.png')
  png(os.path.join(d, 'arah-wordmark.svg'), wm, 360, 148)
  # Android adaptive: 108dp canvas, foreground drawn from the 64-unit drawable scaled 108/64.
  ad = adaptive_svg()
  ad_circle = os.path.join(TMP, 'pv_ad_circle.png')
  ad_squircle = os.path.join(TMP, 'pv_ad_squircle.png')
  png(ad.replace('CLIP', 'circle'), ad_circle, 220)
  png(ad.replace('CLIP', 'squircle'), ad_squircle, 220)
  ios_dark = os.path.join(TMP, 'pv_ios_dark.png')
  png(ios_dark_svg(on_plate=True), ios_dark, 180)
  ios_tint = os.path.join(TMP, 'pv_ios_tint.png')
  png(ios_tinted_svg(on_plate=True), ios_tint, 180)
  dbg = os.path.join(TMP, 'pv_dbg.png')
  png(icon_svg(bg=AMBER), dbg, 180)

  W, H = 1640, 1220
  def img(p, x, y, w, h, pix=False):
    r = ' style="image-rendering:pixelated"' if pix else ''
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{b64png(p)}"{r}/>'
  def lab(x, y, t, size=20, anchor='start', fill='#3a3a3a', weight='normal'):
    return (f'<text x="{x}" y="{y}" font-family="Helvetica Neue, Helvetica, Arial" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{t}</text>')
  parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           lab(40, 60, 'Arah — “Pin Kompas” app icon', 34, weight='bold', fill=TEAL),
           lab(40, 92, 'Teal pin (#14a593 → #0b6f65) holding a folded two-tone arrow (#ffffff / #cfe5df) on beige #f4f1ea', 18)]
  # row 1: icon sizes
  y = 130
  parts.append(img(items[0][0], 40, y, 512, 512))
  parts.append(lab(296, y + 540, '1024 px (shown at 512)', 18, 'middle'))
  x = 600
  for p, s in items[1:]:
    parts.append(img(p, x, y + 512 - s, s, s))
    parts.append(lab(x + s / 2, y + 540, f'{s} px', 18, 'middle'))
    x += s + 50
  # zoomed small ones
  parts.append(img(items[2][0], x, y + 512 - 180, 180, 180, pix=True))
  parts.append(lab(x + 90, y + 540, '60 px ×3', 18, 'middle'))
  x += 230
  parts.append(img(items[3][0], x, y + 512 - 116, 116, 116, pix=True))
  parts.append(lab(x + 58, y + 540, '29 px ×4', 18, 'middle'))
  # iOS variants row above small sizes
  parts.append(img(ios_dark, 600, y, 180, 180))
  parts.append(lab(690, y + 205, 'iOS dark', 18, 'middle'))
  parts.append(img(ios_tint, 830, y, 180, 180))
  parts.append(lab(920, y + 205, 'iOS tinted', 18, 'middle'))
  parts.append(img(dbg, 1060, y, 180, 180))
  parts.append(lab(1150, y + 205, 'Debug build', 18, 'middle'))
  parts.append(img(wm, 1270, y + 20, 330, 136))
  parts.append(lab(1435, y + 205, 'Wordmark', 18, 'middle'))
  # row 2
  y = 720
  parts.append(f'<rect x="40" y="{y}" width="260" height="300" rx="16" fill="#ffffff" stroke="#e2e2e2"/>')
  parts.append(img(mk, 77, y + 40, 186, 220))
  parts.append(lab(170, y + 330, 'Mark on white', 18, 'middle'))
  parts.append(f'<rect x="330" y="{y}" width="260" height="300" rx="16" fill="{DARK}"/>')
  parts.append(img(mk, 367, y + 40, 186, 220))
  parts.append(lab(460, y + 330, 'Mark on #121212', 18, 'middle'))
  parts.append(f'<rect x="620" y="{y}" width="260" height="300" rx="16" fill="#ffffff" stroke="#e2e2e2"/>')
  parts.append(img(mono, 657, y + 40, 186, 220))
  parts.append(lab(750, y + 330, 'Mono mark', 18, 'middle'))
  parts.append(f'<rect x="910" y="{y}" width="180" height="300" rx="16" fill="#3c4043"/>')
  parts.append(img(mono_w_big, 976, y + 60, 48, 57))
  parts.append(img(mono_w, 990, y + 160, 20, 24))
  parts.append(img(mono_w, 963, y + 220, 72, 86, pix=True) if False else '')
  parts.append(lab(1000, y + 330, 'Notification 48/24 px', 18, 'middle'))
  parts.append(img(ad_circle, 1120, y + 40, 220, 220))
  parts.append(lab(1230, y + 330, 'Android circle', 18, 'middle'))
  parts.append(img(ad_squircle, 1380, y + 40, 220, 220))
  parts.append(lab(1490, y + 330, 'Android squircle', 18, 'middle'))
  parts.append('</svg>')
  sheet = os.path.join(TMP, 'preview.svg')
  write(sheet, '\n'.join(parts))
  subprocess.run(['rsvg-convert', sheet, '-o', os.path.join(d, 'preview.png')], check=True)


# ---------------- Android ----------------------------------------------------
LAUNCHER_PIN_H = 36.0  # in the 64-unit foreground viewport (safe zone circle d≈39)


def launcher_t():
  return fit(32, 32, LAUNCHER_PIN_H)


def adaptive_svg():
  """Preview of the adaptive icon: 108dp canvas, mask 'CLIP' replaced by circle/squircle."""
  # foreground 64 viewport is drawn into the 108dp canvas: scale 108/64
  s = 108 / 64
  t0 = launcher_t()
  t = T(t0.s * s, t0.tx * s, t0.ty * s)
  # visible area: 72dp centred mask region of the 108 canvas -> crop 18..90
  return ('<svg xmlns="http://www.w3.org/2000/svg" width="220" height="220" viewBox="18 18 72 72">'
          '<defs><clipPath id="circle"><circle cx="54" cy="54" r="36"/></clipPath>'
          '<clipPath id="squircle"><rect x="18" y="18" width="72" height="72" rx="22"/></clipPath></defs>'
          f'<g clip-path="url(#CLIP)"><rect width="108" height="108" fill="{BEIGE}"/>'
          f'<path fill="{TEAL}" d="{geom.pin_path(t)}"/>'
          f'<path fill="{WHITE}" d="{geom.arrow_left(t)}"/>'
          f'<path fill="{WHITE}" fill-opacity="0.85" d="{geom.arrow_right(t)}"/></g></svg>')


def vd_header(w, h, vw, vh, extra=''):
  return (f'<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
          f'  android:width="{w}"\n  android:height="{h}"\n{extra}'
          f'  android:viewportWidth="{vw}"\n  android:viewportHeight="{vh}">\n')


def vd_path(d, fill, extra=''):
  return f'  <path\n    android:pathData="{d}"\n    android:fillColor="{fill}"{extra}/>\n'


def build_android():
  res = os.path.join(WT, 'android/app/src/main/res')
  t = launcher_t()
  hdr = vd_header('64dp', '64dp', 64, 64)
  # release foreground
  fg = (hdr + vd_path(geom.pin_path(t), '@color/fg_app_icon_release')
        + vd_path(geom.arrow_left(t), '@color/fg_app_icon_white')
        + vd_path(geom.arrow_right(t), '@color/fg_app_icon_white', '\n    android:fillAlpha="0.85"')
        + '</vector>\n')
  write(os.path.join(res, 'drawable/ic_launcher_foreground.xml'), fg)
  stroke = lambda c: (f'\n    android:strokeWidth="@dimen/app_icon_border_width"'
                      f'\n    android:strokeColor="@color/{c}"')
  for kind in ('debug', 'test'):
    fgk = (hdr + vd_path(geom.pin_path(t), f'@color/fg_app_icon_{kind}_fill1', stroke(f'fg_app_icon_{kind}_border'))
           + vd_path(geom.arrow_left(t), f'@color/fg_app_icon_{kind}_fill2')
           + vd_path(geom.arrow_right(t), f'@color/fg_app_icon_{kind}_fill2', '\n    android:fillAlpha="0.85"')
           + '</vector>\n')
    write(os.path.join(res, f'drawable/ic_launcher_foreground_{kind}.xml'), fgk)
  mono = hdr + vd_path(mono_path(t), '#FFFFFF') + '</vector>\n'
  write(os.path.join(res, 'drawable/ic_launcher_foreground_monochrome.xml'), mono)

  # 835 viewport logos: pin 790 tall, centred
  t8 = fit(417.5, 417.5, 790)
  h8 = lambda w: vd_header(w, w, 835, 835)
  write(os.path.join(res, 'drawable/ic_logo.xml'),
        h8('64dp') + vd_path(geom.pin_path(t8), TEAL) + vd_path(geom.arrow_left(t8), WHITE)
        + vd_path(geom.arrow_right(t8), SHADE) + '</vector>\n')
  write(os.path.join(res, 'drawable/ic_logo_small.xml'),
        h8('835dp') + vd_path(mono_path(t8), '#fff') + '</vector>\n')
  write(os.path.join(res, 'drawable/ic_logo_monochrome.xml'),
        h8('64dp') + vd_path(mono_path(t8), '#FFFFFFFF') + '</vector>\n')
  write(os.path.join(res, 'drawable/ic_logo_monochrome_settings.xml'),
        vd_header('22dp', '22dp', 835, 835, '  android:tint="?iconTint"\n')
        + vd_path(mono_path(t8), '#FFFFFFFF') + '</vector>\n')

  # legacy mipmaps: rounded-square plate with soft shadow, transparent corners
  leg = icon_svg(inset=0.0833, shadow=True)
  for dpi, s in (('mdpi', 48), ('hdpi', 72), ('xhdpi', 96), ('xxhdpi', 144), ('xxxhdpi', 192)):
    png(leg, os.path.join(res, f'mipmap-{dpi}/ic_launcher.png'), s)
  # Play Store 512: opaque full-bleed square
  png(icon_svg(rounded=False), os.path.join(WT, 'android/app/src/main/ic_launcher-playstore.png'), 512,
      extra=('-alpha', 'off'))


# ---------------- iOS --------------------------------------------------------
def ios_dark_svg(on_plate=False, pin_a='#19b3a0', pin_b='#0d7f73'):
  t = fit(512, 512, ICON_PIN_H)
  bg = '<rect width="1024" height="1024" rx="229" fill="#1a1a1a"/>' if on_plate else ''
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">'
          f'<defs>{grad(t, a=pin_a, b=pin_b)}</defs>{bg}{mark_paths(t)}</svg>')


def ios_tinted_svg(on_plate=False):
  t = fit(512, 512, ICON_PIN_H)
  bg = '<rect width="1024" height="1024" rx="229" fill="#202020"/>' if on_plate else ''
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">'
          f'<defs>{grad(t, a="#9a9a9a", b="#6a6a6a")}</defs>{bg}'
          f'{mark_paths(t, left="#ffffff", right="#dadada")}</svg>')


def part_svg(body, bbox):
  x0, y0, x1, y1 = bbox
  w, h = x1 - x0, y1 - y0
  return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(w)}" height="{fmt(h)}" '
          f'viewBox="{fmt(x0)} {fmt(y0)} {fmt(w)} {fmt(h)}">{body}</svg>')


def arrow_bbox(t):
  pts = geom._arrow_pts().values()
  xs = [p[0] * t.s + t.tx for p in pts]
  ys = [p[1] * t.s + t.ty for p in pts]
  return min(xs), min(ys), max(xs), max(ys)


def build_ios():
  xa = os.path.join(WT, 'iphone/Maps/Images.xcassets')
  light = icon_svg(rounded=False)
  png(light, os.path.join(xa, 'Icon.appiconset/Light.png'), 1024, extra=('-alpha', 'off'))
  png(ios_dark_svg(), os.path.join(xa, 'Icon.appiconset/Dark.png'), 1024)
  png(ios_tinted_svg(), os.path.join(xa, 'Icon.appiconset/Tinted.png'), 1024,
      extra=('-colorspace', 'Gray', '-define', 'png:color-type=4'))
  png(icon_svg(bg=AMBER, rounded=False), os.path.join(xa, 'Debug Icon.appiconset/Light-Debug.png'), 1024,
      extra=('-alpha', 'off'))
  png(ios_dark_svg(pin_a='#f8c152', pin_b='#e09a12'), os.path.join(xa, 'Debug Icon.appiconset/Dark-Debug.png'), 1024)
  shutil.copy(os.path.join(xa, 'Icon.appiconset/Tinted.png'), os.path.join(xa, 'Debug Icon.appiconset/Tinted-Debug.png'))
  # Logo.svg: full-bleed square vector
  write(os.path.join(xa, 'Interface/Logo.imageset/Logo.svg'), light)

  # Icon Composer documents
  t = fit(512, 512, ICON_PIN_H)
  pin_bb = (X0 * t.s + t.tx, Y0 * t.s + t.ty, X1 * t.s + t.tx, Y1 * t.s + t.ty)
  ab = arrow_bbox(t)
  ab = (ab[0] - 2, ab[1] - 2, ab[2] + 2, ab[3] + 2)
  part1 = part_svg(f'<path fill="{TEAL}" d="{geom.pin_path(t)}"/>', pin_bb)
  part2 = part_svg(f'<path fill="{WHITE}" d="{geom.arrow_left(t)}"/><path fill="{SHADE}" d="{geom.arrow_right(t)}"/>', ab)
  tr1 = [round((pin_bb[0] + pin_bb[2]) / 2 - 512, 4), round((pin_bb[1] + pin_bb[3]) / 2 - 512, 4)]
  tr2 = [round((ab[0] + ab[2]) / 2 - 512, 4), round((ab[1] + ab[3]) / 2 - 512, 4)]
  for name, bg in (('Icon.icon', BEIGE), ('Debug Icon.icon', AMBER)):
    d = os.path.join(WT, 'iphone/Maps', name)
    # Icon Composer draws groups[0] in front: Part 1 (front) = arrow, Part 2 (back) = pin.
    write(os.path.join(d, 'Assets/Part 1.svg'), part2)
    write(os.path.join(d, 'Assets/Part 2.svg'), part1)
    p = os.path.join(d, 'icon.json')
    j = json.load(open(p))
    j['fill']['solid'] = srgb(bg)
    for gi, g in enumerate(j['groups']):
      if gi >= 2:
        g['translucency']['value'] = 0.15  # keep the teal pin saturated under glass
      for layer in g['layers']:
        if gi == 0:
          layer.pop('fill', None)  # front arrow keeps the SVG's two-tone fold colours
        if layer['image-name'] == 'Part 1.svg':
          layer['position']['translation-in-points'] = tr2
          col = WHITE
        else:
          layer['position']['translation-in-points'] = tr1
          col = TEAL_A
        f = layer.get('fill', {})
        if 'solid' in f:
          f['solid'] = srgb(col)
        if 'linear-gradient' in f:
          f['linear-gradient'] = [p3(col, 0), srgb(col)]
    write(p, json.dumps(j, indent=2, ensure_ascii=False).replace('": ', '" : '))


def srgb(hexc, a=1):
  r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
  return f'srgb:{r:.5f},{g:.5f},{b:.5f},{a:.5f}'


def p3(hexc, a):
  r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
  return f'display-p3:{r:.5f},{g:.5f},{b:.5f},{a:.5f}'


# ---------------- Qt ---------------------------------------------------------
def build_qt():
  q = os.path.join(WT, 'qt/res')
  desk = icon_svg(inset=0.04)
  png(desk, os.path.join(q, 'logo.png'), 512)
  write(os.path.join(q, 'logo-scalable.svg'), desk.replace('width="1024" height="1024"', 'width="128" height="128"', 1))
  ddesk = icon_svg(bg=AMBER, inset=0.04)
  png(ddesk, os.path.join(q, 'designer.png'), 512)
  write(os.path.join(q, 'designer-scalable.svg'), ddesk.replace('width="1024" height="1024"', 'width="128" height="128"', 1))
  mac = icon_svg(inset=0.0977, shadow=True)    # 824/1024 macOS grid
  dmac = icon_svg(bg=AMBER, inset=0.0977, shadow=True)
  for name, svg in (('mac', mac), ('designer', dmac)):
    iconset = os.path.join(TMP, f'{name}.iconset')
    shutil.rmtree(iconset, ignore_errors=True)
    os.makedirs(iconset)
    for fn, s in (('icon_16x16.png', 16), ('icon_16x16@2x.png', 32), ('icon_128x128.png', 128),
                  ('icon_128x128@2x.png', 256)):
      png(svg, os.path.join(iconset, fn), s)
    subprocess.run(['iconutil', '-c', 'icns', '-o', os.path.join(q, f'mac/{name}.icns'), iconset], check=True)
  for name, svg in (('windows', desk), ('designer', ddesk)):
    files = []
    for s in (16, 32, 48, 64, 128, 256):
      o = os.path.join(TMP, f'{name}_{s}.png')
      png(svg, o, s)
      files.append(o)
    subprocess.run(['magick', *files, os.path.join(q, f'windows/{name}.ico')], check=True)


if __name__ == '__main__':
  steps = sys.argv[1:] or ['docs', 'preview', 'android', 'ios', 'qt']
  for s in steps:
    globals()['build_' + s]()
    print('built', s)
