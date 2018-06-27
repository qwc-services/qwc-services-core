from distutils.core import setup


desc = """\
=================
QWC Services Core
=================

Shared modules for QWC services.
"""

setup(name='qwc-services-core',
      version='0.1',
      description='QWC Services Core',
      long_description=desc,
      author='Sourcepole AG',
      author_email='info@sourcepole.ch',
      url='https://github.com/qwc-services/qwc-services-core',
      packages=['qwc_services_core'],
      license='BSD-3-Clause'
      )
