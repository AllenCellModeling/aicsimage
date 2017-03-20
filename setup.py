from setuptools import setup, find_packages

with open('version.value', 'r') as f:
    version = f.readline().strip()

with open('./aics/image/io/aicsimageio_version.py', 'w') as f:
    f.writelines('AICSIMAGEIO_VERSION = "{}"'.format(version))


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='aics.image.io',
      version=version,
      description='Simple file format readers and writers',
      long_description=readme(),
      url='http://stash.corp.alleninstitute.org/projects/AICS/repos/aicsimageio',
      author='Dan Toloudis',
      author_email='danielt@alleninstitute.org',
      license='MIT',
      packages=find_packages(),
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
