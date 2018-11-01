# pcds-recipes
Collection of conda recipes for PCDS software at LCLS.

This repository is for conda recipes for packages that don't automatically
upload to the `pcds-tag` channel, but also can't be found on `conda-forge` or
in `defaults`. These tend to be community packages like EPICS, packages from
other groups at SLAC, and packages that we need to patch for some reason or
another.

## Adding a recipe
- Fork this repository and start a new branch for your recipe.
- Add the recipe into a folder with the package's name alongside the other
  recipes.
- Make sure you are on `psbuild-rhel6`
- Run `./test-conda.sh $PACKAGENAME` to make sure the build works
- If the build works, install the package into a conda environment and verify
  that the built package works. Check on both `psbuild-rhel6` and
  `psbuild-rhel7`. Feel free to do additional testing to convince yourself
  that everything works as expected.
- Add your package to the list of automatically built packages in `build.py`
- Make a PR and explain what the package is for

## Building
`build.py` will slowly check all the package variants in the build matrix and
build the variants that are missing on `pcds-tag`. Yes, we can make this faster
with some effort.

### Requirements
- You must have the `anaconda-client` package installed as well as be in an
  Conda environment with `conda-build=3.5.1`
- You must have a valid `Anaconda.org` profile that has access to the
  `pcds-tag` organization

### How To
- Generate a valid Anaconda token (remove old token first, then create new)
```bash
$ anaconda auth --remove build
$ ANACONDA_TOKEN=$(anaconda auth --create --name build --org pcds-tag --scopes api --max-age 1800)
```
- Build and upload
```bash
./build.py --channel pcds-tag --token $ANACONDA_TOKEN
```
