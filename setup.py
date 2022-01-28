from setuptools import setup
import visca_over_ip

with open('README.md', 'r') as handle:
    long_description = handle.read()

setup(
    name='visca_over_ip',
    version=visca_over_ip.__version__,
    description='A driver package for the VISCA over IP protocol used by some Sony PTZ cameras',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Yook74 and misterhay',
    author_email='andrewBlomen@gmail.com',
    url='https://github.com/Yook74/VISCA-IP-Controller',
    packages=['visca_over_ip'],
)
