import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pylilo',
    version='0.1',
    author="jzarca01",
    author_email="jeremie.zarca@gmail.com",
    description="Connect to a LILO Pret a pousser via Bluetooth",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jzarca01/pylilo",
    packages=setuptools.find_packages(),
    install_requires=[
        'bleak>=0.18.1'
        'bleak-retry-connector>=2.1.3',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
 )
