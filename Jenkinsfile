#!/usr/bin/env groovy

dockerfile {
    dockerPush = true
    dockerRepos = ['confluentinc/cp-kafka-rest',]
    mvnPhase = 'package'
    mvnSkipDeploy = true
    nodeLabel = 'docker-oraclejdk8-compose-swarm'
    slackChannel = 'connect-notification'
    upstreamProjects = []
    dockerPullDeps = ['confluentinc/cp-base']
    usePackages = true
    cron = '' // Disable the cron because this job requires parameters
}
