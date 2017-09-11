from setuptools import setup, find_packages

README = 'a pimped up subprocess module with monitoring and remote (SSH) capabilities'

requires = []
tests_require = [
        'pytest',
        'testix==0.9',
        ]

setup(name='pimped_subprocess',
      version='2.2.0',
      description=README,
      long_description=README,
      url='https://github.com/haarcuba/pimped_subprocess',
      classifiers=[
          "Programming Language :: Python",
      ],
      author='Yoav Kleinberger',
      author_email='haarcuba@gmail.com',
      keywords='subprocess, terminal, monitoring',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=requires,
      )
