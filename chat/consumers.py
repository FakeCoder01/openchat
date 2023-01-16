import json, openai

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

def HandleAPI(q):

    openai.api_key = "API_KEY"

    model_engine = "text-davinci-002"
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
        self.room_group_name = 'test'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
            }
        )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type':'chat',
            'message': HandleAPI(message),
        }))

