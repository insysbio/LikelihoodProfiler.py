`Documentation <https://insysbio.github.io/LikelihoodProfiler.py/>`_
.. image:: https://travis-ci.org/insysbio/LikelihoodProfiler.py.svg?branch=master
    :alt: Travis
    :target: https://travis-ci.org/insysbio/LikelihoodProfiler.py
    :figclass: align-center

Installation
************

If your OS is Windows, you have to install special wheel. Go to
  https://www.lfd.uci.edu/~gohlke/pythonlibs/#nlopt
and download the wheel that suits you.

For install python package, that you need, run next command::

  pip install -r requirements.txt

Quick start
*****

For plot simple get interval::

  from likelihoodprofiler import get_interval
  f_3p_1im_dep = lambda x: 5.0 + (x[0]-3.0)**2 + (x[0]-x[1]-1.0)**2 + 0*x[2]**2
  res0 = get_interval(
      [3., 2., 2.1],
      0,
      lambda x: f_3p_1im_dep(x),
      "LIN_EXTRAPOL",
      loss_crit = 9)
  res0.plot()
.. figure:: docs\plot.png
    :width: 455px
    :align: center
    :height: 312px
    :alt: alternate text
    :figclass: align-center
