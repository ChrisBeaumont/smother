import os
from setuptools import setup, find_packages, Command

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    with open('README.md') as infile:
        LONG_DESCRIPTION = infile.read()


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.egg-info ./htmlcov')

setup(
    name='smother',
    version='0.2',
    description='An abundance of coverage data',
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    author='Chris Beaumont',
    author_email='chrisnbeaumont@gmail.com',
    url='https://github.com/chrisbeaumont/smother',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
        'click',
        'more_itertools',
        'coverage>=4',
        'portalocker>=0.4',
        'six',
        'unidiff',
    ],
    entry_points={
        'nose.plugins.0.10': [
            'smother = smother.nose_plugin:SmotherNose',
        ],
        'console_scripts': [
            'smother = smother.cli:cli'
        ],
        'pytest11': [
            'smother = smother.pytest_plugin',
        ]
    },
    package_data={
        '': ["*.smother*"],
    },
    cmdclass={
        'clean': CleanCommand,
    }
)
