from setuptools import setup

setup(
    name='FieldEP',
    version='1.0',
    description='Runs software on RPi Zero to operate FieldEP'
                'IOT devices',
    author='Oli Tills',
    url='https://github.com/EmbryoPhenomics/fieldep_software/tree/main/FieldEP',
    packages=['ms5837'],
    install_requires=['opencv-python',
                      'picamera',
                      'scipy',
                      'math',
                      'numpy',
                      'skimage',
                      'vuba',
                      'python-smbus'
                      'tsys01',
                      'ms5837'
                      ],
    dependancy_links=[
        'https://github.com/bluerobotics/ms5837-python',
        'https://github.com/bluerobotics/tsys01-python'
    ]
)