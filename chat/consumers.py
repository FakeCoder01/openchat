import json, os, platform, faiss, langchain, openai
from urllib.parse import parse_qsl
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from gpt_index import GPTSimpleVectorIndex
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from .models import ChatHistory

from langchain.llms import OpenAI


os.environ['OPENAI_API_KEY'] = "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"
def ask_lenny(query, room_id):
    try:
        chat_history_qs = ChatHistory.objects.filter(user_id=room_id)
        chat_history = [(str(ch.question), str(ch.chat_history)) for ch in chat_history_qs]
    except:
        chat_history = []

    save_directory = f"faiss-data/{room_id}/"
    embeddings = OpenAIEmbeddings()
    vectordb = FAISS.load_local(save_directory, embeddings)
    qa = ConversationalRetrievalChain.from_llm(llm = OpenAI(temperature = 0), retriever = vectordb.as_retriever())
    result = qa({"question": query, "chat_history" : chat_history})
    ChatHistory.objects.create(user_id=room_id, question=query, chat_history=result["answer"])
    return result["answer"]

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
        room_id = data['room_id']
        book = data['book']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'chat_message',
                'message': message,
                'sent_by' : sent_by,
                'room_id' : room_id,
                'book' : book,
            }
        )
        
    def chat_message(self, event):
        message = event['message']
        sent_by = event['sent_by']
        room_id = event['room_id']
        book = event['book']

        self.send(text_data=json.dumps({
            'type':'chat',
            'message': message,
            'sent_by' : sent_by,
            'room_id' : room_id,
            'book' : book,
        }))  

        if sent_by == 'user':
            txt = ask_lenny(message, room_id if room_id == book else book )
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type':'chat_message',
                    'message': txt,
                    'sent_by' : 'chat-gpt',
                    'room_id' : room_id,
                    'book' : book,
                }
            )
