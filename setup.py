from setuptools import setup

setup(name='soilgenerate',
      version='0.1',
      description='Select seeds for optimal humus generation',
      url='http://github.com/ReedAnders/soilgenerate',
      author='Reed Anderson',
      author_email='reed.anderson@colorado.edu',
      license='MIT',
      packages=['soilgenerate'],
      entry_points={
      	'console_scripts': 
      		['soilgenerate = soilgenerate.__main__:main']
      		},
      zip_safe=False)
