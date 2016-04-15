from setuptools import setup

PACKAGES = ['django_fields_changes']

REQUIREMENTS = []

version = __import__('django_fields_changes').__version__

setup(
      name='django-fields-changes',
      version=version,
      description="Django application for tracking fields changes",
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'],
      author='Alejandro Souto',
      author_email='sorinaso@gmail.com',
      url='https://github.com/sorinaso/django-fields-changes',
      license='MIT',
      packages=PACKAGES,
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIREMENTS,
)
