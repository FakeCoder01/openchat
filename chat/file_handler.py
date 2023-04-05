from langchain.llms import OpenAI
import os
from gpt_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper 


os.environ['OPENAI_API_KEY'] = "API_KEY"
def file_upload_handler(user_id):
    try:
        file_url = f"media/pdf/{user_id}.pdf"
        max_input_size = 4096
        num_outputs = 256
        max_chunk_overlap = 20
        chunk_size_limit = 600
        llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003", max_tokens=num_outputs))
        prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
        documents = SimpleDirectoryReader(input_files=[file_url, ]).load_data()
        index = GPTSimpleVectorIndex(
            documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper
        )
        index.save_to_disk(f'media/file-data/{user_id}_data.json')
        os.remove(file_url)
        return True
    except Exception as err:
        print(err)
        return False
    
