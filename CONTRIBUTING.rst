.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/bihealth/altamisa/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

AltamISA could always use more documentation, whether as part of the
official AltamISA docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/bihealth/altamisa/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `altamisa` for local development.

1. Fork the `altamisa` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/altamisa.git

3. Install your local copy with `uv <https://docs.astral.sh/uv/>`_, which creates ``.venv`` with
   the package in editable mode and all development dependencies::

    $ cd altamisa/
    $ uv sync

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass linting (ruff and pyright)
   and the tests::

    $ make format
    $ make lint
    $ make test

   The same checks run in CI for Python 3.11 through 3.14.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "fix: your short description of your changes"
    $ git push origin name-of-your-bugfix-or-feature

   Commit messages and pull request titles follow `conventional commits
   <https://www.conventionalcommits.org/>`_; release-please derives the version and changelog
   from them.

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.11, 3.12, 3.13, and 3.14. Check the GitHub Actions
   results on the pull request and make sure that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests::

$ uv run pytest tests/test_parse_investigation.py


Deploying
---------

A reminder for the maintainers on how to deploy.
Releases are made by `release-please <https://github.com/googleapis/release-please>`_:
every push to ``master`` updates a release pull request with the next version (derived from the
conventional commit messages) and the changelog. Merging that pull request creates the git tag
and the GitHub release, builds the package with ``uv build``, and publishes it to PyPI.

Do not edit ``CHANGELOG.md`` or ``altamisa/version.py`` by hand.
