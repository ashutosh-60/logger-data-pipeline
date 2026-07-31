from setuptools import setup, find_packages

setup(
    name="data-logger-de",
    version="1.0.0",
    author="Data Engineering Platform Team",
    author_email="de-team@enterprise.com",
    description="An enterprise-grade, configuration-driven JSON logging package for data engineering pipelines.",
    long_description=open("README.md").read() if open("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/enterprise/data-logger-de",
    
    # Automatically scan the workspace for your modular subpackages
    packages=find_packages(exclude=["tests*", "docs*"]),
    
    # Lock down the exact external libraries required to boot the package
    install_requires=[
        "python-json-logger>=2.0.0",
        "pandas>=1.5.0",
        "SQLAlchemy>=1.4.0",
    ],
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
)