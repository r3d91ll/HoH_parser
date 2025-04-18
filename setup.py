from setuptools import setup, find_packages

setup(
    name="HoH_parser",
    version="0.1.0",
    description="Hammer of Hephaestus ParserModel Context Protocol Server",
    author="Todd W. Bucy",
    author_email="todd@bucy-medrano.me",
    packages=find_packages(),
    install_requires=[],  # All runtime deps are in requirements.txt
    python_requires=">=3.11",
)
