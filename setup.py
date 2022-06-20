long_description = open('README.txt').read()

from setuptools import setup, find_packages

requires = ["requests"]

setup(
    name='bigbluebutton',
    version='0.6.1',
    author='Marcin Biegala',
    author_email='marcin@codeclusive.io',
    maintainer='Marcin Biegala',
    maintainer_email='marcin@codeclusive.io',
    url='https://github.com/codeclusiveio/bigbluebutton-cc',
    description='Python API for bigbluebutton.',
    long_description=long_description,
    keywords='bigbluebutton',
    license='MIT',
    packages=find_packages(),
    install_requires=requires,
)
    # Based on
    # name='bigbluebutton',
    # version='0.6.0',
    # author='Reimar Bauer',
    # author_email='rb.proj@gmail.com',
    # maintainer='Reimar Bauer',
    # maintainer_email='rb.proj@gmail.com',
    # url='https://hg.sr.ht/~dreimark/bigbluebutton-python-api',
    # description='Python API for bigbluebutton.',
    # long_description=long_description,
    # keywords='bigbluebutton',
    # license='MIT',
    # packages=find_packages(),
    # install_requires=requires,