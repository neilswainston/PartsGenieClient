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
from sbol import Config, Document, Sequence, SBOL_ENCODING_IUPAC
from sseclient import SSEClient


Config.setOption('validate', False)


class PartsGenieClient():
    '''PartsGenieClient class.'''

    def __init__(self, url='https://parts.synbiochem.co.uk'):
        self.__url = url if url[-1] == '/' else url + '/'

    def run(self, filename, taxonomy_id, out_dir):
        '''Run client.'''
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        job_ids = self.__run_parts_genie(filename, taxonomy_id)

        results = {}

        for job_id in job_ids:
            if job_id not in results:
                response = self.__get_progress(job_id)

                if response[0][0][0] == 'finished':
                    results.update({res['desc']: res
                                    for res in response[0][1]['result']})
                else:
                    raise Exception(job_id)

        _update_docs(filename, results, out_dir)

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


def _update_docs(filename, results, out_dir):
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

    doc.write(os.path.join(out_dir, os.path.basename(filename)))


def main(args):
    '''main method.'''
    client = PartsGenieClient(args[0])
    client.run(args[1], args[2], args[3])


if __name__ == '__main__':
    main(sys.argv[1:])
