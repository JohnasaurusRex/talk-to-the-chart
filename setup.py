from setuptools import setup, find_packages

setup(
    name="talk-to-chart",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
    extras_require={
        "dev": ["pytest"],
    },
)
