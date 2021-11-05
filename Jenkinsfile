#!/usr/bin/env groovy

dockerfile {
    dockerPush = true
    dockerRepos = ['confluentinc/cp-kafka-rest',]
    mvnPhase = 'package'
    mvnSkipDeploy = true
    nodeLabel = 'docker-debian-jdk8-compose'
    slackChannel = '#rest-proxy-warn'
    upstreamProjects = []
    dockerPullDeps = ['confluentinc/cp-base-new']
    usePackages = true
    cron = '' // Disable the cron because this job requires parameters
    cpImages = true
    osTypes = ['deb8', 'ubi8']
    disableConcurrentBuilds = true
}
