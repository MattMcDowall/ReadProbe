# ReadProbe

## Features

- [x] **Input Moderation**: asdasd

## Plans
- [ ] Bing search function: Given a question, 
this function should return a string which is the concatenation of the web
documents of top **3** Bing search results.
- [ ] Question generation function: Given a piece of text, this function
should call ChatGPT APIs to generate a list questions relevant to the text
to support lateral reading.
- [ ] Answer generation function: Given a generated question and top **n**
relevant documents found by Bing search, this function should call ChatGPT
APIs to generate an answer to the question.
- [ ] Input text examination. To avoid intentionally malicious input,
we should filter out certain black-list words and check the language 
(English only).
- [ ] For each generated question, there should be a "like" button so that
users can indicate if they like the generated questions.
- [ ] Ask friends to try this web app and provide feedback.
- [ ] Make sure the API key is provided in the cloud app, not in this repo.
- [ ] Log histories (input, output, feedback) into a online database.

## Q&A
1. How to run this project on my local machine? \
Make sure you have [Streamlit](https://streamlit.io/) installed. 
Then run this command in the root repository of this project 
`streamlit run main.py`. 
   1. Bing API: free , how to get.


## Evaluation

To empirically evaluate the effectiveness of this web app in real-life scenarios,
we conducted a small-scale pilot user study by asking our friends to try using
this tool.
To mimic real use cases, we didn't provide additional context or explanations
other than those shown in the web app itself.
Here is our instruction for the pilot user study.
> We developed a tool to help users perform lateral reading 
> using OpenAI services. Thanks for agreeing to participate in
> this pilot user study. Some of your usage data will be collected 
> anonymously. Please spend at least 15 minutes playing with this web
> application: https://readprobe.streamlit.app/. Once finished, please
> contact us to provide feedback on what aspects you like or dislike this
> application. Thanks again for your valuable time.

X participants joined this pilot study. Here, we express our gratitude to
their valuable feedback. We summarized their feedback into several points
shown below:
- Positive
  1. asdas
- Nagtive
  1. asdasd



## :warning: Disclaimer 
## Other

Deliverables

t the end of the hackathon, your team is asked to submit the following:

A live prototype solution, and
Hint: depending on the nature of your app, you may be able to deploy it for free at https://vercel.com/
An open-source program with installation instructions uploaded to GitHub and licensed under GNU GPLv3.
The source code should include a readme document that will (a) outline your solution, (b) describe all planned and implemented functionalities, (c) how your solution can be deployed to fight misinformation online and by whom and (d) whether and how you evaluated its effectiveness.