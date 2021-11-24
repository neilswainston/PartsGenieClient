'''
PartsGenieClient (c) University of Liverpool. 2019

PartsGenieClient is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
import json
import os.path
import sys

import requests
from .sbol import Config, Document, Sequence, SBOL_ENCODING_IUPAC
from sseclient import SSEClient


Config.setOption('validate', False)


class PartsGenieError(Exception):
    '''PartsGenieError class.'''

    def __init__(self, job_id, cause):
        self.__job_id = job_id
        self.__cause = cause
        super(PartsGenieError, self).__init__(str(cause))

    def get_job_id(self):
        '''Get job id.'''
        return self.__job_id

    def get_cause(self):
        '''Get cause.'''
        return self.__cause

    def __repr__(self):
        return str({'job_id': self.__job_id, 'cause': self.__cause})


class PartsGenieClient():
    '''PartsGenieClient class.'''

    def __init__(self, url):
        self.__url = url if url[-1] == '/' else url + '/'

    def run(self, filename, taxonomy_id, outfile):
        '''Run client.'''
        job_ids = self.__run_parts_genie(filename, taxonomy_id)

        results = {}

        for job_id in job_ids:
            if job_id not in results:
                response = self.__get_progress(job_id)

                if response[0][0][0] == 'finished':
                    results.update({res['desc']: res
                                    for res in response[0][1]['result']})
                else:
                    self.__raise_error(job_id, response, job_ids, results)

        _update_docs(filename, results, outfile)

    def __run_parts_genie(self, filename, taxonomy_id):
        '''Run PartsGenie.'''
        url = self.__url + 'submit_sbol'

        with open(filename, 'rb') as fle:
            files = [('sbol', fle)]
            resp = requests.post(url,
                                 data={'taxonomy_id': taxonomy_id},
                                 files=files)
            resp_json = json.loads(resp.text)
            return resp_json['job_ids']

    def __get_progress(self, job_id):
        '''Get progress.'''
        responses = []
        messages = SSEClient(self.__url + 'progress/' + job_id)
        status = [None, None, float('NaN')]

        for msg in messages:
            resp = json.loads(msg.data)
            update = resp['update']
            updated_status = [update['status'], update['message'],
                              update['progress']]

            if updated_status != status:
                status = updated_status

                if status[0] != 'running':
                    responses.append([status, resp])
                    break

        return responses

    def __raise_error(self, error_job_id, response, job_ids, results):
        '''Raise error.'''
        try:
            for job_id in job_ids:
                if job_id != error_job_id and job_id not in results:
                    # Cancel outstanding jobs on PartsGenie:
                    url = self.__url + 'cancel/' + job_id
                    requests.get(url)
        finally:
            raise PartsGenieError(error_job_id, response[0][1])


def _update_docs(filename, results, outfile):
    '''Update documents.'''
    doc = Document()
    doc.read(filename)

    for gene_uri, result in results.items():
        # Get gene definition:
        gene_def = doc.getComponentDefinition(gene_uri)
        seq = ''

        # Iterate through sub component definitions:
        for comp_def in [doc.getComponentDefinition(c.definition)
                         for c in gene_def.components]:
            # Update sub component sequence if not already set:
            if not comp_def.sequence:
                feature = [f for f in result['features']
                           if f['name'] == comp_def.identity][0]

                subseq = feature['seq']

                comp_def.sequence = \
                    Sequence('%s_seq' % comp_def.displayId,
                             subseq,
                             SBOL_ENCODING_IUPAC)
            else:
                subseq = comp_def.sequence.elements

            seq += subseq

        gene_def.sequence = \
            Sequence('%s_seq' % gene_def.displayId,
                     seq,
                     SBOL_ENCODING_IUPAC)

    doc.write(outfile)
