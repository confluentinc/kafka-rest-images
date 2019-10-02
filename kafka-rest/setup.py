import setuptools


setuptools.setup(
    name='kafka-rest-tests',
    version='0.0.1',
    author="Confluent, Inc.",
    author_email="kafka-core-eng@confluent.io",
    description='Kafka REST docker image tests',
    url="https://github.com/confluentinc/kafka-rest-images",
    dependency_links=open("requirements.txt").read().split("\n"),
    packages=['test'],
    include_package_data=True,
    python_requires='>=2.7',
    setup_requires=['setuptools-git'],
)
