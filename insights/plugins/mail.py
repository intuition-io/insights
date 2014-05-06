# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Mail plugin
  -----------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import os
import time
import codecs
import requests
import jinja2
import insights.analysis as analysis
import dna.logging

log = dna.logging.logger(__name__)


# TODO Get some inspiration: http://godoc.org/github.com/riobard/go-mailgun
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
            loader=jinja2.FileSystemLoader(self._asset_dir))

    def _render_report_template(
            self, identity, orderbook, metrics, benchmark='GSPC'):
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
            orderbook=stocks,
            metrics=metrics
        )

    def _render_email_template(self, identity, orderbook):
        completion = []
        for sid, quantity in orderbook.iteritems():
            completion.append({
                'action': 'Buy' if quantity > 0 else 'Sell',
                'quantity': abs(quantity),
                'equity': sid
            })
        template = self.template_env.get_template(self.mail_name + '.j2')
        return template.render(
            strategy_name=identity,
            suggestions=completion
        )

    @property
    def is_allowed(self):
        return time.time() - self._last_send > 30.0

    def send_briefing(self, identity, orderbook, metrics):
        # TODO Portfolio summary
        if orderbook and self.is_allowed:
            self._last_send = time.time()

            # TODO catch errors
            log.info('generating report template')
            report = self._render_report_template(
                identity, orderbook, metrics
            )
            fd = codecs.open(
                self._asset_dir + self.report_name, 'w', 'utf-8')
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
