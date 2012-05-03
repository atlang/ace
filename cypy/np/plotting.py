# All content Copyright 2010 Cyrus Omar <cyrus.omar@gmail.com> unless otherwise
# specified.
#
# Contributors:
#     Cyrus Omar <cyrus.omar@gmail.com>
#
# This file is part of, and licensed under the terms of, the atomic-hedgehog
# package.
#
# The atomic-hedgehog package is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# The atomic-hedgehog package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with the atomic-hedgehog package. If not, see <http://www.gnu.org/licenses/>.
"""Various plot utilities."""
from matplotlib.pyplot import * #@UnusedWildImport

def raster(times, indices, max_time=None, max_index=None, 
           x_label="Timestep", y_label="Index", **kwargs):
    """Plots a raster plot given times and indices of events."""
    # set default size to 1
    if 's' not in kwargs:
        kwargs['s'] = 1
    scatter(times, indices, **kwargs)
    
    if max_time is None:
        max_time = max(times)
    if max_index is None:
        max_index = max(indices)
    axis((0, max_time, 0, max_index))
    if x_label is not None: xlabel(x_label)
    if y_label is not None: ylabel(y_label)
    