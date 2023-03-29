import json, os
from urllib.parse import parse_qsl
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from gpt_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI

os.environ["OPENAI_API_KEY"] = "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"

def construct_index(directory_path):
    max_input_size = 4096
    num_outputs = 256
    max_chunk_overlap = 20
    chunk_size_limit = 600

    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=num_outputs))
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
 
    documents = SimpleDirectoryReader(directory_path).load_data()
    
    index = GPTSimpleVectorIndex(
        documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper
    )

    index.save_to_disk('index.json')
    return index

def ask_lenny(query):
    
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    while True: 
        response = index.query(query, response_mode="compact")
        return response.response
    
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
            txt = ask_lenny(message)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type':'chat_message',
                    'message': txt,
                    'sent_by' : 'chat-gpt'
                }
            )
