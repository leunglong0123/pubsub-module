from setuptools import setup, find_packages

setup(
    name="pubsub_module",  # Name of the module
    version="1.0.0",       # Module version
    description="A reusable Pub/Sub module for GCP",
    author="Bryan",
    author_email="leonellus0123@gmail.com",
    packages=find_packages(),  # Automatically find packages
    install_requires=[
        "google-cloud-pubsub>=2.11.0",  # List dependencies
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version
)
