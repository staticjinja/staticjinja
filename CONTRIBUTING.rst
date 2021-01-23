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
fork, install all the dependencies, and then install tox_ for testing:

.. code-block:: bash

    $ cd $HOME/projects
    $ git clone git://github.com/{YOUR_USERNAME}/staticjinja.git
    $ cd staticjinja
    $ python -m pip install --upgrade pip
    $ pip install -r requirements.txt
    $ pip install tox

Making Changes
--------------

Start making edits! If you need to test these changes against your personal
project, then you'll need to install the local, modified version of
staticjinja for your project to use. Do this by running

.. code-block:: bash

    $ python setup.py install

whenever you make edits. There might be a better way to do this, but IDK what
it is. Please file an Issues_ if you know!

Testing your Changes
--------------------

You should test your changes with tox_:

.. code-block:: bash

    $ tox

This will:

* Run tests on multiple Python versions.
* Check that the code is formatted to conform to PEP 8.
* Check that the documentation builds successfully.

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
.. _tox: https://tox.readthedocs.org/en/stable/
.. _good commit message style: https://chris.beams.io/posts/git-commit/
