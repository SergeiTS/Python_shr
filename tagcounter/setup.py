from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tagcounter",
    version="0.0.2",
    author="Serhii Tsotsko",
    author_email="stsotsko@outlook.com",
    description="Web-site tags counter program",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SergeiTS/Python_shr",
    packages=find_packages(),
    entry_points={'console_scripts': ['tagcounter = tagcounter.tagcounter:main']},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
)
