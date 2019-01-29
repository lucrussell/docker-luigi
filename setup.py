from setuptools import setup, find_packages


desc = ''
with open('README.md', 'r') as fp:
    desc = fp.read()

setup(
    name='Docker-Luigi',
    version='1.0.0',
    description='Docker Luigi Example',
    long_description=desc,
    url='https://github.com',
    author='MyOrganization',
    license='',
    classifiers=[
        'Intended Audience :: Information Technology',
        'Intended Audience :: Software Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'luigi',
                                    'luigistate', 'docker', 'data', 'examples', 'report']),
    install_requires=[
        'luigi',
        'requests',
    ],
    package_data={},
    data_files=[],
    entry_points={
        'console_scripts': [
            'example = example.__main__:main'
        ],
    },
)
