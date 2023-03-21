
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