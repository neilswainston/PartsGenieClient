'''
PartsGenieClient (c) University of Manchester. 2018

PartsGenieClient is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
# pylint: disable=too-few-public-methods
import json
import sys
import requests
from sseclient import SSEClient


class PartsGenieClient():
    '''PartsGenieClient class.'''

    def __init__(self, url='https://parts.synbiochem.co.uk'):
        self.__url = url if url[-1] == '/' else url + '/'

    def run(self, filenames, out_dir):
        '''Run client.'''
        job_ids = self.__run_parts_genie(filenames)
        print(job_ids)

        results = {}

        for job_id in job_ids:
            if job_id not in results:
                response = self.__get_progress(job_id)

                if response[0][0][0] == 'finished':
                    results.update({res['desc']: res['seq']
                                    for res in response[0][1]['result']})
                else:
                    raise Exception(job_id)

        print(results)

    def __run_parts_genie(self, filenames):
        '''Run PartsGenie.'''
        url = self.__url + 'submit_sbol'

        files = [('sbol', open(filename, 'rb'))
                 for filename in filenames]

        resp = requests.post(url, files=files)
        resp_json = json.loads(resp.text)

        print(resp_json)

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
                print('\t'.join([job_id] + [str(val) for val in status]))

                if status[0] != 'running':
                    responses.append([status, resp])
                    break

        return responses


def main(args):
    '''main method.'''
    client = PartsGenieClient(url='http://0.0.0.0:5000/')
    client.run(args[1:], args[0])


if __name__ == '__main__':
    main(sys.argv[1:])
