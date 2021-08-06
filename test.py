from __future__ import print_function
from __future__ import unicode_literals
import youtube_dl

import os.path
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
import mimetypes
import base64
from apiclient import errors

import json


def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode()}

def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    # print 'Message Id: %s' % message['id']
    print (f'Message Id: {message["id"]}')
    return message
  except errors.HttpError as error:
    # print 'An error occurred: %s' % error
    print (f'An error occurred: {error}')
    return None

def delete_message(messageId):
    try:
        service.users().messages().delete(userId='me', id=messageId).execute()
    except:
        print('Message not found!')


def read_unread_messages():
    ret = []
    query = (service.users().messages().list(userId='me',q='in:inbox is:unread subject:DEEZER/SPLEETER 2-stems').execute())
    if 'messages' in query:
      messages = query['messages']
      if(messages):
          for m in messages:
              id = m['id']
              retM = service.users().messages().get(userId='me', id=id).execute()
              size = retM['payload']['body']['size']

              if(size > 0):
                  data = retM['payload']['body']['data']
              else:
                  data = retM['payload']['parts'][0]['body']['data']

              dataStr = base64.urlsafe_b64decode(data).decode()
              parsed = json.loads(dataStr, strict=False)

              item = {
                  'id': id,
                  'youtubeURL': parsed['youtubeURL'],
                  'email': parsed['email']
              }

              ret.append( item )

    return ret




def download_audio(youtubeURL):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': "audio_sample.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }]
    }
# '-f' bestaudio -x --audio-format mp3}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtubeURL])

def search_messages(service, query):
    result = service.users().messages().list(userId='me',q=query).execute()
    messages = [ ]
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages


credentials_dict = json.loads(os.environ['CREDENTIALS'])

SCOPES = ['https://mail.google.com/']

creds = None

creds = Credentials(
    credentials_dict["token"],
    refresh_token = credentials_dict["refresh_token"],
    token_uri = credentials_dict["token_uri"],
    client_id = credentials_dict["client_id"],
    client_secret = credentials_dict["client_secret"],
    scopes = credentials_dict["scopes"])

if not creds or not creds.valid:
    print("será que vai funcionar o próximo refresh?")

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        print("Bau bau!")
    # with open('token.json', 'w') as token:
    #     token.write(creds.to_json())

service = build('gmail', 'v1', credentials=creds)


msg = create_message('me', 'diogo.alves@gmail.com', 'DEEZER/SPLEETER 2-stems', '''{
  "youtubeURL": "https://www.youtube.com/watch?v=O1iVlFSdoTw",
  "email": "diogo.alves@gmail.com"
}''' )
send_message(service, 'me', msg)
