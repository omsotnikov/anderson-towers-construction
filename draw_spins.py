"""
Draws spins on 2d lattice.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mplcolors
from matplotlib import cm
from matplotlib.collections import PatchCollection
from h5py import File
from argparse import ArgumentParser
import numpy as np


def find_corners(x, y):

    x_min = x_max = x[0]
    y_min = y_max = y[0]

    for n, m in zip(x, y):
        if x_min > n:
            x_min = n
        if x_max < n:
            x_max = n
        if y_min > m:
            y_min = m
        if y_max < m:
            y_max = m

    return x_min, x_max, y_min, y_max


def ask(msg):
    answ = input(msg)
    return True if 'y' in answ else False


def get_parameters():

    p = ArgumentParser()
    p.add_argument('file', nargs='+', help='File(s) with spins and coordinates datasets.')
    p.add_argument('--root', default='', help='Root of hdf5 data.')
    p.add_argument('--prefix', default='', help='Prefix for all output files.')

    p.add_argument('--x-limits', type=float, nargs=2, default=None, help='Limit image to specified X range.')
    p.add_argument('--y-limits', type=float, nargs=2, default=None, help='Limit image to specified Y range.')
    p.add_argument('--z-limits', nargs=2, type=float, default=None, help='Limits for z-axis colormap.')

    p.add_argument('--cmap', default='rainbow', help='olormap for Z component of spins.')
    
    p.add_argument('--radius', default=0.495, type=float, help='Radius of spins.')
    p.add_argument('--edge', type=float, default=None, help='Edge width.')
    p.add_argument('--edge-color', default='black', help='Edge color.')

    p.add_argument('--scale-spins', type=float, default=1, help='Scale width of spin arrows.')
    p.add_argument('--quivers-width', type=float, default=1, help='Width of spin arrows.')

    p.add_argument('--zoom', type=float, default=0.95, help='Zoom the whole image.')
    p.add_argument('--font-size', type=float, default=18, help='Fonts size.')
    p.add_argument('--colorbar', action='store_true', help='Draw colorbar.')
    p.add_argument('--scale-colorbar-font', type=float, default=1, help='Scaling factor for colorbar axis font.')

    p.add_argument('--save', default=None, choices=('pdf','png','svg'), help='Save figure in given format.')
    p.add_argument('--dpi', type=int, default=None, help='DPI of the raster image.')
    p.add_argument('--transparent', action='store_true', help='Make figure with transparent background.')
    
    p = p.parse_args()

    if not p.root.endswith('/'):
        p.root += '/'
    
    return p
    
def main():

    p = get_parameters()

    if len(p.file) > 4 and not p.save:
        if not ask('Do you want to display {0} (!) files one by one? [y/N] : '.format(len(p.file))):
            exit(1)

    for fn in p.file:
        custom_h = []
        h = None
        j = None
        x = None
        s = None


        with File(fn, 'r') as f:
            
            coords = f[p.root+'coordinates'][:]
            spins = f[p.root+'spins'][:]
            
            if p.x_limits or p.y_limits:
                
                filtered_s = []
                filtered_coords = []
                for i, c in enumerate(coords):
                    if not (p.x_limits is None):
                        if c[0] < p.x_limits[0] or c[0] > p.x_limits[1]:
                            continue
                    if not (p.y_limits is None):
                        if c[1] < p.y_limits[0] or c[1] > p.y_limits[1]:
                            continue
                    filtered_s.append(spins[i,:])
                    filtered_coords.append(coords[i,:])
                coords = np.array(filtered_coords)
                spins = np.array(filtered_s)

            x = [None, None]
            x[0] = coords[:, 0]
            x[1] = coords[:, 1]
            s = [None, None, None]

            s[0] = spins[:, 0]
            s[1] = spins[:, 1]
            s[2] = spins[:, 2]

        fig, ax = plt.subplots()
            
        circles = []
        sz_cut = []
        qposx = []
        qposy = []
        qsx = []
        qsy = []

        for i,xy in enumerate(zip(x[0], x[1])):
            circles.append(mpatches.Circle(xy, p.radius))

        collection = PatchCollection(circles, cmap=cm.get_cmap(p.cmap))

        collection.set_array(np.array(s[2]))

        if p.z_limits:
            norm = mplcolors.Normalize(vmin=p.z_limits[0], vmax=p.z_limits[1])
        else:
            norm = mplcolors.Normalize(vmin=-1.0, vmax=1.0)
        collection.set_norm(norm)

        if p.edge:
            collection.set_linestyle('-')
            collection.set_edgecolor(p.edge_color)
            collection.set_linewidth(p.edge)
            
        ax.add_collection(collection)

        ax.quiver(x[0], x[1], s[0], s[1], pivot='mid', units='x', scale=0.5/p.scale_spins/p.radius, linewidths=(1,),
                  width=0.035*p.quivers_width)  # scale 0.5 for alps

        x_min, x_max, y_min, y_max = find_corners(x[0], x[1])
        ax.set_xlim(x_min-p.radius/p.zoom, x_max+p.radius/p.zoom)  # add some space to draw edges properly
        ax.set_ylim(y_min-p.radius/p.zoom, y_max+p.radius/p.zoom)

        ax.set_aspect('equal')
        ax.set_axis_off()

        if p.colorbar:
            cbar = fig.colorbar(collection)
            cbar.ax.tick_params(labelsize=p.font_size * p.scale_colorbar_font)

        if p.save:

            ofn = fn.strip().split('.')
            ofn[-1] = p.save
            if p.prefix:
                ofn.insert(-1, p.prefix)
            ofn = '.'.join(ofn)

            if ofn == fn:
                raise RuntimeError('File name mismatch.')
            
            plt.savefig(ofn, dpi=p.dpi, format=p.save, transparent=p.transparent)
            plt.close()
            
        else:
            plt.show()


if __name__ == '__main__':
    main()
