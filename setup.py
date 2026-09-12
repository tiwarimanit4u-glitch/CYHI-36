import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

# Read the README for the long description (fallback if missing)
try:
    long_description = (HERE / "README.md").read_text(encoding="utf-8")
except Exception:
    long_description = "Doc‑Scout: AI‑augmented CLI for documentation‑drift detection."

setup(
    name="doc-scout",
    version="0.1.0",
    description="AI‑augmented CLI for documentation‑drift detection.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Harsh Bansal",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
        "google-generativeai>=0.4.0",
        "python-dotenv>=1.0",
    ],
    entry_points={
        "console_scripts": [
            "doc-scout=doc_scout.__main__:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
