# HorDoc

Unleashing the power of AI and community knowledge to enhance user support in public Discord channels.

## Problem statement

For public Discord communities it is a challenge to efficiently and accurately providing answers to user questions, especially with a continuous inflow of new users asking the same question over and over.

By leveraging the knowledge embedded in historical conversation data from support channels we aim to reduce the repetitive burden on community members, improve response times, and enhance the overall user experience for new and existing users seeking assistance.

## Target audience

Open source projects with a public Discord community.
- Medium sized (sufficient chat history)

## Objectives

MVP for a chatbot that can learn from and answer questions based on conversations in public Discord channels. The bot should be able to effectively scrape text data from these channels, including questions and answers, and use this data to train a simple yet effective Q&A model. The primary objective is to help answer common questions asked by new users, leveraging the knowledge acquired from the historical chat data.

## MVP features & functionality

1. Scrape Discord messages from support channels to collect relevant data for the chatbot.
2. Use NLP techniques or simple heuristics (e.g., messages ending with a question mark) to accurately identify proper questions and answers from the scraped messages.
3. Extract mini Q&A conversation logs, organize them into structured pairs, and store them in a database for easier access and retrieval.
4. Generate consistent and efficient embedding vectors for questions and answers using an appropriate method (e.g., Word2Vec, FastText, or BERT embeddings).
5. Develop a Discord chatbot that listens for user questions and integrates the model with the Discord platform.
6. Create embedding vectors for incoming user questions using the same embedding method as in step 4 to maintain consistency.
7. Perform a similarity search using the question vector and a similarity metric like cosine similarity or other distance measures to accurately identify the most related historical conversations.
8. Limit the number of related conversations used as context and create a prompt for a large language model (LLM) to generate an answer based on the provided context.
9. Return the generated answer to the user, completing the chatbot's purpose of assisting with relevant information based on historical chat data.

## Risks
1. Discord TOS: Scraping and storing user messages might be a violation of the Terms of Services of Discord.
2. Data Privacy: Scraping and storing user messages from public Discord channels may raise data privacy concerns.
3. Inaccurate answers: The chatbot may provide incorrect or irrelevant answers, especially if the training data is noisy or insufficient.
4. Scalability: The chatbot may struggle to handle a large number of simultaneous users or a significant increase in conversation volume.
5. Resistance to adoption: Users may be hesitant to engage with the chatbot or may prefer human interaction.
6. Continual learning: The chatbot may become outdated if it doesn't continuously learn from new conversations.
7. Misinterpretation of context or sarcasm: The chatbot may not accurately interpret context, sarcasm, or other nuances in the user's questions, leading to incorrect responses.

## KPIs
1. User satisfaction: Track user satisfaction through feedback mechanisms such as ratings, surveys, or direct feedback.
2. Adoption rate: Monitor the percentage of users who actively engage with the chatbot compared to the total number of users in the community.
3. Accuracy: Calculate the percentage of correct answers provided by the chatbot based on user feedback or manual evaluation.
4. Response time: Measure the average time taken for the chatbot to respond to user questions.
5. Reduction in repetitive questions: Track the decrease in the number of repetitive questions asked in the support channels.
6. Escalation rate: Measure the percentage of questions escalated to human support due to the chatbot's inability to provide a satisfactory answer.
7. Retention rate: Assess the percentage of users who continue to use the chatbot after their initial interaction.
8. Community growth: Monitor the growth of the community, considering factors such as new user registrations and user activity levels.

## Assumptions

1. Availability of sufficient historical chat data: The chatbot's effectiveness relies on a large amount of historical conversation data to train and develop accurate responses.
2. Quality and relevance of chat data: The scraped messages from support channels are assumed to contain accurate and relevant information to address users' questions.
3. User acceptance: It is assumed that users will be open to engaging with an AI chatbot for support and will provide feedback to improve its performance.
4. Feasibility of natural language processing techniques: The assumption is that NLP techniques or heuristics will be effective in accurately identifying questions and answers from the scraped messages.
5. Consistency in language and terminology: The assumption is that users within the community use consistent language and terminology when discussing issues and solutions, making it easier for the chatbot to understand and respond.
6. Compatibility with the Discord platform: It is assumed that the chatbot can be effectively integrated into the Discord platform without any significant technical difficulties or limitations.
7. Ongoing support and maintenance: The assumption is that there will be sufficient resources, both human and financial, to maintain and update the chatbot as needed.
8. Compliance with data protection regulations: It is assumed that scraping and storing user messages for training purposes will comply with applicable data protection regulations, and that any necessary consents will be obtained from users.

