import sys
sys.path.insert(0, 'vendor')

import os
import requests
import random
import json


API_ROOT = 'https://api.groupme.com/v3/'
FLAGGED_PHRASES = (
    'essay written by professionals',
    'paper writing service',
    'academic writing service',
    'student paper assignments',
    'getting professional academic help from us is easy',
    'cutt.us',
    'inyurl.com/muxz7h',
    'u.to/xavt',
    'we write your papers',
    'best in the writing service industry',
    'side job offer for you which',
    'getting $1000 within week',
    'lost my daughter to cancer about a week ago,she was',
    'to cancer about a week ago',
    'play station 5',
    'ps5',
    'ticket',
    'tickets',
    'essay writer',
    'super writer',
    'cute writer',
    'hentai',
)


def get_memberships(group_id, token):
    response = requests.get(f'{API_ROOT}groups/{group_id}', params={'token': token}).json()['response']['members']
    return response
            
def get_membership_id_and_admin_status(group_id, user_id, token):
    memberships = get_memberships(group_id, token)
    for membership in memberships:
        if membership['user_id'] == user_id:
            return membership['id'], membership.get('admin', False)

def remove_member(group_id, membership_id, token):
    response = requests.post(f'{API_ROOT}groups/{group_id}/members/{membership_id}/remove', params={'token': token})
    print('Tried to kick user, got response:')
    print(response.text)
    return response.ok


def delete_message(group_id, message_id, token):
    response = requests.delete(f'{API_ROOT}conversations/{group_id}/messages/{message_id}', params={'token': token})
    return response.ok


def kick_user(group_id, user_id, token):
    membership_id, _ = get_membership_id_and_admin_status(group_id, user_id, token)
    remove_member(group_id, membership_id, token)



def receive(event, context):
    message = json.loads(event['body'])

    bot_id = message['bot_id']
    for phrase in FLAGGED_PHRASES:
        if phrase in message['text'].lower():
            membership_id, is_admin = get_membership_id_and_admin_status(message['group_id'], message['user_id'], message['token'])
            # Proceed with actions only if the user is not an admin
            if not is_admin:
                kick_user(message['group_id'], message['user_id'], message['token'])
                delete_message(message['group_id'], message['id'], message['token'])
                send('Kicked ' + message['name'] + ' due to apparent spam post.', bot_id)
            break

    return {
        'statusCode': 200,
        'body': 'ok'
    }



def send(text, bot_id):
    url = 'https://api.groupme.com/v3/bots/post'

    message = {
        'bot_id': bot_id,
        'text': text,
    }
    r = requests.post(url, json=message)
