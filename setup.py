from setuptools import setup, find_packages

with open('version.value', 'r') as f:
    version = f.readline().strip()

with open('./aicsimage/aicsimage_version.py', 'w') as f:
    f.writelines('AICSIMAGE_VERSION = "{}"'.format(version))


setup(name='aicsimage',
      version=version,
      description='A generalized scientific image processing module from the Allen Institute for Cell Science.',
      url='http://stash.corp.alleninstitute.org/projects/AICS/repos/aicsimage',
      author='Zach Crabtree',
      author_email='zacharyc@alleninstitute.org',
      license='MIT',
      packages=find_packages(exclude=['test', 'pipeline']),
      scripts=[],
      install_requires=[
            'numpy>=1.12',
            'Pillow>=3.3.1',
            'scipy>=0.18.1',
            'matplotlib>=2.0.0',
            'scikit-image>=0.13.0',
            'nose>=1.3.7',
            'tifffile>=0.12.1'
      ],
      test_suite='test.test_suite',
      zip_safe=False,
      )
