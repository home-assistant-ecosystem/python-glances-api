python-glances-api
==================

A Python client for interacting with `Glances <https://nicolargo.github.io/glances/>`_.

This module is not official, developed, supported or endorsed by Glances.

Installation
------------

The module is available from the `Python Package Index <https://pypi.python.org/pypi>`_.

.. code:: bash

    $ pip3 install glances_api

Or on a Fedora-based system or on a CentOS/RHEL machine with has EPEL enabled.

.. code:: bash

    $ sudo dnf -y install python3-glances-api


For Nix or NixOS is `pre-packed module <https://search.nixos.org/packages?channel=unstable&query=glances-api>`_
available. The lastest release is usually present in the ``unstable`` channel.

.. code:: bash

    $ nix-env -iA nixos.python3Packages.glances-api

Usage
-----

The file ``example.py`` contains an example about how to use this module.

License
-------

``python-glances-api`` is licensed under MIT, for more details check LICENSE.
