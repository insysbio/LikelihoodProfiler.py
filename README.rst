.. image::
   https://img.shields.io/website-up-down-green-red/https/insysbio.github.io/LikelihoodProfiler.py.svg
   :height: 20
   :target: https://insysbio.github.io/LikelihoodProfiler.py/
   :alt: Documentation

.. image::
   https://travis-ci.org/insysbio/LikelihoodProfiler.py.svg?branch=master
   :height: 20
   :target: https://travis-ci.org/insysbio/LikelihoodProfiler.py
   :alt: Travis build status

.. image::
   https://ci.appveyor.com/api/projects/status/github/insysbio/LikelihoodProfiler.py?branch=master&svg=true
   :height: 20
   :target: https://ci.appveyor.com/project/metelkin/likelihoodprofiler-py
   :alt: Appveyor build status

.. image::
   https://zenodo.org/badge/DOI/10.13140/RG.2.2.18935.06563.svg
   :height: 20
   :target: https://doi.org/10.13140/RG.2.2.18935.06563
   :alt: DOI:10.13140/RG.2.2.18935.06563

Intro
*****

**LikelihoodProfiler** is a package for identifiability analysis and confidence intervals evaluation which was originally written in **Julia** language. See https://github.com/insysbio/LikelihoodProfiler.jl This is the translation of the original **Julia** code to **Python**.

Installation
************

If your OS is Windows, you have to install NLopt wheel. Go to
  https://www.lfd.uci.edu/~gohlke/pythonlibs/#nlopt

Download the wheel which suits you and install it with:

  pip install NLopt-***.whl

Then clone LikelihoodProfiler from

  https://github.com/insysbio/LikelihoodProfiler.py.git

Install LikelihoodProfiler requirements with:

  pip install -r requirements.txt

Quick start
***********

Plot simple profile::

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
