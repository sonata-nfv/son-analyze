"""An helper module usable from a notebook"""

from colorsys import rgb_to_hls, hls_to_rgb
import numpy as np
import pandas
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import warnings
warnings.simplefilter('ignore', category=FutureWarning)
from statsmodels.tsa.stattools import adfuller
warnings.resetwarnings()
import statsmodels as smt


def foobar():
    """An example function"""
    return 'foobar'


def shade_color(color, percent):
    """
    A color helper utility to either darken or lighten given color.
    This color utility function allows the user to easily darken or lighten a
    color for plotting purposes.  This function first converts the given color
    to RGB using ColorConverter and then to HSL.  The saturation is modified
    according to the given percentage and converted back to RGB.
    (From: https://github.com/matplotlib/matplotlib/pull/2745)

    Parameters
    ----------
    color : string, list, hexvalue
        Any acceptable Matplotlib color value, such as 'red', 'slategrey',
        '#FFEE11', (1,0,0)
    percent :  the amount by which to brighten or darken the color.
    Returns
    -------
    color : tuple of floats
        tuple representing converted rgb values
    """
    rgb = mcolors.colorConverter.to_rgb(color)
    h, l, s = rgb_to_hls(*rgb)
    l *= 1 + float(percent)/100
    l = np.clip(l, 0, 1)
    r, g, b = hls_to_rgb(h, l, s)
    return r, g, b


def test_stationarity(dataf):
    rolbase = dataf.rolling(center=False, window=12)
    rolmean = rolbase.mean()
    rolstd = rolbase.std()
    fig = plt.figure()
    pos = 0
    for k, elt in dataf.items():
        ax1 = fig.add_subplot(len(dataf.columns), 2, 1 + pos)
        ax3 = fig.add_subplot(len(dataf.columns), 2, 2 + pos)
        pos += 2
        bcolor = np.random.rand(3)
        bcolor = bcolor * [0.95, 1.0, 1.0]
        _ = ax1.plot(elt, '.', linewidth=0.2, label=k, c=bcolor)
        _ = ax1.plot(rolmean[k], '-.', linewidth=0.7, color='red',
                     label='Rolling Mean')
        _ = ax1.plot(rolstd[k], '--', linewidth=0.7, color='black',
                     label='Rolling Std')
        ax1.legend(loc='best')
        _ = ax3.plot(rolstd[k], '-', linewidth=0.7, color='black',
                     label='Rolling Std')
        ax3.legend(loc='best')
    fig.suptitle('Results of Dickey-Fuller Test')
    print('Results of Dickey-Fuller Test:')
    adf_results = {}
    for col in dataf.columns.values:
        try:
            dftest = adfuller(dataf[col], autolag='AIC')
        except np.linalg.LinAlgError as e:
            print('Catched error with col {}: {}'.format(col, e))
            continue
        dfoutput = pandas.Series(dftest[0:4],
                                 index=['Test Statistic', 'p-value',
                                        '#Lags Used',
                                        'Number of Observations Used'])
        for key,value in dftest[4].items():
            dfoutput['Critical Value (%s)'%key] = value
        adf_results[col] = dfoutput
    tmp = pandas.DataFrame(adf_results)
    print(tmp)
    return fig


def autocorrelation_plot(tserie, lags=20):
    fig = plt.figure()
    fig.suptitle('Time Series Analysis Plots for {}'.format(tserie.name))
    layout = (1, 2)
    tmp = {"acf": [plt.subplot2grid(layout, (0, 0)),
                   smt.tsa.stattools.acf(tserie, nlags=lags),
                   "q"],
           "pacf": [plt.subplot2grid(layout, (0, 1)),
                    smt.tsa.stattools.pacf(tserie, nlags=lags, method='ols'),
                    "p"]
          }
    z95 = 1.959963984540054
    z99 = 2.5758293035489004
    for k, v in tmp.items():
        target_ax = v[0]
        lenv1 = len(v[1])
        target_ax.set_xlim([0, lenv1])
        target_ax.set_ylim([-1, 1])
        target_ax.set_xticks(np.arange(0, lags + 1, 2))
        target_ax.set_xticks(np.arange(0, lags + 1, 1), minor=True)
        target_ax.plot(v[1], label=k)
        target_ax.axhline(y=0, linestyle='-', color='black')
        target_ax.axhline(y=z99 / np.sqrt(lenv1), linestyle='-.',
                          color='gray', label="+99%")
        target_ax.axhline(y=z95 / np.sqrt(lenv1), linestyle='--',
                          color='gray', label="+95%")
        target_ax.axhline(y=-z95 / np.sqrt(lenv1), linestyle='--',
                          color='gray', label="-95%")
        target_ax.axhline(y=-z99 / np.sqrt(lenv1), linestyle='-.',
                          color='gray', label="-99%")
        target_ax.set_xlabel("Lag")
        target_ax.set_ylabel("Autocorrelation")
        target_ax.legend(loc='best')
        target_ax.set_title(v[2])
        target_ax.grid(b=True, which='both')
    return fig
