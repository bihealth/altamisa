.. _installation:

.. highlight:: shell

============
Installation
============

Using ``pip``
-------------

To install AltamISA, run this command in your terminal:

.. code-block:: console

    $ pip install altamisa

This is the preferred method to install AltamISA, as it will always install the most recent stable release.

If you don't have `pip <https://pip.pypa.io>`_ installed, this `Python installation guide <http://docs.python-guide.org/en/latest/starting/installation/>`_ can guide
you through the process.

Using ``conda``
---------------

If you like `conda <https://docs.conda.io/en/latest/>`_ as much as we do, you can install AltamISA from the `Bioconda <https://bioconda.github.io/>`_ channel.
This assumes that you have already setup conda and the Bioconda channel `as described in the Bioconda manual <https://bioconda.github.io/user/install.html>`_.

.. code-block:: console

    $ conda install altamisa

From sources
------------

The sources for AltamISA can be downloaded from the `Github repo <https://github.com/bihealth/altamisa>`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/bihealth/altamisa

Or download the `tarball <https://github.com/bihealth/altamisa/tarball/master>`_:

.. code-block:: console

    $ curl  -OL https://github.com/bihealth/altamisa/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install

