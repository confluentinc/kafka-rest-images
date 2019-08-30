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

ENV COMPONENT=kafka-rest

# default listener
EXPOSE 8082


RUN echo "===> Installing ${COMPONENT}..." \
    && apt-get update \
    && echo "===> Adding confluent repository...${CONFLUENT_PACKAGES_REPO}" \
    && if [ "x$ALLOW_UNSIGNED" = "xtrue" ]; then echo "APT::Get::AllowUnauthenticated \"true\";" > /etc/apt/apt.conf.d/allow_unauthenticated; else curl -s -L ${CONFLUENT_PACKAGES_REPO}/archive.key -o /tmp/archive.key && apt-key add /tmp/archive.key; fi \
    && echo "deb [arch=amd64] ${CONFLUENT_PACKAGES_REPO} stable main" >> /etc/apt/sources.list \
    && cat /etc/apt/sources.list \
    && apt-get install -y apt-transport-https \
    && apt-get update \
    && apt-get install -y confluent-${COMPONENT}=${CONFLUENT_VERSION}${CONFLUENT_PLATFORM_LABEL}-${CONFLUENT_DEB_VERSION} \
    confluent-control-center=${CONFLUENT_VERSION}${CONFLUENT_PLATFORM_LABEL}-${CONFLUENT_DEB_VERSION} \
    confluent-security=${CONFLUENT_VERSION}${CONFLUENT_PLATFORM_LABEL}-${CONFLUENT_DEB_VERSION} \
    && echo "===> clean up ..."  \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* \
    && echo "===> Setting up ${COMPONENT} dirs" \
    && chmod -R ag+w /etc/${COMPONENT}

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
