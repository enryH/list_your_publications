# Example Python package

Source was based on
[article from Chris Holdgraf](https://chrisholdgraf.com/blog/2022/orcid-auto-update/)
from his blog.

## How to use

Install the package from github using pip:

```bash
pip install git+https://github.com/RasmussenLab/list_your_publications.git
```

Then you have the command line script available.

```bash
fetch_orcid_pubs --orcid-id 0000-0001-8833-7617 --lastname Webel --output-file publications.md
```

## Development environment

Install package so that new code is picked up in a restared python interpreter:

```
pip install -e .
```

## TestPyPI

Install vom [TestPyPI](https://test.pypi.org/project/list-publications/):

```
pip install -i https://test.pypi.org/simple/ list-publications
```

<!-- ## Readthedocs

The documentation is build using readthedocs automatically. See 
[project on Readthedocs](https://readthedocs.org/projects/list-publications/).

- make sure to enable build from PRs in the settings (advanded settings)
- checkout configuration file: [`.readthedocs.yaml`](.readthedocs.yaml) -->
