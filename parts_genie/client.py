'''
PartsGenieClient (c) University of Manchester. 2018

PartsGenieClient is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=relative-import
# pylint: disable=superfluous-parens
# pylint: disable=wrong-import-order
import json
import os
import sys

from six.moves.urllib import request
from sseclient import SSEClient
from synbiochem.utils import net_utils


class PlasmidGenieClient(object):
    '''PlasmidGenieClient class.'''

    def __init__(self, ice_params, url='https://parts.synbiochem.co.uk'):
        self.__ice_params = ice_params
        self.__url = url if url[-1] == '/' else url + '/'

    def run(self, in_filename, restr_enzs, melt_temp=70.0,
            circular=True, out_filename='export.zip'):
        '''Run client.'''
        plas_gen_result = self.__run_plasmid_genie(in_filename, restr_enzs,
                                                   melt_temp, circular)

        save_result = self.__run_save(plas_gen_result)
        export_result = self.__run_export(save_result)

        self.__save_export(export_result['path'], out_filename)

    def __run_plasmid_genie(self, filename, restr_enzs, melt_temp, circular):
        '''Run PlasmidGenie.'''
        query = self.__get_plasmid_genie_query(filename, restr_enzs,
                                               melt_temp, circular)
        responses = self.__run_query(query)

        return responses[0][1]['result'] \
            if responses[0][0][0] == 'finished' else None

    def __run_save(self, result):
        '''Save PlasmidGenie result to ICE.'''
        query = self.__get_result_query(result)
        response = self.__run_query(query)

        for res, ice_ids in zip(result, response[0][1]['result']):
            res['ice_ids'] = ice_ids

        return result

    def __run_export(self, designs):
        '''Run export method to receive list of components.'''
        query = self.__get_result_query(designs)
        return self. __get_response('export', query)

    def __run_query(self, query):
        '''Run query.'''
        resp = self.__get_response('submit', query)

        job_id = resp['job_ids'][0]
        return self.__get_progress(job_id)

    def __get_response(self, method, query):
        '''Get response.'''
        headers = {'Accept': 'application/json, text/plain, */*',
                   'Accept-Language': 'en-gb',
                   'Content-Type': 'application/json;charset=UTF-8'}

        return json.loads(net_utils.post(self.__url + method,
                                         json.dumps(query),
                                         headers))

    def __get_plasmid_genie_query(self, filename, restr_enzs, melt_temp,
                                  circular):
        '''Return query.'''
        query = {u'designs': _get_designs(filename),
                 u'app': 'PlasmidGenie',
                 u'ice': self.__ice_params,
                 u'design_id': _get_design_id(filename),
                 u'restr_enzs': restr_enzs,
                 u'melt_temp': melt_temp,
                 u'circular': circular}

        return query

    def __get_result_query(self, designs):
        '''Return query.'''
        query = {u'designs': designs,
                 u'app': 'save',
                 u'ice': self.__ice_params}

        return query

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
                print('\t'.join([str(val) for val in status]))

                if status[0] != 'running':
                    responses.append([status, resp])
                    break

        return responses

    def __save_export(self, path, out_filename):
        '''Save export result.'''
        request.urlretrieve(self.__url + path, out_filename)
        print('Exported to ' + out_filename)


def _get_design_id(filename):
    '''Get design id.'''
    _, tail = os.path.split(filename)
    return os.path.splitext(tail)[0]


def _get_designs(filename):
    '''Get designs.'''
    designs = []

    with open(filename, 'rU') as fle:
        for line in fle:
            tokens = line.split()
            designs.append({'name': tokens[0], 'design': tokens[1:]})

    return designs


def main(args):
    '''main method.'''
    ice_params = {u'url': args[0],
                  u'username': args[1],
                  u'password': args[2],
                  u'groups': args[3]}

    client = PlasmidGenieClient(ice_params)
    client.run(in_filename=args[4], out_filename=args[5], restr_enzs=args[6:])


if __name__ == '__main__':
    main(sys.argv[1:])
