#
# Copyright 2019 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG DOCKER_UPSTREAM_REGISTRY
ARG DOCKER_UPSTREAM_TAG=latest

FROM ${DOCKER_UPSTREAM_REGISTRY}confluentinc/cp-base-new:${DOCKER_UPSTREAM_TAG}

ARG PROJECT_VERSION
ARG ARTIFACT_ID

ARG CONFLUENT_VERSION
ARG CONFLUENT_PACKAGES_REPO
ARG CONFLUENT_PLATFORM_LABEL
ARG CONFLUENT_DEB_VERSION
ARG ALLOW_UNSIGNED
LABEL maintainer="partner-support@confluent.io"

ENV COMPONENT=kafka-rest

# default listener
EXPOSE 8082


RUN echo "===> Installing ${COMPONENT}..." \
    && yum -q -y update \
    && yum install -y \
        confluent-${COMPONENT}-${CONFLUENT_VERSION}${CONFLUENT_PLATFORM_LABEL} \
        confluent-control-center-${CONFLUENT_VERSION}${CONFLUENT_PLATFORM_LABEL} \
        confluent-security-${CONFLUENT_VERSION}${CONFLUENT_PLATFORM_LABEL} \
    && echo "===> clean up ..."  \
    && yum clean all \
    && rm -rf /tmp/* \
    && echo "===> Setting up ${COMPONENT} dirs" \
    && chmod -R ag+w /etc/${COMPONENT}

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
