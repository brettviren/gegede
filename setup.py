from setuptools import setup


setup(name = 'gegede',
      version = '0.3',
      description = 'General Geometry Description',
      author = 'Brett Viren',
      author_email = 'brett.viren@gmail.com',
      license = 'GPLv2',
      url = 'http://github.com/brettviren/gegede',
      package_dir = {'':'python'},
      packages = ['gegede', 'gegede.schema', 'gegede.export',
                  'gegede.export.gdml', 'gegede.examples'],
      # These are just what were developed against.  Older versions may be okay.
      install_requires=[
          "pint >= 0.5.1",      # for units
          "lxml >= 3.3.5",      # for GDML export
      ],
      # implicitly depends on ROOT
      entry_points = {
          'console_scripts': [
              'gegede-cli = gegede.main:main',
              ]
      }
              
  )

