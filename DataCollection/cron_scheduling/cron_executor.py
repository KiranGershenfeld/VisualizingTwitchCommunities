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
import logging
from subprocess import PIPE, Popen
import sys
import threading
import time

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

from apiclient import discovery
from apiclient.errors import HttpError
import httplib2
from oauth2client.client import GoogleCredentials

log = logging.getLogger(__name__)

PUBSUB_SCOPES = ["https://www.googleapis.com/auth/pubsub"]


class AsynchronousFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    '''

    def __init__(self, fd, queue):
        assert isinstance(queue, Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        '''The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            self._queue.put(line)

    def eof(self):
        '''Check whether there is no more content to expect.'''
        return not self.is_alive() and self._queue.empty()


def get_client():
    """Creates Pub/Sub client and returns it."""
    credentials = GoogleCredentials.get_application_default()
    credentials = credentials.create_scoped(PUBSUB_SCOPES)
    http = httplib2.Http()
    credentials.authorize(http)
    return discovery.build('pubsub', 'v1beta2', http=http)


class Executor():
    def __init__(self,
                 topic='mytopic',
                 project='myproject',
                 subname='default_sub',
                 task_cmd="sleep 20",
                 deadline=60):
        self.topic = topic
        self.project = project
        self.subname = "%s_%s" % (topic, subname)
        self.task_cmd = task_cmd
        self.client = get_client()
        self.sub = self.get_subscription(deadline=deadline)
        self.ackdeadline = self.sub['ackDeadlineSeconds']
        self.io_queue = Queue()
        self.lease_start = None
        self.job_log = logging.getLogger(self.subname)

    def create_subscription(self, deadline=60):
        log.debug("creating subscription")
        body = {
            # The name of the topic from which this subscription receives messages
            'topic': 'projects/{}/topics/{}'.format(self.project, self.topic),
            'ackDeadlineSeconds': deadline
        }

        try:
            subscription = self.client.projects().subscriptions().create(
                name='projects/{}/subscriptions/{}'.format(self.project,
                                                           self.subname),
                body=body).execute()
        except Exception as e:
            log.critical("unable to create subscription")
            raise

        return subscription

    def get_subscription(self, deadline=60):
        sub = None
        log.debug("getting subscription")
        try:
            # note: subscriptions are a flat namespace in a project
            # we delete then recreate the subscription if it exists
            # so we don't execute old messages

            self.client.projects().subscriptions().delete(
                subscription='projects/{}/subscriptions/{}'.format(
                    self.project, self.subname)).execute()
            log.debug("deleted existing subscription")
        except HttpError as e:
            if e.resp.status == 404:
                sub = self.create_subscription(deadline=deadline)
            else:
                raise
        else:
            sub = self.create_subscription(deadline=deadline)
        log.debug("subscription %s" % sub)
        return sub

    def get_messages(self):
        # You can fetch multiple messages with a single API call.
        batch_size = 1

        # Create a POST body for the Pub/Sub request
        body = {
            # Setting ReturnImmediately to false instructs the API to wait
            # to collect the message up to the size of MaxEvents, or until
            # the timeout (approx 90s)
            'returnImmediately': False,
            'maxMessages': batch_size,
        }
        log.debug("pulling messages")
        resp = self.client.projects().subscriptions().pull(
            subscription=self.sub['name'],
            body=body).execute()
        if 'receivedMessages' in resp:
            log.debug("number msgs: %s" % len(resp.get('receivedMessages')))
            self.lease_start = datetime.now()
            return resp.get('receivedMessages')
        else:
            return []

    def extend_lease(self, msg):
        body = {
            'ackIds': [msg['ackId']],
            'ackDeadlineSeconds': self.ackdeadline,
        }
        resp = self.client.projects().subscriptions().modifyAckDeadline(
            subscription=self.sub['name'],
            body=body).execute()
        return resp

    def run_task(self, msg):
        proc = Popen(self.task_cmd, stdout=PIPE, shell=True)
        stdout_reader = AsynchronousFileReader(proc.stdout, self.io_queue)
        stdout_reader.start()
        while not stdout_reader.eof():
            # read line without blocking
            while True:
                try:
                    # line = self.io_queue.get_nowait() # or q.get(timeout=.1)
                    line = self.io_queue.get_nowait()  # could do timeout=.1
                except Empty:
                    break
                else:
                    self.job_log.info(line)

            lease_age = datetime.now() - self.lease_start
            if lease_age.seconds > (self.ackdeadline - 20):
                # 10 seconds left in lease, renew
                log.debug("extending lease")
                try:
                    resp = self.extend_lease(msg)
                    self.extend_error_ct = 0
                    self.lease_start = datetime.now()
                except HttpError as e:
                    if e.resp.status == 503:
                        # service might return intermitant 503
                        log.warning("PubSub returned 503")
                        self.extend_error_ct += 1
                        if self.extend_error_ct > 5:
                            log.critical(
                                "Too many error responses to extend request")
                            raise
            time.sleep(1)

        retcode = proc.poll()
        if retcode is not None:
            # TODO if error - expire lease immediately?
            # process exited
            log.debug("process ended")
        return retcode

    def process_messages(self, msgs):
        for received_message in msgs:
            pubsub_message = received_message.get('message')
            log.debug("processing %s" % received_message.get('ackId'))
            if pubsub_message:
                ack_ids = []
                # Process messages
                # Note the design here is to run a single task at a time
                # print base64.urlsafe_b64decode(
                # str(pubsub_message.get('data')))
                # Get the message's ack ID
                cmd_retcode = self.run_task(received_message)
                # TODO if cmd_retcode == 0, the cmd exited clean
                # the retry logic could get complex and is left as an exercise
                ack_ids.append(received_message.get('ackId'))
                # in this case - should ack per message instead of batch
                # as want to make sure task is acked after completion, as
                # nothing else will extend
                # Create a POST body for the acknowledge request
                ack_body = {'ackIds': ack_ids}
                if ack_ids:
                    # Acknowledge the message.
                    log.debug("acking %s" % ack_ids)
                    ack_resp = self.client.projects().subscriptions().acknowledge(
                        subscription=self.sub['name'],
                        body=ack_body).execute()

    def watch_topic(self):
        while True:
            msgs = self.get_messages()
            if msgs:
                self.process_messages(msgs)
            # when return immediately is False-  there is about a 90second open
            # request
