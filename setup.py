from setuptools import setup, find_packages

setup(
    name='smother',
    version='0.0.1',
    packages=find_packages(),
    entry_points={
        'nose.plugins.0.10': [
            'smother = smother.nose_plugin:SmotherNose',
        ],
        'console_scripts': [
            'smother = smother.cli:cli'
        ]
    },
)
