"""Rewrite the comaps.symbolset SF Symbol template with the Arah pin mark (values only)."""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import arah_icon_geom as geom
from arah_icon_geom import T, fmt
from arah_icon_arc2cubic import convert

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FILES = [os.path.join(WT, 'iphone/Maps', p, 'Interface/Symbols/comaps.symbolset/comaps.svg')
         for p in ('Images.xcassets', 'CoMapsWidgetExtension/Assets.xcassets')]

X0, Y0, X1, Y1 = geom.pin_bbox()
PIN_H = Y1 - Y0
BASE_H, BASE_TOP = 80.0, -74.0      # Regular: pin 80 pt tall, top at -74 (tip 6 below baseline)
WEIGHTS = {'Ultralight-S': 0.96, 'Regular-S': 1.0, 'Black-S': 1.03}

STYLE = '''.monochrome-0 {-sfsymbols-motion-group:0}
.monochrome-1 {-sfsymbols-motion-group:0}
.monochrome-2 {-sfsymbols-motion-group:0}

.multicolor-0:custom {fill:#0F8B7E;-sfsymbols-motion-group:0}
.multicolor-1:custom {fill:#FFFFFF;-sfsymbols-motion-group:0}
.multicolor-2:custom {fill:#CFE5DF;-sfsymbols-motion-group:0}

.hierarchical-0:primary {-sfsymbols-motion-group:0}
.hierarchical-1:secondary {-sfsymbols-motion-group:0}
.hierarchical-2:secondary {-sfsymbols-motion-group:0}
'''


def glyph(k):
  h = BASE_H * k
  s = h / PIN_H
  w = h  # square advance box so Image("comaps").aspectRatio(1) does not distort the pin
  t = T(s, w / 2 - (X0 + X1) / 2 * s, BASE_TOP * k - Y0 * s)
  pin = geom.pin_path(t) + geom.arrow_full(t, reverse=True)
  paths = [
    ('monochrome-0 multicolor-0:custom hierarchical-0:primary SFSymbolsPreviewWireframe', pin),
    ('monochrome-1 multicolor-1:custom hierarchical-1:secondary SFSymbolsPreviewWireframe', geom.arrow_left(t)),
    ('monochrome-2 multicolor-2:custom hierarchical-2:secondary SFSymbolsPreviewWireframe', geom.arrow_right(t)),
  ]
  return w, paths


def main():
  for f in FILES:
    s = open(f).read()
    s = re.sub(r'(<style>\.defaults \{[^\n]*\}\n\n)(.*?)(\.SFSymbolsPreviewWireframe)',
               lambda m: m.group(1) + STYLE + '\n' + m.group(3), s, count=1, flags=re.S)
    for name, k in WEIGHTS.items():
      m = re.search(rf'<g id="{name}" transform="matrix\(1 0 0 1 ([0-9.]+) 696\)">\n(.*?)\n  </g>', s, re.S)
      gx = float(m.group(1))
      w, paths = glyph(k)
      body = '\n'.join(f'   <path class="{c}" d="{convert(d)}"/>' for c, d in paths)
      s = s[:m.start(2)] + body + s[m.end(2):]
      short = name.split('-')[0]
      s = re.sub(rf'(id="right-margin-{short}-S" style="[^"]*" x1=")[0-9.]+(" x2=")[0-9.]+',
                 lambda mm: f'{mm.group(1)}{fmt(gx + w)}{mm.group(2)}{fmt(gx + w)}', s)
      s = re.sub(rf'(id="left-margin-{short}-S" style="[^"]*" x1=")[0-9.]+(" x2=")[0-9.]+',
                 lambda mm: f'{mm.group(1)}{fmt(gx)}{mm.group(2)}{fmt(gx)}', s)
    open(f, 'w').write(s)
    print('wrote', f)


if __name__ == '__main__':
  main()
