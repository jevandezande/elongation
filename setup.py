import setuptools


def readme():
    with open('README.md') as f:
        return f.read()


setuptools.setup(
    name='Elongation',
    version='0.2',
    description='Package for managing elongation data.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    url='',
    author='Jonathon Vandezande',
    author_email='jevandezande@gmail.com',
    license='MIT',
    python_requires='>=3.6',
    setup_requires=['wheel'],
    install_requires=['numpy', 'matplotlib', 'more_itertools'],
    tests_require=['pytest', 'coverage'],
    scripts=['bin/convert_elongation', 'bin/plot_elongation'],
)
