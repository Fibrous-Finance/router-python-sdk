from setuptools import setup, find_packages

setup(
    name='fibrous-python',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        "requests",
        "starknet-py",
        "pydantic"
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
    author='kermo',
    description='Fibrous Finance Python Client.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Fibrous-Finance/router-python-sdk',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

)
