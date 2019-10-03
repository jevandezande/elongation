import setuptools


def readme():
    with open('README.rst') as f:
        return f.read()

setuptools.setup(
    name="Elongation",
    version="0.1",
    description="Package for managing elongation data.",
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    url="",
    author="Jonathon Vandezande",
    author_email="jevandezande@gmail.com",
    license="MIT",
    python_requires='>=3.6',
    packages=setuptools.find_packages(exclude=['*test*']),
    install_requires=["numpy"],
    test_suite='elongation.tests',
    tests_require=['pytest'],
    scripts=['bin/convert_elongation'],
)
