import setuptools

desc = """\
=================
QWC Services Core
=================
Shared modules for QWC services.
"""

setuptools.setup(
    name="qwc-services-core",
    version="1.1.5",
    author="Sourcepole AG",
    author_email="info@sourcepole.ch",
    description="Shared modules for QWC services",
    long_description=desc,
    long_description_content_type="text/x-rst",
    url="https://github.com/qwc-services/qwc-services-core",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
