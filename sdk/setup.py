from setuptools import find_packages, setup

setup(
    name='nactite',
    version = '0.0.1',
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        'beautifulsoup4',
        'requests',
        'Unidecode'
    ],
    author = 'Nactite',
    author_email = '',
    description = '',
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires = '>=3.6',
)