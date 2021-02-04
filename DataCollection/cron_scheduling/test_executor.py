#!/usr/bin/env python

# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

This sample script shows how to use the reusable Executor utility to
watch a topic and execute a command when a message is received

"""
"""
This script needs python2 while the rest of my project uses python3. This is a pain
but this came directly from google's sample projects and I couldn't find any other way
to schedule cron jobs on google cloud vms. If you actually want to get this part working automatically
open an issue on the VisualizingTwitchCommunities github so I can help. This was originally published
here: https://github.com/GoogleCloudPlatform/reliable-task-scheduling-compute-engine-sample
"""
import logging
import os
import sys
import Credentials as cr #--IMPORTANT-- This line imports PROJECT, TOPIC, and script_path because those values are specific to my project and should be changed by each individual
from cloud_handler import CloudLoggingHandler
from cron_executor import Executor

PROJECT = cr.PROJECT  # change this to match your project
TOPIC = cr.TOPIC

script_path = cr.script_path

sample_task = "python3 %s" % script_path


root_logger = logging.getLogger('cron_executor')
root_logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stderr)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root_logger.addHandler(ch)

cloud_handler = CloudLoggingHandler(on_gce=True, logname="task_runner")
root_logger.addHandler(cloud_handler)

# create the executor that watches the topic, and will run the job task
test_executor = Executor(topic=TOPIC, project=PROJECT, task_cmd=sample_task)

# add a cloud logging handler and stderr logging handler
job_cloud_handler = CloudLoggingHandler(on_gce=True, logname=test_executor.subname)
test_executor.job_log.addHandler(job_cloud_handler)
test_executor.job_log.addHandler(ch)
test_executor.job_log.setLevel(logging.DEBUG)


# watches indefinitely
test_executor.watch_topic()
