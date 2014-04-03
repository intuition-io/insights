#
# Copyright 2013 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import time
import codecs
import requests
import jinja2
import insights.analysis as analysis
import dna.logging

log = dna.logging.logger(__name__)


#TODO Get some inspiration: http://godoc.org/github.com/riobard/go-mailgun
class Mailgun(object):
    '''
    Send emails through mailgun api
    '''
    _api_url = 'https://api.mailgun.net/v2/{}/messages'
    _api_key = ''

    def __init__(self, friendly_name):
        self._api_key = os.environ.get('MAILGUN_API_KEY')
        domain = os.environ.get('MAILGUN_DOMAIN')
        self.from_email = '{} <me@{}>'.format(friendly_name, domain)
        self._api_url = self._api_url.format(domain)

    def send(self, targets, subject, body, attachment=None):
        if isinstance(targets, str):
            targets = [targets]
        payload = {
            'from': self.from_email,
            'to': targets,
            'subject': subject,
            'html': body
        }
        if attachment:
            # TODO Support multiple attachments
            feedback = requests.post(
                self._api_url,
                files=[('attachment', open(attachment))],
                auth=('api', self._api_key),
                data=payload)
        else:
            feedback = requests.post(
                self._api_url,
                auth=('api', self._api_key),
                data=payload)
        return feedback


# TODO Only if live and add securities anyway
class Report(Mailgun):
    ''' Sent mail reports about the situation '''
    asset_dir = os.path.expanduser('~/.intuition/assets/')
    report_name = 'report.rnw'
    mail_name = 'mail-template.html'

    def __init__(self, targets):
        Mailgun.__init__(self, 'intuition.io')
        self.targets = targets
        self._last_send = time.time()

        self.generator = analysis.Stocks()
        log.info('Mail report ready', recipients=targets)

        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.asset_dir))

    def _render_report_template(self, identity, orderbook, benchmark='GSPC'):
        stocks = []
        for sid, quantity in orderbook.iteritems():
            stocks.append({
                'action': 'Buy' if quantity > 0 else 'Sell',
                'quantity': abs(quantity),
                'name': sid.upper()
            })
        template = self.template_env.get_template(self.report_name + '.j2')
        return template.render(
            strategy_name=identity,
            start_date='2013/11/01',
            benchmark=benchmark,
            orderbook=stocks)

    def _render_email_template(self, identity, orderbook):
        completion = []
        for sid, quantity in orderbook.iteritems():
            completion.append({
                'action': 'Buy' if quantity > 0 else 'Sell',
                'quantity': abs(quantity),
                'equity': sid
                #'reason': 'not implemented'
            })
        template = self.template_env.get_template(self.mail_name + '.j2')
        return template.render(
            strategy_name=identity, suggestions=completion)

    @property
    def is_allowed(self):
        return time.time() - self._last_send > 30.0

    def send_briefing(self, identity, orderbook, portfolio):
        # TODO Portfolio summary
        if orderbook and self.is_allowed:
            self._last_send = time.time()

            log.info('generating report template')
            report = self._render_report_template(
                identity, orderbook)
            fd = codecs.open(
                self.asset_dir + self.report_name, 'w', 'utf-8')
            fd.write(report)
            fd.close()

            self.generator.process()

            feedback = self.send(
                targets=self.targets,
                subject='{} notification'.format(identity),
                body=self._render_email_template(identity, orderbook),
                attachment="report.pdf")
            log.debug(feedback.json())

            self.generator.clean(everything=False)
