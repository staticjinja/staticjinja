This project is very small, and there's lot of room for
improvement. If you'd like to contribute, here's a quick guide:

1. Make an issue describing what you wish to fix.
2. Fork the repo.
3. Make your changes, and test them with `tox`.
4. Push to your fork and submit a pull request.

## Testing your changes with tox

You can test your changes with tox
(http://tox.readthedocs.org/en/latest/), which you can install with:

    $ pip install tox

You can run tests on all supported Python versions, check the code
conforms to PEP 8, and check that the documentation builds
successfully by just running:

    $ tox

Once you're happy, push code to your fork, and submit a pull request.

## Getting your pull request accepted

At this point you're waiting on me. I like to at least comment on, if
not accept, pull requests within three business days (and, typically,
one business day). I may suggest some changes or improvements or
alternatives.

Some things that will increase the chance that your pull request is
accepted:

- If relevant, include tests that fail without your code and pass
  with it.
- Update all documentation that would be affected by your
  contribution.
- Make sure your code passes all the checks that `tox` runs.
- Ideally, make sure your commit messages are in the proper format.

```

(#99999) Make the example in CONTRIBUTING imperative and concrete

Without this patch applied the example commit message in the CONTRIBUTING
document is not a concrete example.  This is a problem because the
contributor is left to imagine what the commit message should look like
based on a description rather than an example.  This patch fixes the
problem by making the example concrete and imperative.

The first line is a real life imperative statement with a ticket number
from our issue tracker.  The body describes the behavior without the patch,
why this is a problem, and how the patch fixes the problem when applied.

```
