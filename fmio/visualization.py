# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

import imageio
from fmio import raster


def pngs2gif(png_paths, gif_path):
    """png_paths: Series"""
    ims = png_paths.apply(imageio.imread)
    imageio.mimsave(gif_path, ims, duration=0.2)


def plot_save_rr(rr, transform, border, rr_crs, savepath):
    ax = border.to_crs(rr_crs).plot(zorder=0)
    raster.plot_rr(rr, transform=transform, ax=ax, zorder=10)
    ax.set_axis_off()
    ax.get_figure().savefig(savepath, bbox_inches='tight')
    return ax

