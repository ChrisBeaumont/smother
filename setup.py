from setuptools import setup, find_packages

setup(
    name='smother',
    version='0.0.1',
    packages=find_packages(),
    install_requires = [
#        'click',
#        'diff_cover>=0.9',
#        'more_itertools',
        'coverage',
        'portalocker>=0.4',
        'six',
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
)
