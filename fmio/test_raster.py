# TODO: draft
import rasterio


def test_value_at_coords():
    from fmio.raster import value_at_coords
    filepath = 'data/20171213_2230.tif'
    x = 364000
    y = 6.91e6
    with rasterio.open(filepath) as data:
        assert value_at_coords(data, x, y) == 126
