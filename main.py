from datetime import datetime
import speech_recognition as sr
import pyttsx3
from logging.config import listen
import webbrowser
import wikipedia
import wolframalpha
import keyboard
import threading
import time

# speech recognization

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0=male, 1=female
activationword = 'computer'
#wolframe client
appID = '7JUJ7Q-YE8RRLGG47'
wfClient= wolframalpha.Client(appID)
# fixing browser
bpath = r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
webbrowser.register('brave', None, webbrowser.BackgroundBrowser(bpath))


def speak(text, rate=120):
    engine.setProperty('rate',rate)
    engine.say(text)
    engine.runAndWait()


def parsecommand():
    listener = sr.Recognizer()

    while True:
        print("Listening...")

        with sr.Microphone() as source:
            listener.pause_threshold = 1
            try:
                input_speech = listener.listen(source, timeout=5)
                print("Recognizing speech...")
                query = listener.recognize_google(input_speech, language='en-in')
                print(f'The input speech was: {query}')
                return query.lower()
            except sr.UnknownValueError:
                speak("Scythor didn't understand, please repeat again.")
                return 'None'
            except sr.RequestError as e:
                speak(f"Could not request results from Google Speech Recognition service; {e}")
                return 'None'


def search_wiki(query = ''):
    searchResults = wikipedia.search(query)
    if not searchResults:
        speak('No results on wikipedia ')
        return 'No results received..'
    try:
        wikiPage =  wikipedia.page(searchResults[0])
    except wikipedia.DisambiguationError as error:
        wikiPage = wikiPage.page(error.options[0])
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary

def listOrDict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']


def search_wf(query=''):
    try:
        response = wfClient.query(query)
        if response['@success'] == 'false':
            error_message = response.get('@error', {}).get('msg', 'Could not compute')
            print(f"Wolfram Alpha Error: {error_message}")
            return 'Could not compute'

        # Extract relevant information from the response
        result = parse_wolfram_response(response)
        return result
    except Exception as e:
        print(f"Exception during computation: {e}")
        return 'Could not compute'


def parse_wolfram_response(response):
    try:
        # Look for pods that may contain results
        pods = response.get('pod', [])

        for pod in pods:
            # Check if the pod contains a primary result
            if pod.get('@primary', 'false') == 'true':
                subpods = pod.get('subpod', [])

                # Extract plaintext from the first subpod
                if subpods:
                    return subpods[0].get('plaintext', '').strip()

        # If no primary result found, try to get the first plaintext from any pod
        for pod in pods:
            subpods = pod.get('subpod', [])
            if subpods:
                return subpods[0].get('plaintext', '').strip()

        return 'Could not compute'
    except Exception as e:
        print(f"Exception during parsing: {e}")

    return 'Could not compute'


if __name__ == '__main__':
    speak('All systems normal...')

    while True:
        query = parsecommand().lower()

        # Check for "say hello" anywhere in the sentence
        if 'say' in query and 'hello' in query:
            speak('Greetings, all..')

        elif 'se' in query and 'hello' in query:
            speak('Greetings, all..')
        # Check if the activation word is present and process other commands
        if activationword in query:
            query = query.replace(activationword, '').strip()

            # Process other commands
            if query.startswith('say') or query.startswith('se') :
                speech = query[4:].strip()
                speak(speech)

        # Check for "go to" anywhere in the sentence
        elif 'go to' in query or 'open' in query:
            speak('Opening...')
            query_url = query.split('go to', 1)[1].strip()
            if not query_url.startswith(('http://', 'https://')):
                query_url = 'https://www.google.com/search?q=' + query_url
            webbrowser.get('brave').open_new(query_url)

        #wekipedia

        if query.startswith('wikipedia'):
            query = query[len('wikipedia'):].strip()  # Remove 'wikipedia' from the query
            speak('Querying the universal databank')
            result = search_wiki(query)
            speak(result)

        if 'how are you' in query:
            speak("Scythor is happy, how are you?")

        if 'compute' in query or 'tell me about' in query or 'explain' in query:
            query = ' '.join(query[1:])
            speak('Computing...')
            try:
                result = search_wf(query)
                speak(result)
            except Exception as e:
                print(f"Exception during computation: {e}")
                speak('Unable to compute')

        if 'terminate' in query:
            speak('terminating...')
            exit(0)







