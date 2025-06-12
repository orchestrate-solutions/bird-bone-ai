#!/usr/bin/env python3
"""
Setup script for Bird Bone AI project.
"""

from setuptools import setup, find_packages
import pathlib

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# Read requirements from requirements.txt
requirements = []
try:
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]
except FileNotFoundError:
    pass

setup(
    name="bird-bone-ai",
    version="0.1.0",
    description="AI-powered bird bone analysis and classification system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bird Bone AI Team",
    author_email="dev@bird-bone-ai.com",
    url="https://github.com/joshuawink/bird-bone-ai",
    project_urls={
        "Bug Reports": "https://github.com/joshuawink/bird-bone-ai/issues",
        "Source": "https://github.com/joshuawink/bird-bone-ai",
        "Documentation": "https://github.com/joshuawink/bird-bone-ai/docs",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="ai, machine learning, bird, bone, classification, computer vision",
    packages=find_packages(exclude=["tests*", "docs*"]),
    python_requires=">=3.8, <4",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "bird-bone-ai=scripts.validate_environment:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
