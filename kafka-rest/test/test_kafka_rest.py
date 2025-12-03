import os
import unittest
import utils
import time
import string
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, "fixtures")
KAFKA_READY = "bash -c 'kafkacat -L -b localhost:9092 -J && echo PASS || echo FAIL'"
HEALTH_CHECK = "bash -c 'cub kr-ready {host} {port} 20 && echo PASS || echo FAIL'"

GET_TOPICS_CHECK = "bash -c 'curl -X GET -i {host}:{port}/topics'"

POST_TO_TOPIC_CHECK = """curl -X POST -H "Content-Type: application/vnd.kafka.json.v1+json" \
    --data '{"records":[{"value":{"foo":"bar"}}]}' \
    %s:%s/topics/%s"""

JMX_CHECK = """bash -c "\
    echo 'get -b kafka.rest:type=jetty-metrics connections-active' |
        java -jar jmxterm-1.0-alpha-4-uber.jar -l {jmx_hostname}:{jmx_port} -n -v silent "
"""

DOCKER_IMAGE_NAME = "{0}confluentinc/cp-kafka-rest:{1}".format(os.environ.get("DOCKER_REGISTRY",""), os.environ.get("DOCKER_TAG","latest"))
class ConfigTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        machine_name = os.environ["DOCKER_MACHINE_NAME"]
        cls.machine = utils.TestMachine(machine_name)

        cls.cluster = utils.TestCluster("config-test", FIXTURES_DIR, "standalone-config.yml")
        cls.cluster.start()

        assert "PASS" in cls.cluster.run_command_on_service("kafka", KAFKA_READY.format(brokers=1))

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    @classmethod
    def is_kafka_rest_healthy_for_service(cls, service):
        output = cls.cluster.run_command_on_service(service, HEALTH_CHECK.format(host="localhost", port=8082))
        assert "PASS" in output

    def test_required_config_failure(self):
        self.assertTrue("one of (KAFKA_REST_ZOOKEEPER_CONNECT,KAFKA_REST_BOOTSTRAP_SERVERS) is required." in self.cluster.service_logs("failing-config", stopped=True))

    def test_default_config(self):
        self.is_kafka_rest_healthy_for_service("default-config")
        props = self.cluster.run_command_on_service("default-config", "bash -c 'cat /etc/kafka-rest/kafka-rest.properties | sort'")
        expected = """
            bootstrap.servers=PLAINTEXT://kafka:9092
            host.name=default-config
            """
        self.assertEquals(props.translate(None, string.whitespace), expected.translate(None, string.whitespace))

    def test_default_logging_config(self):
        self.is_kafka_rest_healthy_for_service("default-config")

        logger_props = self.cluster.run_command_on_service("default-config", "cat /etc/kafka-rest/log4j2.yaml")
        expected_logger_props = """Configuration:
              name: "Log4j2"

              Appenders:
                Console:
                  name: STDOUT
                  target: SYSTEM_OUT
                  PatternLayout:
                    Pattern: "[%d] %p %m (%c)%n"

              Loggers:
                Root:
                  level: "INFO"
                  AppenderRef:
                    - ref: STDOUT
                Logger:
            """
        self.assertEquals(logger_props.translate(None, string.whitespace), expected_logger_props.translate(None, string.whitespace))


class StandaloneNetworkingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cluster = utils.TestCluster("standalone-network-test", FIXTURES_DIR, "standalone-network.yml")
        cls.cluster.start()
        assert "PASS" in cls.cluster.run_command_on_service("kafka-bridge", KAFKA_READY.format(brokers=1))
        assert "PASS" in cls.cluster.run_command_on_service("kafka-host", KAFKA_READY.format(brokers=1))

    @classmethod
    def tearDownClass(cls):
        cls.cluster.shutdown()

    @classmethod
    def is_kafka_rest_healthy_for_service(cls, service, port=8082):
        output = cls.cluster.run_command_on_service(service, HEALTH_CHECK.format(host="localhost", port=port))
        assert "PASS" in output

    def test_bridged_network(self):
        # Test from within the container
        self.is_kafka_rest_healthy_for_service("kafka-rest-bridge")
        # Test from outside the container on host network
        logs = utils.run_docker_command(
            image=DOCKER_IMAGE_NAME,
            command=HEALTH_CHECK.format(host="localhost", port=18082),
            host_config={'NetworkMode': 'host'})

        self.assertTrue("PASS" in logs)

        # Test from outside the container on bridge network
        logs_2 = utils.run_docker_command(
            image=DOCKER_IMAGE_NAME,
            command=HEALTH_CHECK.format(host="kafka-rest-bridge", port=8082),
            host_config={'NetworkMode': 'standalone-network-test_zk'})

        self.assertTrue("PASS" in logs_2)

        # Test writing a topic and confirm it was written by checking for it
        logs_3 = utils.run_docker_command(
            image=DOCKER_IMAGE_NAME,
            command=POST_TO_TOPIC_CHECK % ("kafka-rest-bridge", 8082, "testtopicbridge"),
            host_config={'NetworkMode': 'standalone-network-test_zk'})

        self.assertTrue("value_schema_id" in logs_3)

        logs_4 = utils.run_docker_command(
            image=DOCKER_IMAGE_NAME,
            command=GET_TOPICS_CHECK.format(host="kafka-rest-bridge", port=8082),
            host_config={'NetworkMode': 'standalone-network-test_zk'})

        self.assertTrue("testtopicbridge" in logs_4)

    def test_host_network(self):
        # Test from within the container
        self.is_kafka_rest_healthy_for_service("kafka-rest-host")
        # Test from outside the container
        logs = utils.run_docker_command(
            image=DOCKER_IMAGE_NAME,
            command=HEALTH_CHECK.format(host="localhost", port=8082),
            host_config={'NetworkMode': 'host'})

        self.assertTrue("PASS" in logs)

        # Test writing a topic and confirm it was written by checking for it
        logs_2 = utils.run_docker_command(
            image=DOCKER_IMAGE_NAME,
            command=POST_TO_TOPIC_CHECK % ("localhost", 8082, "testtopichost"),
            host_config={'NetworkMode': 'host'})

        self.assertTrue("value_schema_id" in logs_2)

        logs_3 = utils.run_docker_command(
            image=DOCKER_IMAGE_NAME,
            command=GET_TOPICS_CHECK.format(host="localhost", port=8082),
            host_config={'NetworkMode': 'host'})

        self.assertTrue("testtopichost" in logs_3)

    def test_jmx_bridged_network(self):

        self.is_kafka_rest_healthy_for_service("kafka-rest-bridged-jmx")

        # Test from outside the container
        logs = utils.run_docker_command(
            image="confluentinc/cp-jmxterm",
            command=JMX_CHECK.format(jmx_hostname="kafka-rest-bridged-jmx", jmx_port=9999),
            host_config={'NetworkMode': 'standalone-network-test_zk'})
        self.assertTrue("connections-active =" in logs)

    def test_jmx_host_network(self):

        self.is_kafka_rest_healthy_for_service("kafka-rest-host-jmx", 28082)

        # Test from outside the container
        logs = utils.run_docker_command(
            image="confluentinc/cp-jmxterm",
            command=JMX_CHECK.format(jmx_hostname="localhost", jmx_port=39999),
            host_config={'NetworkMode': 'host'})
        self.assertTrue("connections-active =" in logs)