import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from itertools import cycle


def plotter(
    elongs,
    title=None, style='stress/strain',
    plot=None,
    xlim=None, xticks=None, xticks_minor=True, xlabel=None,
    ylim=None, yticks=None, yticks_minor=True, ylabel=None,
    smoothed=False,
    legend=True, colors=None, markers=None, linestyles=None,
    peaks=False, youngs_modulus=False,
    savefig=None,
):
    """
    :param elongs: list of Elongation objects
    :param title: title of the plot
    :param style: plot-style
    :param plot: (figure, axis) on which to plot, generates new figure if None
    :param x*: x-axis setup parameters
    :param y*: y-axis setup parameters
    :param smoothed: number of points with which to smooth
    :param legend: boolean to plot legend
    :param colors: colors to plot the spectra
    :param markers: markers to plot the spectra
    :param linestyles: linestyles to plot the spectra
    :param peaks: dictionary of peak picking parameters
    :param youngs_modulus: dictionary of Young's modulus picking parameters
    :param savefig: where to save the figure
    :return: figure and axes
    """
    if plot is None:
        fig, ax = plt.subplots()
    else:
        fig, ax = plot

    setup_axis(ax, style, title, xlim, xticks, xticks_minor, xlabel, ylim, yticks, yticks_minor, ylabel)

    if smoothed:
        elongs = [elong.smoothed(smoothed) for elong in elongs]

    plot_elongations(elongs, ax, style, markers=markers, linestyles=linestyles, colors=colors, peaks=peaks, youngs_modulus=youngs_modulus)

    if legend:
        ax.legend()

    if savefig:
        fig.savefig(savefig)

    return fig, ax


def plot_elongations(elongs, ax, style='stress/strain', markers=None, linestyles=None, colors=None, peaks=False, youngs_modulus=False):
    """
    Plot Elongations on an axis.

    :param elongs: the Elongations to be plotted
    :param ax: the axis on which to plot
    :param style: the plot style
    :param markers: the markers to use at each point on the plot
    :param linestyles: the styles of line to use
    :param colors: the colors to use
    :param peaks: dictionary of peak picking parameters
    :param youngs_modulus: dictionary of Young's modulus picking parameters
    :return: figure and axes
    """
    colors = cycle_values(colors)
    markers = cycle_values(markers)
    linestyles = cycle_values(linestyles)

    for elong, color, marker, linestyle in zip(elongs, colors, markers, linestyles):
        plot_elongation(elong, ax, style, marker=marker, linestyle=linestyle, color=color, peaks=peaks, youngs_modulus=youngs_modulus)


def plot_elongation(elong, ax, style='stress/strain', marker=None, linestyle=None, color=None, peaks=False, youngs_modulus=False):
    """
    Plot an Elongation on an axis

    :param elong: the Elongation to be plotted
    :param ax: the axis on which to plot
    :param style: the plot style
    :param marker: the marker to use at each point on the plot
    :param linestyle: the style of line to use
    :param color: the color to use
    :param peaks: dictionary of peak picking parameters
    :param youngs_modulus: dictionary of Young's modulus picking parameters
    """
    ax.plot(
        elong.xs, elong.ys,
        label=elong.name,
        marker=marker, linestyle=linestyle, color=color
    )

    if peaks:
        peak_defaults = {
            'color': color,
            'format': '3.0f',
            'labels': True,
            'marker': 'x',
            'print': True,
        }
        peaks = peak_defaults if peaks is True else {**peak_defaults, **peaks}
        peak_indices, _ = elong.peak_indices()
        peak_xs, peak_ys = elong.xs[peak_indices], elong.ys[peak_indices]

        if peaks['marker']:
            ax.scatter(peak_xs, peak_ys, color=peaks['color'], marker=peaks['marker'])

        if peaks['labels']:
            for x, y in zip(peak_xs, peak_ys):
                ax.text(x, y, f'{{:{peaks["format"]}}}'.format(x), verticalalignment='bottom')

        if peaks['print']:
            print('Peaks')
            print('   X       Y')
            for x, y in zip(peak_xs, peak_ys):
                print(f'{x:>6.1f} {y:>6.1f}')

    if youngs_modulus:
        youngs_modulus_defaults = {
            'color': color,
            'format': '4.1f',
            'labels': True,
            'tangent': True,
            'marker': 'x',
            'print': True,
        }
        youngs_modulus = youngs_modulus_defaults if youngs_modulus is True else {**youngs_modulus_defaults, **youngs_modulus}
        idx = np.nanargmax(elong.youngs_modulus_array)
        x, y, ym = elong.xs[idx], elong.ys[idx], elong.youngs_modulus_array[idx]

        if youngs_modulus['marker']:
            ax.scatter(x, y, color=youngs_modulus['color'], marker=youngs_modulus['marker'])

        if youngs_modulus['tangent']:
            xs = [0, 2*x]
            ys = [y - ym*x, y + ym*x]
            ax.plot(xs, ys, color=youngs_modulus['color'])

        if youngs_modulus['labels']:
            ax.text(x, y, f'{{:{youngs_modulus["format"]}}}'.format(x), verticalalignment='bottom')

        if youngs_modulus['print']:
            print(f'Modulus: {ym:5.1f} ({x:5.1f}, {y:5.1f})')


def setup_axis(
    ax, style='stress/strain', title=None,
    xlim=None, xticks=None, xticks_minor=True, xlabel=None,
    ylim=None, yticks=None, yticks_minor=True, ylabel=None
):
    """
    Setup the axis labels and limits. Autogenerates based on style for any variable set to None.

    :param ax: axis to setup
    :param style: style to use
    :param title: title of the axis
    :param *lim: limits for *-axis values
    :param *ticks: *-axis ticks
    :param *ticks_minor: *-axis minor ticks
    :param *label: label for the *-axis
    """
    # update values that are None
    up = lambda v, d: d if v is None else v
    # make ticks multiples of the tick width
    make_ticks = lambda start, end, tw: np.arange(int(start/tw)*tw, int(end/tw + 1)*tw, tw)

    backwards = True

    if style == 'stress/strain':
        if xlim:
            xticks = up(xticks, make_ticks(*xlim, 50))
        xlabel = up(xlabel, 'Strain (%)')
        ylabel = up(ylabel, 'Stress (N)')

    ax.set_title(title)

    if xticks is not None:
        ax.set_xticks(xticks)
    if xticks_minor is True:
        ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    elif xticks_minor is not None:
        xticks_minor *= 1 if not backwards else -1
        ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(xticks_minor))
    if yticks is not None:
        ax.set_yticks(yticks)
    if yticks_minor is True:
        ax.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    elif yticks_minor is not None:
        ax.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(yticks_minor))

    if xlim is not None:
        ax.set_xlim(*xlim)
    if ylim is not None:
        ax.set_ylim(*ylim)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def cycle_values(values):
    """
    Make a cycle iterator of values.

    :param values: value(s) to be cycled through
    :return: cycle of value(s)
    """
    if not isinstance(values, list):
        values = [values]
    return cycle(values)
