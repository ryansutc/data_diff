import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(name='data_diff',
      version='0.1.2',
      description='Quickly compare two tables',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/ryansutc/data_diff',
      author='Ryan Sutclif',
      author_email="ryansutc@gmail.com",
      license='GNU',
      packages=setuptools.find_packages(),
      classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      entry_points={
          'console_scripts': ['csv_diff=data_diff.csv_diff:main'],
      },
	  install_requires=['pandas<0.23.1'],
      extras_require={'dev': ["jupyter", "pytest", "twine"]},
      zip_safe=False
      )