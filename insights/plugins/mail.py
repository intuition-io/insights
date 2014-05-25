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
import dna.logging
import intuition.data.remote as remote
import insights.analysis as analysis

log = dna.logging.logger(__name__)


def human_sid(symbol):
    sid = remote.lookup_symbol(symbol)
    if len(sid):
        human_fmt = '{} {} - {} ({})'.format(
            sid[0]['name'],
            sid[0]['typeDisp'],
            sid[0]['exchDisp'],
            sid[0]['symbol']
        )
    else:
        human_fmt = symbol

    return human_fmt


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

    def send(self, targets, subject, body, attachments=None):
        attachments = attachments or []
        attachments = [
            ('attachment', open(filename, 'rb')) for filename in attachments
        ]
        if isinstance(targets, str):
            targets = [targets]
        payload = {
            'from': self.from_email,
            'to': targets,
            'subject': subject,
            'html': body
        }
        # TODO Support multiple attachments
        feedback = requests.post(
            self._api_url,
            files=attachments,
            auth=('api', self._api_key),
            data=payload
        )
        return feedback


class Report(Mailgun):
    ''' Sent mail reports about the situation '''

    _assets_dir = os.path.expanduser('~/.intuition/assets/')
    report_name = 'report.rnw'
    mail_name = 'mail-template.html'

    def __init__(self, targets):
        Mailgun.__init__(self, 'intuition.io')
        self.targets = targets
        self._last_send = time.time()

        self.generator = analysis.Stocks()
        log.info('Mail report ready', recipients=targets)

        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self._assets_dir))

    def _render_report_template(
            self, summary, orderbook, metrics, benchmark='FCHI'):
        stocks = []
        for sid, infos in orderbook.iteritems():
            stocks.append({
                'action': 'Buy' if infos['value'] > 0 else 'Sell',
                'quantity': abs(infos['value']),
                'name': sid,
                'symbol': infos['symbol'].upper()
            })
        template = self.template_env.get_template(self.report_name + '.j2')
        return template.render(
            summary=summary,
            start_date='2013/11/01',
            benchmark=benchmark,
            orderbook=stocks,
            metrics=metrics
        )

    def _render_email_template(self, identity, orderbook):
        completion = []
        for sid, infos in orderbook.iteritems():
            completion.append({
                'action': 'Buy' if infos['value'] > 0 else 'Sell',
                'quantity': abs(infos['value']),
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

    def send_briefing(
            self, __class__, manager, identity, orderbook, perf_tracker):
        # TODO Portfolio summary
        if orderbook and self.is_allowed:
            self._last_send = time.time()
            identity = identity.capitalize()
            orderbook = {
                human_sid(sid): {'symbol': sid, 'value': value}
                for sid, value in orderbook.iteritems()
            }

            # TODO __class__ output is not friendly
            summary = {
                'identity': identity,
                'algorithm': __class__.__name__,
                'manager': manager.__class__.__name__ if manager else None
            }
            log.info('generating report template')
            # TODO catch errors
            report = self._render_report_template(
                summary, orderbook, perf_tracker
            )
            fd = codecs.open(
                self._assets_dir + self.report_name, 'w', 'utf-8'
            )
            fd.write(report)
            fd.close()

            self.generator.process()

            feedback = self.send(
                targets=self.targets,
                subject='{} notification'.format(identity),
                body=self._render_email_template(identity, orderbook),
                attachments=[
                    self._assets_dir + 'legal_notice.txt',
                    'report.pdf'
                ]
            )
            log.debug(feedback.json())

            self.generator.clean(everything=False)
