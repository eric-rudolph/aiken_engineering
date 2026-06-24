import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap


def scatter_with_filter(
        data: dict[str, np.ndarray],
        title: str,
        size: tuple[int | float, int | float] = (20, 5),
        color: str = "hsv",
        s: float = 2.0,
        colors_rgb: ListedColormap | None = None,
        filter_data: np.ndarray | None = None
):
    """
    Can specify list of colors to plot in discrete mode.
    Example:
    plot_data(data={"Theta (degrees)": nodes["Y"],
                    "Height (inches)": nodes["Z"],
                    "Membrane Stress (psi)": nodes["Pm"]},
              title="Membrane Stress in Shell",
              colors_rgb=ansys_colors),
              filter_data=ndarray same length as data
    """
    x, y, z = data.keys()

    fig = plt.figure(figsize=size)
    ax = fig.add_subplot(111)

    xvals = np.asarray(list(data[x]))
    yvals = np.asarray(list(data[y]))
    zvals = np.asarray(list(data[z]))

    if filter_data is None:
        plot_mask = np.ones(len(zvals), dtype=bool)
    else:
        plot_mask = np.asarray(filter_data, dtype=bool).ravel()
        if len(plot_mask) != len(zvals):
            raise ValueError("filter_data must be the same length as the data arrays.")
        ax.scatter(xvals[~plot_mask], yvals[~plot_mask], s=s / 10, c="0.75")

    x_plot = xvals[plot_mask]
    y_plot = yvals[plot_mask]
    z_plot = zvals[plot_mask]

    if len(z_plot) == 0:
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(title)
        plt.show()
        return

    # DISCRETE mode
    if colors_rgb is not None:
        if len(colors_rgb) < 1:
            raise ValueError("colors_rgb must contain at least 1 (r,g,b) color.")

        # Convert (r,g,b) to 0..1 floats (support 0..255 ints or 0..1 floats)
        cols = np.asarray(colors_rgb, dtype=float)
        if cols.max() > 1.0:
            cols = cols / 255.0
        cols = np.clip(cols, 0.0, 1.0)

        cmap = mcolors.ListedColormap(cols)

        # Auto-scale boundaries from z range into N discrete bins
        zmin = float(np.nanmin(z_plot))
        zmax = float(np.nanmax(z_plot))
        n = len(cols)

        # Handle constant z gracefully: everything gets the first color
        if np.isclose(zmin, zmax) or not np.isfinite(zmin) or not np.isfinite(zmax):
            boundaries = np.array([zmin - 0.5, zmin + 0.5])
            norm = mcolors.BoundaryNorm(boundaries, cmap.N)
        else:
            boundaries = np.linspace(zmin, zmax, n + 1)
            norm = mcolors.BoundaryNorm(boundaries, cmap.N)

        p = ax.scatter(x_plot, y_plot, s=s, c=z_plot, cmap=cmap, norm=norm)

        cbar = fig.colorbar(p, ax=ax, shrink=0.75, label=z, boundaries=boundaries)
        cbar.ax.set_yticklabels([f"{b:g}" for b in boundaries])

    # CONTINUOUS mode
    else:
        p = ax.scatter(x_plot, y_plot, s=s, c=z_plot, cmap=color)
        fig.colorbar(p, ax=ax, shrink=0.75, label=z)

    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(title)
    plt.show()
