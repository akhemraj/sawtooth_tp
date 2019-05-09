'''
Transaction family class for Document storage onm blockchain.
'''

import traceback
import sys
import hashlib
import logging
import ast

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

LOGGER = logging.getLogger(__name__)
FAMILY_NAME = "document_store"


def _hash(data):
    '''Compute the SHA-512 hash and return the result as hex characters.'''
    return hashlib.sha512(data).hexdigest()

# Prefix for document store is the first six hex digits of SHA-512(TF name).
ds_namespace = _hash(FAMILY_NAME.encode('utf-8'))[0:6]

class DocumentStoreTransactionHandler(TransactionHandler):
    '''
    Transaction Processor class for document storage family
    It includes functions like storing documents using the validator.
    ''' 

    def __init__(self,namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [self._namespace_prefix]
    
    def apply(self,transaction,context):
        '''
        This function is used to process  single transaction completely.
        '''
        header = transaction.header
        signer = header.signer_public_key

        # Get the payload and extract simplewallet-specific information.
        doc_payload_list = transaction.payload.decode().split(',')
        operation = doc_payload_list[0]
        hash_value = doc_payload_list[1]

        # Get the public key sent from the client.
        user_key = header.signer_public_key

        #perform the operation
        LOGGER.info("operation = "+operation)

        if(operation == 'store'):
            self._do_Store(context,hash_value,user_key)
        else:
            LOGGER.info("Unhandled operation. "+"Operation should be Store ")
    
    def _do_Store(self,context,hash_value,user_key):
        user_address = self._get_user_address(user_key)
        LOGGER.info('got the key from {} with the address {}'.format(user_key,user_address))

        state_data = str(hash_value).encode('utf-8')
        addresses = context.set_state({user_address:state_data}) 
        if len(addresses) < 1:
            raise InternalError("State Error")

    def _get_user_address(self,user_key):
        return _hash(FAMILY_NAME.encode('utf-8'))[0:6] + _hash(user_key.encode('utf-8'))[0:64]
def setup_loggers():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

def main():
    '''Entry point function for document store transaction processor.'''
    setup_loggers()
    try:
        # Register the transaction handler and start it.
        processor = TransactionProcessor(url='tcp://localhost:4004')   

        handler = DocumentStoreTransactionHandler(ds_namespace)

        processor.add_handler(handler)

        processor.start()

    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1) 

