from setuptools import setup

with open('version.value', 'r') as f:
    version = f.readline().strip()

with open('./aicsimagetools/aicsimagetools_version.py', 'w') as f:
    f.writelines('AICSIMAGETOOLS_VERSION = "{}"'.format(version))


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='aicsimagetools',
      version=version,
      description='Simple file format readers and writers',
      long_description=readme(),
      url='http://stash.corp.alleninstitute.org/projects/AICS/repos/aicsimagetools',
      author='Dan Toloudis',
      author_email='danielt@alleninstitute.org',
      license='MIT',
      packages=['aicsimagetools'],
      scripts=[],
      install_requires=[
          'numpy',
          'pillow',
          'scipy',
          'tifffile'
      ],
      zip_safe=False,
      test_suite='test.test_suite'
      )
