# coding: utf-8
from io import open
import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('pitools/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(f.read()).group(1)))


setup(
    name='pitools',
    version=version,
    url='https://github.com/JokerQyou/pitools',
    license='BSD',
    author='Joker Qyou',
    author_email='Joker.Qyou@gmail.com',
    description='A server running on rPi',
    long_description=open('README.md').read(),
    packages=['pitools', ],
    include_package_data=True,
    zip_safe=False,
    platforms='linux',
    install_requires=open('requirements.txt').readlines(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Hardware',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
