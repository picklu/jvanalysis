from setuptools import setup

setup(
    name='jvanalysis',
    version='1.0',
    license='GNU General Public License v3',
    author='Subrata Sarker',
    author_email='contact@subratasarker.com',
    description='Web application for extracting photovoltaic parameters and diode model parameters from JV data',
    packages=['jvanalysis'],
    include_package_data=True,
    platforms='any',
    install_requires=[
        'flask',
        'numpy',
        'scipy',
    ],
    classifiers=[
        'Development Status :: 1 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: CS50x subscribers',
        'License :: OSI Approved :: GNU General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)