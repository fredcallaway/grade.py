from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='gradepy',
      version='0.3',
      description='Tools for automated grading of python assignments.',
      long_description=readme(),
      keywords='grade grading python framework student assignment',
      url='https://github.com/fredcallaway/grade.py',
      author='Fred Callaway',
      author_email='fredc@llaway.com',
      license='MIT',
      packages=['gradepy'],  
      include_package_data=True,
      zip_safe=False)