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

from datetime import datetime
import json
import logging
import sys
from threading import Thread

from apiclient import discovery

import httplib2
import oauth2client.contrib.gce as gce_oauth2client

LOGGING_SCOPES = ["https://www.googleapis.com/auth/logging.admin",
                  "https://www.googleapis.com/auth/cloud-platform"]
METADATA_SERVER = 'http://metadata/computeMetadata/v1/%s'

SEVERITY = {
    0: "DEFAULT",
    10: "DEBUG",
    20: "INFO",
    25: "NOTICE",
    30: "WARNING",
    40: "ERROR",
    50: "CRITICAL",
    60: "ALERT",
    70: "EMERGENCY",
}


class CloudLoggingHandler(logging.Handler):
    """
    A python logging handler that emits to Google Cloud Logging

    NOTE this is for demo purposes only, do not use on high volume production
    services.
    """

    def __init__(self,
                 credentials=None,
                 logname='python',
                 labels={},
                 project_id=None,
                 on_gce=False,
                 async=True):

        super(CloudLoggingHandler, self).__init__()

        self.main_http = http = httplib2.Http()
        if not credentials:
            if not on_gce:
                raise ValueError(
                    "credentials need to be provided if not on running on GCE")
            else:
                credentials = gce_oauth2client.AppAssertionCredentials(
                    scope=LOGGING_SCOPES)
        if project_id is None:
            if not on_gce:
                raise ValueError(
                    "project_id needs to be provided if not running on GCE")
            else:
                resp, self.project_id = http.request(
                    METADATA_SERVER % "project/project-id",
                    method='GET',
                    body=None,
                    headers={'Metadata-Flavor': 'Google'})
        else:
            self.project_id = project_id

        if not on_gce:
            # The following are placeholder values
            self.instance_id = '12345'
            self.zone = 'us-central1-a'
        else:
            resp, self.zone = http.request(
                METADATA_SERVER % "instance/zone",
                method='GET',
                body=None,
                headers={'Metadata-Flavor': 'Google'})

            self.zone = self.zone.decode('UTF-8').split('/')[-1]
            resp, self.instance_id = http.request(
                METADATA_SERVER % "instance/id",
                method='GET',
                body=None,
                headers={'Metadata-Flavor': 'Google'})

        credentials = credentials.create_scoped(LOGGING_SCOPES)
        credentials.authorize(http)
        self.credentials = credentials
        self.async = async
        self.client = discovery.build("logging", "v1beta3", http=http)
        self.logname = logname
        self.labels = labels
        self.labels["compute.googleapis.com/resource_id"] = self.instance_id
        self.labels["compute.googleapis.com/resource_type"] = 'instance'

    def write_log(self, record):
        if self.async:
            http = httplib2.Http()
            self.credentials.authorize(http)
        else:
            http = self.main_http

        msg = self.format(record)
        entry_metadata = {
            "timestamp": "2015-03-25T10:20:50.52Z",
            "region": "us-central1",
            "zone": "us-central1-a",
            "serviceName": "compute.googleapis.com",
            "severity": "CRITICAL",
            "labels": {}
        }
        entry_metadata['timestamp'] = "%sZ" % datetime.utcfromtimestamp(
            record.created).isoformat()
        # min(range(len(levels)), key=lambda i: abs(levels[i]-loglevel))
        entry_metadata['severity'] = SEVERITY[min(SEVERITY.keys(),
                                                  key=lambda i:
                                                  abs(record.levelno - i))]
        entry_metadata['zone'] = self.zone
        entry_metadata['region'] = '-'.join(self.zone.split('-')[:-1])
        # note - labels are searchable, but not visible in UI
        entry_metadata['labels'] = {
            'module': record.module,
            'funcName': record.funcName,
            'filename': record.filename,
            'name': record.name,
        }

        body = {
            "commonLabels": self.labels,
            "entries": [{"metadata": entry_metadata,
                         "log": self.logname, }]
        }

        if isinstance(record.msg, dict):
            # TODO - not working as expected
            raise NotImplementedError(
                "structured logs not supported in this version")
        else:
            body['entries'][0]['textPayload'] = msg

        try:
            resp = self.client.projects().logs().entries().write(
                projectsId=self.project_id,
                logsId=self.logname,
                body=body).execute(http=http)
            if resp:
                # this would be an error
                sys.stderr.write(resp + '\n')
        except Exception as e:
            sys.stderr.write(e.message + '\n')

    def emit(self, record):
        if self.async:
            # send the logging event to logging service in a thread so
            # main program is not blocked
            http_writer = Thread(target=self.write_log, args=(record, ))
            http_writer.start()
            return
        else:
            self.write_log(record)
            return
