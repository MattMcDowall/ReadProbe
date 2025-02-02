import time
import uuid
import openai
import requests
import numpy as np
import streamlit as st
from bs4 import BeautifulSoup
from ftfy import fix_text
from typing import List


@st.cache_data(show_spinner=False)
def bing_search(query, top_n=3):
    # This function takes as input a query and
    # return a list containing Bing search results (top n) for the query.
    headers = {'Ocp-Apim-Subscription-Key': st.secrets.azure_bing_keys.key}
    return_list = []
    response = requests.get('https://api.bing.microsoft.com/v7.0/search', headers=headers,
                            params={'q': query, 'textDecorations': True, 'textFormat': "HTML"})
    response.raise_for_status()
    search_results = response.json()
    # Fetch the web document content for each relevant URL
    for result in search_results['webPages']['value']:
        result_response = requests.get(result['url'])
        try:
            soup = BeautifulSoup(result_response.content, 'html.parser')
            text = soup.find('body').get_text()
            clean_text = ''
            for line in text.split('\n'):
                clean_line = line.strip()
                if len(clean_line.split(' ')) > 3:
                    clean_text += f'{clean_line}\n'
        except AttributeError as e:
            print(f'[INFO] Skipped one URL [{result["url"]}] with error {e}.')
            continue
        return_list.append([result['url'], clean_text])
        if len(return_list) >= top_n:
            break
    return return_list


@st.cache_data(show_spinner=False)
def generate_questions(input_text: str, provider='openai'):
    # This function calls OpenAI APIs to generate a list of questions
    # based on the input text given by the user.
    print(openai.api_base)
    messages = [
        {'role': 'system',
         'content': 'You are a factual and helpful assistant to aid users in the lateral reading task. You will '
                    'receive a segment of text (Text:), and you need to raise five important, insightful, diverse, '
                    'simple, factoid questions that may arise to a user when reading the text but are not answered by '
                    'the text (Question1:, Question2:, Question3:, Question4: Question5:). The questions should be '
                    'suitable as meaningful queries (use explicit entities that are fully resolved and not dependent '
                    'on Text:) to a search engine like Bing. Your questions will motivate users to search for '
                    'relevant documents to better determine whether the given text contains misinformation.'},
        {'role': 'user', 'content': f'Text: {input_text}\n------\nCarefully choose insightful and atomic lateral '
                                    f'reading questions not answered by the above text, ensuring that the queries are '
                                    f'self-sufficient (Do not have pronouns or attributes relying on the text, '
                                    f'they should be fully resolved and make complete sense independently).'}
    ]
    if provider == 'openai':
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
            temperature=0.2,
        )
    elif provider == 'azure':
        completion = openai.ChatCompletion.create(
            engine='gpt-4-32k',
            messages=messages,
            temperature=0.2,
        )
    else:
        raise Exception(f'[ERROR] Unidentified ChatGPT Provider: {provider}')
    response = completion['choices'][0]['message']['content']
    responses = [line for line in response.split('\n') if line.strip() != '']
    questions = []
    for ind, line in enumerate(responses):
        question = line.strip()
        questions.append(question.removeprefix(f'Question{ind + 1}:').strip())
    return questions


@st.cache_data(show_spinner=False)
def summarize(question: str, documents: List[str], provider='openai'):
    # This function takes as input a pair of question and document to produce
    # a short summary to answer the question using the information in the document.

    # Use embeddings to find relevant chunks.
    concatenated_input = ''
    for doc_id, document in enumerate(documents):
        concatenated_input += f'Document {doc_id + 1}:\n{document[:40000]}'

    messages = [
        {'role': 'system',
         'content': 'You are a factual and helpful assistant designed to read and cohesively summarize segments from '
                    'different relevant document sources to answer the question at hand. Your answer should be '
                    'informative but no more than 100 words. Your answer should be concise, easy to understand and '
                    'should only use information from the provided relevant segments but combine the search results '
                    'into a coherent answer. Do not repeat text and do not include irrelevant text in your answers. '
                    'Use an unbiased and journalistic tone. Make sure the output is in plaintext. Attribute each '
                    'sentence with proper citations using the document number with the [${doc_number}] notation '
                    '(Example: "Hydroxychloroquine is not a cure for COVID-19 [1][3]."). Ensure each sentence in the '
                    'answer is properly attributed. Ensure each of the documents is cited at least once. If different '
                    'results refer to different entities with the same name, cite them separately.'},
        {'role': 'user',
         'content': f'My question is "{question}" Cohesively and factually summarize the following documents to '
         f'answer my question.\n------\n{concatenated_input}'}]
    # Ask ChatGPT to summarize the extracted chunks.
    retry_count = 0
    while retry_count < 3:
        try:
            if provider == 'openai':
                completion = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=messages,
                    temperature=0.2,
                )
            elif provider == 'azure':
                completion = openai.ChatCompletion.create(
                    engine='gpt-4-32k',
                    messages=messages,
                    temperature=0.2,
                )
        except Exception as e:
            print(f'[INFO] Exception: {e}. Retry in five seconds.')
            time.sleep(10)
            continue
        break

    if retry_count < 3:
        return completion['choices'][0]['message']['content']
    else:
        return ''


@st.cache_data(show_spinner=False)
def log_data(log_id: str, user_input: str, output: str, action: str):
    # This function takes as input a pair of question and document to produce
    # a short summary to answer the question using the information in the document.
    form_data = {
        'entry.824492780': log_id,
        'entry.1800058496': user_input,
        'entry.602078405': output,
        'entry.242548152': action
    }
    url = st.secrets.google_forms.link
    requests.post(url, data=form_data)


@st.cache_data(show_spinner=False)
def input_check(input_text: str):
    # This function check whether the input text complies with OpenAI's usage policies.
    response = openai.Moderation.create(
        input=input_text
    )
    output = response['results'][0]['categories'].values()
    return False if True in output else True


def refresh(top_n: int):
    # This function refreshes the current page and makes it ready for regeneration.
    if 'generated' in st.session_state:
        st.session_state.generated = 0
    if 'generation_id' in st.session_state:
        st.session_state.generation_id = uuid.uuid4()
    for i in range(top_n):
        if f'question_{i}_feedback' in st.session_state:
            st.session_state[f'question_{i}_feedback'] = 0
    st.cache_data.clear()


if __name__ == '__main__':
    # This part is used for testing functions in this file.
    print('This is a text.')
