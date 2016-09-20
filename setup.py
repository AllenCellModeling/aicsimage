from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='aicsimagetools',
      version='0.1',
      description='Simple file format readers and writers',
      long_description=readme(),
      url='http://stash.corp.alleninstitute.org/projects/AICS/repos/aicsimagetools',
      author='Dan Toloudis',
      author_email='danielt@alleninstitute.org',
      license='MIT',
      packages=['aicsimagetools'],
      scripts=['bin/interleave.py']
      install_requires=[
          'numpy',
          'pillow',
          'scipy',
          'tifffile'
      ],
      zip_safe=False)
