This project is very small, and there's lot of room for
improvement. If you'd like to contribute, here's a quick guide:

1. Make an issue describing what you wish to fix.
2. Fork the repo.
3. Make your changes, and test them with `tox`.
4. Push to your fork and submit a pull request.
5. Check that the GitHub Actions CI tests pass.

## Testing your changes

You can test your changes with [tox](http://tox.readthedocs.org/en/latest/),
which you can install with:

    $ pip install tox

You can run tests on all supported Python versions, check the code
conforms to PEP 8, and check that the documentation builds
successfully by just running:

    $ tox

Once you're happy, push code to your fork, and submit a pull request. GitHub
Actions should pick up your PR and automatically run its tests, linter, etc on
your change. It uses multiple OSs and python versions so it may catch some
errors that your `tox` run didn't.

## Getting your pull request accepted

At this point you're waiting on me. I may suggest some changes or improvements
or alternatives. I am slow, I'm sorry. It may be weeks or months before I get
to it. I know, that's pretty terrible, but this is just a hobby project for me.
If you want to help speed things up by taking on co-maintainership, let me
know.

Some things that will increase the chance that your pull request is
accepted:

- If relevant, include tests that fail without your code and pass
  with it.
- Update all documentation that would be affected by your
  contribution.
- Make sure your code passes all `tox` checks locally, and all GitHub Actions
  checks on your PR.
- Ideally, make sure your commit messages are in the proper format:

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
