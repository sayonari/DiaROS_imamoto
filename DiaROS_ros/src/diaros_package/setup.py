import os
from glob import glob
from setuptools import setup

package_name = 'diaros_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='81802',
    maintainer_email='81802@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pub = diaros_package.publisher:main',
            'relay = diaros_package.listener:main',
            'sub = diaros_package.testModule:main',
            'sm = diaros_package.ros2_sm:main',
            'lu = diaros_package.ros2_lu:main',
            'dm = diaros_package.ros2_dm:main',
            'rc = diaros_package.ros2_rc:main',
            'nlg = diaros_package.ros2_nlg:main',
            'ss = diaros_package.ros2_ss:main',
            'dr = diaros_package.ros2_dr:main',
            'mm = diaros_package.ros2_mm:main'
        ],
    },
)
