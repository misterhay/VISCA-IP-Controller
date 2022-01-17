from setuptools import setup

with open('README.md', 'r') as handle:
    long_description = handle.read()

setup(
    name='visca_over_ip',
    version='0.1.0',
    description='A driver package for the VISCA over IP protocol used by some Sony PTZ cameras',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Andrew Blomenberg',
    author_email='andrewBlomen@gmail.com',
    url='https://github.com/Yook74/VISCA-IP-Controller',
    packages=['visca_over_ip'],
)
