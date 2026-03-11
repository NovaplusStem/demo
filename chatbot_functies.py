import cohere

API_key  = "fsUZa6Yd0VzMfgHG5PecZbpFnDFDp57iYpfQ5ZnK"

co = cohere.Client(API_key)

def chatbot_response(prompt):
    '''Deze functie neemt een prompt als input, stuurt de prompt naar de Cohere API en geeft het LLM-antwoord terug'''
    response = co.chat(message=prompt)
    return response.text