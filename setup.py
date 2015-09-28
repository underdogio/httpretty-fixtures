from setuptools import setup, find_packages


setup(
    name='httpretty_fixtures',
    version='2.1.0',
    description='Fixture manager for httpretty',
    long_description=open('README.rst').read(),
    keywords=[
        'httpretty',
        'fixture',
        'responses',
        'mock'
    ],
    author='Todd Wolfson',
    author_email='todd@twolfson.com',
    url='https://github.com/underdogio/httpretty-fixtures',
    download_url='https://github.com/underdogio/httpretty-fixtures/archive/master.zip',
    packages=find_packages(),
    license='MIT',
    install_requires=open('requirements.txt').readlines(),
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
