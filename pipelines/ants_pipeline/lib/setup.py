import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="example-pkg-Antogeo",
    version="0.0.1",
    maintainer="@antogeo",
    author="Example Author",
    author_email="g.antonopoulos@fz-juelich.de",
    description="ants segmentation pipeline (htcondor)",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://jugit.fz-juelich.de/g.antonopoulos/ants_pipeline",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering",
        "Topic :: Neuroimaging",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research"
    ],
    packages=setuptools.find_packages(
              exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires='>=3.6',
)
