from setuptools import setup


setup(name = 'gegede',
      version = '0.0',
      description = 'General Geometry Description',
      author = 'Brett Viren',
      author_email = 'brett.viren@gmail.com',
      license = 'GPLv2',
      url = 'http://github.com/brettviren/gegede',
      package_dir = {'':'python'},
      packages = ['gegede', 'gegede.schema'],
      install_requires=[
          "pint >= 0.5.1",
      ],
  )

