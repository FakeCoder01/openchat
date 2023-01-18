import json, openai
from urllib.parse import parse_qsl
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from .models import Message, Profile

def HandleAPI(q):
    openai.api_key = "API-KEY"

    model_engine = "text-davinci-003"
    req = openai.Completion.create(
        engine=model_engine, 
        prompt=str(q), 
        max_tokens=200, 
        n=1, 
        stop=None, 
        temperature=0
    )
    response = str(req.choices[0].text)
    response = response.replace("\n", "<br>")

    return response




class ChatConsumer(WebsocketConsumer):

    def connect(self):
        query_params = dict(parse_qsl(self.scope['query_string'].decode('utf-8')))
        group = str(query_params['room_id'])
        self.room_group_name = group

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sent_by = text_data_json['sent_by']
        user = text_data_json['user']
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'chat_message',
                'message': message,
                'sent_by' : sent_by

            }
        )
        
        

    def chat_message(self, event):
        message = event['message']
        sent_by = event['sent_by']
        user = event['user']

        self.send(text_data=json.dumps({
            'type':'chat',
            'message': message,
            'sent_by' : sent_by
        }))  

        if sent_by == 'user':
            txt = HandleAPI(message)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type':'chat_message',
                    'message': txt,
                    'sent_by' : 'chat-gpt'
                }
            )
