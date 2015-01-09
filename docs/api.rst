.. _api:

Developer Interface
===================

.. module:: staticjinja

This part of the documentation covers staticjinja's API.

Main Interface
--------------

All of staticjinja's functionality can be accessed by this function,
which returns an instance of the :class:`Site <Site>` object.

.. autofunction:: make_site

Classes
~~~~~~~

.. autoclass:: staticjinja.Site
   :inherited-members:

.. autoclass:: staticjinja.Reloader
   :inherited-members:
