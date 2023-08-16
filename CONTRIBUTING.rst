Contributing
============

If you've found a bug, have an idea for a feature, or have a comment or other
question, we would love to hear from you. Search the Issues_ to see if anyone
else has run into the same thing. If so, add onto that issue. Otherwise, start
your own issue. Thanks for your thoughts!

If you want to implement the change yourself (that would be awesome!) then
continue...

Get the Code
------------

Fork the `staticjinja/staticjinja`_ repository on GitHub. Clone a copy of your
fork and get set up:

.. code-block:: bash

    $ cd $HOME/projects
    $ git clone git://github.com/{YOUR_USERNAME}/staticjinja.git
    $ cd staticjinja
    $ make init

The dev dependencies are installed in a virtual environment managed by poetry.
To use the dev tools (such as the ``pytest`` or ``flake8`` commands),
you need to either run them inside the poetry virtual environment with
``poetry run pytest``, or enter a poetry shell with ``poetry shell`` and then
you can run them directly such as ``pytest``. See the `Poetry docs`_ for more
info.

Making Changes
--------------

Start making edits! The ``poetry install`` command that was run in ``make init``
should have installed the local version of staticjinja in editable mode.
Any other projects on your system should be using the local version, in case
you want to test your changes.

Testing your Changes
--------------------

You should test your changes:

.. code-block:: bash

    $ make test

This will:

* Run tests on multiple Python versions.
* Check that the code is formatted and linted.
* Check that the documentation builds successfully.
* Check that the package builds successfully.

If one part of this test in particular is failing, let's say building the docs,
then you can iterate faster by just testing that one step with ``make docs``.
See the makefile for all the possible recipes.

Submitting a Pull Request
-------------------------

Nice job, your code looks awesome! Once you're done with your improvements,
there are a few checklist items that you should think about that will increase
the chances your PR will be accepted:

* Add yourself to ``AUTHORS.rst`` if you want.
* If relevant, write tests that fail without your code and pass
  with it. The goal is to increase our test coverage.
* Update all documentation that would be affected by your contribution.
* Use `good commit message style`_.
* Once your PR is submitted, make sure the GitHub Actions tests pass.

Once you're satisfied, push to your GitHub fork and submit a pull request
against the `staticjinja/staticjinja`_ ``main`` branch.

At this point you're waiting on me. I may suggest some changes or improvements
or alternatives. I am slow, I'm sorry. It may be weeks or months before I get
to it. I know, that's pretty terrible, but this is just a hobby project for me.
If you want to help speed things up by taking on co-maintainership, let me
know.

Thanks for your help!

.. _staticjinja/staticjinja : https://github.com/staticjinja/staticjinja
.. _Issues: https://github.com/staticjinja/staticjinja/issues
.. _Poetry docs: https://python-poetry.org/docs/basic-usage/#using-your-virtual-environment
.. _good commit message style: https://cbea.ms/git-commit/
