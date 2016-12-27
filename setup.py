from setuptools import setup

setup(
    name='devour',
    version='0.1',
    url='',
    author='http://github.com/brandoshmando',
    author_email='brancraft@gmail.com',
    license='MIT',
    packages=['devour',],
    install_requires=[
        'pykafka',
    ],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False,
    entry_points={
        'base_script': [
            'devour = devour.bin.devour:main'
        ]
    },
)
