try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
from fasthttp import __version__
version = __version__
    
with open("README.md") as f:
    readme = f.read()

with open("requirements.txt") as f:
    requirements = [r.strip() for r in f]


_classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
]

setup(name="fasthttp",
    version=version,
    packages=["fasthttp"],
    include_package_data=True,
    author="Joel",
    author_email="",
    url="https://github.com/zoreu/fasthttp",
    description="fasthttp",
    long_description=readme,
    license="MIT",
    classifiers=_classifiers,
    install_requires=requirements,
    python_requires=">=2.7",
    )
