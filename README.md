# TLDR-youtube-LLM
Youtube for people with no patience-aka TLDR youtube with help of LLM to speed up the information gathering and learnining.

If you feel watching youtube is too much time consumed just to aquire some info and knowledge but you still want to learn more with better efficiency, this app is for you. 

We let the LLM to read the script with corresponding timestamp so you can easily ask and navigate the content in your control than you have to watch the whole thing. 

![screencapture-localhost-8501-2024-11-12-23_01_35](https://github.com/user-attachments/assets/7b732c70-5cb1-4045-8578-c2898e652016)

![screencapture-tldr-youtube-llm-streamlit-app-2024-11-12-23_02_07](https://github.com/user-attachments/assets/f865c1e5-7f9d-4162-af61-e65aad75d307)


## run 
`pip install -r requirements.txt`

update your `CLAUDE_API_KEY` in .env and 
`streamlit run main.py`

running locally is way much better since it seems youtube block loading script through streamlit cloud for some videos also streamlit on cloud runs inconsistently funny with the localhost version. 


## TODO

1-add user memory layer to better navigate the conversation

2-add user notebook to let user organize the info aquired, not limited by number of notebook like notebookLLM

3-next js true web app than a toy streamlit

## issue with online streamlit
for issue like
```
Error: Could not retrieve a transcript for the video https://www.youtube.com/watch?v=kwivhbXLg9Q! This is most likely caused by:

Subtitles are disabled for this video
```
you need to run locally given the google restriction mostlikely. 

##
License: CC BY-NC 4.0

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.

You are free to:

Share — copy and redistribute the material in any medium or format
Adapt — remix, transform, and build upon the material
Under the following terms:
Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
NonCommercial — You may not use the material for commercial purposes.
[View the full license here: Creative Commons BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.en)
