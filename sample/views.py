from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    return render_to_response('index.html', {'user': request.user}, context_instance=RequestContext(request))    


