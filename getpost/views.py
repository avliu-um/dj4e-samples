from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
import html
from django.views.decorators.csrf import csrf_exempt
from django.views import View

import boto3
import json

# Call as dumpdata('GET', request.GET)

def dumpdata(place, data) :
    retval = ""
    if len(data) > 0 :
        retval += '<p>Incoming '+place+' data:<br/>\n'
        for key, value in data.items():
            retval += html.escape(key) + '=' + html.escape(value) + '</br>\n'
        retval += '</p>\n'
    return retval

def getform(request):
    response = """<p>Impossible GET guessing game...</p>
        <form>
        <p><label for="guess">Input Guess</label>
        <input type="text" name="guess" size="40" id="guess"/></p>
        <input type="submit"/>
        </form>"""

    response += dumpdata('GET', request.GET)
    return HttpResponse(response)

@csrf_exempt
def postform(request):
    response = """<p>Impossible POST guessing game...</p>
        <form method="POST">
        <p><label for="guess">Input Guess</label>
        <input type="text" name="guess" size="40" id="guess"/></p>
        <input type="submit"/>
        </form>"""

    response += dumpdata('POST', request.POST)
    return HttpResponse(response)


def invoke_lambda(lambda_name, payload):
    lambda_client = boto3.client('lambda')
    print(f'lambda name: {lambda_name}')
    print(f'payload: {payload}')
    response = lambda_client.invoke(
        FunctionName=lambda_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload),
        LogType="Tail"
    )
    print(f'lambda response: {response}')

@csrf_exempt
def ev(request):
    # first arriving at this page
    if not request.POST:
        return render(request, 'getpost/ev_intake_form.html')
    
    # form submitted
    else:
        recipient = request.POST['recipient']
        begin_date = request.POST['begin_date']
        end_date = request.POST['end_date']
        uniqueness_inside = request.POST['uniqueness_inside']
        uniqueness_outside = request.POST['uniqueness_outside']

        # TODO: Validate the values (date within range)

        # invoke the job
        # create the payload
        payload = {
            'recipient': recipient, 
            'begin_date': begin_date, 
            'end_date': end_date, 
            'uniqueness_inside': uniqueness_inside, 
            'uniqueness_outside': uniqueness_outside, 
        }
        lambda_name = 'dataset_generator'
        invoke_lambda(lambda_name=lambda_name, payload=payload)

        # debugging
        dump = dumpdata('POST', request.POST)

        return render(request, 'getpost/ev_thank_you.html', {'data' : dump })


@csrf_exempt
def html4(request):
    dump = dumpdata('POST', request.POST)
    return render(request, 'getpost/html4.html', {'data' : dump })

@csrf_exempt
def html5(request):
    dump = dumpdata('POST', request.POST)
    return render(request, 'getpost/html5.html', {'data' : dump })

def failform(request):
    response = """<p>CSRF Fail guessing game...</p>
        <form method="post">
        <p><label for="guess">Input Guess</label>
        <input type="text" name="guess" size="40" id="guess"/></p>
        <input type="submit"/>
        </form>"""

    response += dumpdata('POST', request.POST)
    return HttpResponse(response)

from django.middleware.csrf import get_token

def csrfform(request):
    response = """<p>CSRF Success guessing game...</p>
        <form method="POST">
        <p><label for="guess">Input Guess</label>
        <input type="text" name="guess" size="40" id="guess"/></p>
        <input type="hidden" name="csrfmiddlewaretoken"
            value="__token__"/>
        <input type="submit"/>
        </form>"""

    token = get_token(request)
    response = response.replace('__token__', html.escape(token))
    response += dumpdata('POST', request.POST)
    return HttpResponse(response)

# Call as checkguess('42')
def checkguess(guess) :
    msg = False
    if guess :
        try:
            if int(guess) < 42 :
                msg = 'Guess too low'
            elif int(guess) > 42 :
                msg = 'Guess too high'
            else:
                msg = 'Congratulations!'
        except:
            msg = 'Bad format for guess:' + html.escape(guess)
    return msg

def guess(request):
    guess = request.POST.get('guess')
    msg = checkguess(guess)
    return render(request, 'getpost/guess.html', {'message' : msg })

class ClassyView(View) :
    def get(self, request):
        return render(request, 'getpost/guess.html')

    def post(self, request):
        guess = request.POST.get('guess')
        msg = checkguess(guess)
        return render(request, 'getpost/guess.html', {'message' : msg })

# Send a 302 and Location: header to the browser
def bounce(request) :
    return HttpResponseRedirect('https://www.dj4e.com/simple.htm')

class AwesomeView(View) :
    def get(self, request):
        msg = request.session.get('msg', False)
        if ( msg ) : del(request.session['msg'])
        return render(request, 'getpost/guess.html', {'message' : msg })

    def post(self, request):
        guess = request.POST.get('guess')
        msg = checkguess(guess)
        request.session['msg'] = msg
        return redirect(request.path)


# References

# https://stackoverflow.com/questions/3289860/how-can-i-embed-django-csrf-token-straight-into-html

# https://stackoverflow.com/questions/36347512/how-can-i-get-csrftoken-in-view

if __name__ == '__main__':
    recipient = 'avliu@umich.edu'
    body = 'test from dj4e project folder'
    send_email(recipient, body)
