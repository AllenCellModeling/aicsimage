from setuptools import setup, find_packages

with open('version.value', 'r') as f:
    version = f.readline().strip()


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='aicsimage',
      version=version,
      description='A generalized scientific image processing module from the Allen Institute for Cell Science.',
      long_description=readme(),
      url='http://stash.corp.alleninstitute.org/projects/AICS/repos/aicsimage',
      author='Zach Crabtree',
      author_email='zacharyc@alleninstitute.org',
      license='MIT',
      packages=find_packages(exclude=['test', 'pipeline']),
      scripts=[],
      install_requires=[],
      test_suite='test.test_suite',
      zip_safe=False,
      )
