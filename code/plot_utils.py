# -*- coding: utf-8 -*-
"""
Various plotting functions and useful parameters
"""
from itertools import cycle
import string

import cartopy.crs as ccrs
import matplotlib as mpl
# from matplotlib.offsetbox import AnchoredText
import matplotlib.pyplot as plt
import numpy as np
# import arke
# import misc_utils as misc


cc = plt.rcParams['axes.prop_cycle']
icc = cycle(cc)

iletters = iter(string.ascii_lowercase)

# Common plotting settings
CBARKW = dict(orientation='vertical')
AXGR_KW = dict(axes_pad=0.2,
               cbar_location='right',
               cbar_mode='single',
               cbar_pad=0.2,
               cbar_size='3%')

# Common cartopy settings
trans = dict(transform=ccrs.PlateCarree())
COAST = dict(scale='50m', alpha=0.5,
             edgecolor='#333333', facecolor='#AAAAAA')
clon = 15
clat = 75
extent = [-20, 50, 65, 85]
LCC_KW = dict(clon=clon, clat=clat, coast=COAST, extent=extent,
              ticks=None)

mapkey = dict(transform=ccrs.PlateCarree())

clev101 = list(np.linspace(-1, 1, 9))
clev101.remove(0)
clev101 = np.array(clev101)

# Density map plot settings
abs_plt_kw = dict(cmap='Oranges', extend='max', **trans)


def div_cmap(numcolors=11, name='bwr_div_cmap',
             mincol='blue', midcol='white', maxcol='red',
             under=None, midcol_alpha=0, over=None):
    """
    Create a custom diverging colormap with three colors

    Default is blue to transparent white to red with 11 colors.
    Colors can be specified in any way understandable
    by matplotlib.colors.ColorConverter.to_rgb()
    """
    c_max = mpl.colors.colorConverter.to_rgba(maxcol)
    c_min = mpl.colors.colorConverter.to_rgba(mincol)
    c_mid = mpl.colors.colorConverter.to_rgba(midcol, alpha=midcol_alpha)
    cmap = mpl.colors.LinearSegmentedColormap.from_list(name=name,
                                                        colors=[c_min,
                                                                c_mid, c_max],
                                                        N=numcolors)
    if under is not None:
        cmap.set_under(under)
    if over is not None:
        cmap.set_over(over)
    return cmap