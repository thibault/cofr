"""
A simple Key-Value store encrypted with Trezor.
"""
from setuptools import find_packages, setup

dependencies = ['cryptography', 'readline', 'trezor', 'click']

setup(
    name='cofr',
    version='1.0.0b2',
    url='https://github.com/thibault/cofr',
    license='MIT',
    author='Thibault Jouannic',
    author_email='thibault@miximum.fr',
    description='Make secure backups of sensitive data using your Trezor '
                'hardware wallet.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'cofr = cofr.cli:cli',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
