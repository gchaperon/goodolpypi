import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="goodolpypi",
    version="0.0.1",
    author="gchaperon",
    description="Fetch latest version for packages at a given date",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gchaperon/goodolpypi",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    entry_points={"console_scripts": ["goodolpypi=goodolpypi.main:main"]},
)
