from setuptools import setup

with open('version.value', 'r') as f:
    version = f.readline().strip()

with open('./aics/image/processing/aicsimageprocessing_version.py', 'w') as f:
    f.writelines('AICSIMAGEPROCESSING_VERSION = "{}"'.format(version))


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='aicsimageprocessing',
      version=version,
      description='A generalized scientific image processing module from the Allen Institute for Cell Science.',
      long_description=readme(),
      url='http://stash.corp.alleninstitute.org/projects/AICS/repos/image-processing',
      author='Zach Crabtree',
      author_email='zacharyc@alleninstitute.org',
      license='MIT',
      packages=['aics.image.processing'],
      scripts=[],
      install_requires=[],
      zip_safe=False,
      )
