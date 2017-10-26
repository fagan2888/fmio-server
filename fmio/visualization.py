# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

__metaclass__ = type

import imageio
from fmio import raster
from fmio import basemap


def pngs2gif(png_paths, gif_path, duration=0.4):
    """png_paths: Series"""
    ims = png_paths.apply(imageio.imread)
    imageio.mimsave(gif_path, ims, duration=duration)


def plot_save_rr(rr, transform, border, rr_crs, savepath):
    ax = border.to_crs(rr_crs).plot(zorder=0)
    raster.plot_rr(rr, transform=transform, ax=ax, zorder=10)
    ax.set_axis_off()
    ax.get_figure().savefig(savepath, bbox_inches='tight')
    return ax


def tif_to_png(inputpath, outputpath, bbox_inches='tight', pad_inches=0, **kwargs):
    border = basemap.border()
    cities = basemap.cities()
    ax = raster.plot_radar_file(inputpath, border=border, cities=cities, **kwargs)
    fig = ax.get_figure()
    fig.savefig(outputpath, bbox_inches=bbox_inches, pad_inches=pad_inches, dpi=140)
    fig.clf()
