"""
This sample demonstrates an implementation of the Lex Code Hook Interface in Lambda.

For instructions on how to set up, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
import decimal
import json
import re
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate_pet_license_info(zipCode):
    print("ZIP is "+str(zipCode))
    
    if zipCode is not None:
        if len(zipCode) != 5:
            # Not a valid zip; use a prompt defined on the build-time model.
            return build_validation_result(False, 'zipCode', 'That zip code does not seem to have the right number of digits. Can you try again?')

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """


def get_pet_license_cost(intent_request):
    """
    Performs lookup of cost to license your pet based on your zip code.
    """

    zipCode = get_slots(intent_request)["zipCode"]
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_pet_license_info(zipCode)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])


        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        
        return delegate(output_session_attributes, get_slots(intent_request))
    
    zipCode_Formatted = zipCode
    if intent_request['bot']['alias'] == 'demo_Connect':
        zipCode_Formatted = " ".join(zipCode)

    if zipCode=="90210":
        fulfillmentResponse = "The pet license fee for zip "+zipCode_Formatted+" is $60"
        return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': fulfillmentResponse})
    else:
        fulfillmentResponse = "The pet license fee for zip "+zipCode_Formatted+" is $35"
        return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': fulfillmentResponse})


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
    logger.debug('alias={}'.format(intent_request['bot']['alias']))


    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'LookupLicenseCost':
        return get_pet_license_cost(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/Los_Angeles time zone.
    os.environ['TZ'] = 'America/Los_Angeles'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    print(json.dumps(event));

    return dispatch(event)


""" --- Helper functions --- """

def insert_dash(string, index):
    return string[:index] + '-' + string[index:]

def insert_char(string, index, char):
    return string[:index] + char + string[index:]

def get_num(x):
    return float(''.join(ele for ele in x if ele.isdigit() or ele == '.'))