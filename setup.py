from setuptools import setup

setup(name='fsleyes-plugin-epicseg',
      version='0.0.0',
      description='Epic seg plugin',
      author='Pierre Daudé',
      packages=['fsleyes_plugin_epicseg'],
      entry_points={
            'fsleyes_controls': ['EPIC segmentation = fsleyes_plugin_epicseg:PluginEpic',  ],
      }
      )