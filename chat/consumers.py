import json, openai
from urllib.parse import parse_qsl
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Message, Profile
from PyPDF2 import PdfReader
import base64, os, uuid

def PdfToTextConvert(pdfile):
    reader = PdfReader(pdfile)
    pdfText = ""
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        text = page.extract_text()
        pdfText += text
    print(pdfText)    
    return pdfText




def HandleAPI(q):
    openai.api_key = "API_KEY"

    model_engine = "text-davinci-003"
    req = openai.Completion.create(
        engine=model_engine, 
        prompt=str(q), 
        max_tokens=2000, 
        n=1, 
        stop=None, 
        temperature=0
    )
    response = str(req.choices[0].text)
    response = response.replace("\n", "<br>")
    # print(response)
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
        data = json.loads(text_data)
        message = data['message']
        sent_by = data['sent_by']

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
        # user = event['user']

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
