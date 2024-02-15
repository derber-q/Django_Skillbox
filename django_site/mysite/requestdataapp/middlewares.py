import time
from django.shortcuts import render
from django.http import HttpRequest


def set_useragent_on_request_middleware(get_response):
    def middleware(request: HttpRequest):
        request.user_agent = request.META['HTTP_USER_AGENT']
        response = get_response(request)
        return response
    return middleware

class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

        self.requests_time = {

        }

    def __call__(self, request: HttpRequest):
        time_limit = 5
        if not self.requests_time:
            print('First runserver')
        else:
            if(round(time.time()) * 1) - self.requests_time['time'] < time_limit and self.requests_time['ip_adress'] == request.META.get('REMOTE_ADDR'):
                context = {
                    'error': 'Exceeded the allowed frequency of requests (Requests should be made no more than once every 5 seconds)'
                }
                return render(request, 'requestdataapp/error.html', context=context)


        self.requests_count += 1
        print('requests count', self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        print('responses count', self.responses_count)
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print('got', self.requests_count, 'exception so far')




