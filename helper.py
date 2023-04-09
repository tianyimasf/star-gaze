
import math

def absmag2rad(bv, absmag):
    # Constants
    sun_temp = 5800 # (K)
    sun_absmag = 4.83

    # http://cas.sdss.org/dr4/en/proj/advanced/hr/radius1.asp
    temperature = bvToT(bv)
    delta_absmag = absmag - sun_absmag
    return (sun_temp / temperature)**2 * (2.51**delta_absmag)**(1/2)


def bvToT(bv):
  t = None

  # make sure bv is within its bounds [-0.4, 2] otherwise the math doesnt work
  if bv < -0.4:
    bv = -0.4
  elif bv > 2:
    bv = 2


  # found it online at http://www.wikiwand.com/en/Color_index
  t = 4600 * ((1 / ((0.92 * bv) + 1.7)) + (1 / ((0.92 * bv) + 0.62)))

  # print('t: ' + t);

  return t

  # temperature to CIE xyY Colorspace, assume Y is 1
def tToXyy(t):
  x, y, Y = (1 for i in range(3)); # Y is the luminance, I just assume full luminance for sanity

  # approximation of CIE xyY (http://www.wikiwand.com/en/CIE_1931_color_space) using https://en.wikipedia.org/wiki/Planckian_locus
  if t >= 1667 and t <= 4000:
    x = (-0.2661239 * (math.pow(10, 9) / math.pow(t, 3))) - (-0.2343580 * (math.pow(10, 6) / math.pow(t, 2))) + (0.8776956 * (math.pow(10, 3) / t)) + 0.179910
  elif t >= 4000 and t <= 25000:
    x = (-3.0258469 * (math.pow(10, 9) / math.pow(t, 3))) + (2.1070379 * (math.pow(10, 6) / math.pow(t, 2))) + (0.2226347 * (math.pow(10, 3) / t)) + 0.240390


  if t >= 1667 and t <= 2222:
    y = (-1.1063814 * math.pow(x, 3)) - (1.34811020 * math.pow(x, 2)) + (2.18555832 * x) - 0.20219683
  elif t >= 2222 and t <= 4000:
    y = (-0.9549476 * math.pow(x, 3)) - (1.37418593 * math.pow(x, 2)) + (2.09137015 * x) - 0.16748867
  elif t >= 4000 and t <= 25000:
    y = (3.0817580 * math.pow(x, 3)) - (5.87338670 * math.pow(x, 2)) + (3.75112997 * x) - 0.37001483


  # console.log('xyY: ' + [x, y, Y]);

  return [x, y, Y]


# xyY Color space to XYZ, prepping for conversion to linear RGB
def xyYToXyz(xyY):
  X, Y, Z = (0 for i in range(3))
  x = xyY[0]
  y = xyY[1]

  # X and Z tristimulus values calculated using https://en.wikipedia.org/wiki/CIE_1931_color_space?oldformat=true#CIE_xy_chromaticity_diagram_and_the_CIE_xyY_color_space
  Y = 0 if xyY[2] == 0 else 1
  X = 0 if y == 0 else (x * Y) / y
  Z = 0 if y == 0 else ((1 - x - y) * Y) / y

  # console.log('XYZ: ' + [X, Y, Z]);

  return [X, Y, Z]


# XYZ color space to linear RGB, finally a format I recognize
def xyzToRgb(xyz):
  r, g, b = (0 for i in range(0, 3))
  x = xyz[0]
  y = xyz[1]
  z = xyz[2]

  # using matrix from https://www.cs.rit.edu/~ncs/color/t_convert.html#RGB%20to%20XYZ%20&%20XYZ%20to%20RGB
  r = (3.2406 * x) + (-1.5372 * y) + (-0.4986 * z)

  g = (-0.9689 * x) + (1.8758 * y) + (0.0415 * z)

  b = (0.0557 * x) + (-0.2040 * y) + (1.0570 * z)

  # make sure the values didnt overflow
  r = 1 if r > 1 else r
  g = 1 if g > 1 else g
  b = 1 if b > 1 else b

  # console.log('rgb: ' + [r, g, b]);

  return [r, g, b]


# Im supposed to gamma correct and convert to sRGB but right now it breaks things so TODO: fix this..
def gammaCorrect(rgb):
  a = 0.055
  R, G, B = [0 for i in range(0, 3)]
  r = rgb[0]
  g = rgb[1]
  b = rgb[2]

  # using https://en.wikipedia.org/wiki/SRGB?oldformat=true#The_forward_transformation_.28CIE_xyY_or_CIE_XYZ_to_sRGB.29
  R = 12.92 * r if r <= 0.0031308 else 1.055 * math.pow(r, 1/0.5) - a
  G = 12.92 * g if g <= 0.0031308 else 1.055 * math.pow(g, 1/0.5) - a
  B = 12.92 * b if b <= 0.0031308 else 1.055 * math.pow(b, 1/0.5) - a

  # R = r
  # G = g / 1.05; # idk but i messed up somewhere and this makes it look better
  # B = b

  R = 1 if R > 1 else R
  R = 0 if R < 0 else R
  G = 1 if G > 1 else G
  G = 0 if G < 0 else G
  B = 1 if B > 1 else B
  B = 0 if B < 0 else B

  # turn the 0-1 rgb value to 0-255
  return [round(R * 255), round(G * 255), round(B * 255)]


# now put it all together!
def bvToRgb(bv):
  t, xyY, xyz, rgb, crgb = [0 for i in range(0, 5)]

  t = bvToT(bv)

  xyY = tToXyy(t)

  xyz = xyYToXyz(xyY)

  rgb = xyzToRgb(xyz)

  crgb = gammaCorrect(rgb)

  return crgb


def bv2rgb(bv):
    if bv < -0.40: bv = -0.40
    if bv > 2.00: bv = 2.00

    r = 0.0
    g = 0.0
    b = 0.0

    if  -0.40 <= bv<0.00:
        t=(bv+0.40)/(0.00+0.40)
        r=0.61+(0.11*t)+(0.1*t*t)
    elif 0.00 <= bv<0.40:
        t=(bv-0.00)/(0.40-0.00)
        r=0.83+(0.17*t)
    elif 0.40 <= bv<2.10:
        t=(bv-0.40)/(2.10-0.40)
        r=1.00
    if  -0.40 <= bv<0.00:
        t=(bv+0.40)/(0.00+0.40)
        g=0.70+(0.07*t)+(0.1*t*t)
    elif 0.00 <= bv<0.40:
        t=(bv-0.00)/(0.40-0.00)
        g=0.87+(0.11*t)
    elif 0.40 <= bv<1.60:
        t=(bv-0.40)/(1.60-0.40)
        g=0.98-(0.16*t)
    elif 1.60 <= bv<2.00:
        t=(bv-1.60)/(2.00-1.60)
        g=0.82-(0.5*t*t)
    if  -0.40 <= bv<0.40:
        t=(bv+0.40)/(0.40+0.40)
        b=1.00
    elif 0.40 <= bv<1.50:
        t=(bv-0.40)/(1.50-0.40)
        b=1.00-(0.47*t)+(0.1*t*t)
    elif 1.50 <= bv<1.94:
        t=(bv-1.50)/(1.94-1.50)
        b=0.63-(0.6*t*t)

    return (round(r * 255), round(g * 255), round(b * 255))