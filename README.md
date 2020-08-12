# chatbot_production contains code for chatbot demo

Demo of Rasa chatbot capability exploiting custom actions implemented in Python and webpages served by Flask and rendered in webview in the context of Facebook Messenger.

Custom actions: 
- actions.py: ingest CSV file with base data and take custom actions 
- custom_action_config.yml: config file containing parameters used by actions.py

Rasa core files:
- Sentence level training: data/nlu.md
- Discourse level training: data/stories.md
- Rasa configuration files: config.yml, credentials.yml, credentials_test.yml, domain.yml, endpoints.yml,

webview related files:
- Flask web serving module: flask/*.*
- web pages for rendering in webview in the context of Facebook Messenger: templates/*.*
 
