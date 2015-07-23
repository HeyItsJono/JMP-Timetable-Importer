import JMPConverterSem2
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import urlparse

from .models import PBLQuestion, NumQuestion, PBLChoice, NumChoice

# Create your views here.


def details(request):
    this_url = request.build_absolute_uri()
    if 'code' in request.REQUEST and 'fail' not in request.REQUEST:
        code = request.REQUEST['code']
        pblq = get_object_or_404(PBLQuestion, pk=1)
        numq = get_object_or_404(NumQuestion, pk=1)
        return render(request, 'timetable/details.html', {
            'numq': numq,
            'pblq': pblq,
            'auth_code': code,
            'redir_url': this_url,
        })
    else:
        return redirect(JMPConverterSem2.get_google_redirect(this_url))


def processing(request):
    pblq = get_object_or_404(PBLQuestion, pk=1)
    numq = get_object_or_404(NumQuestion, pk=1)
    destination = request.POST['destination']
    timetable_title = request.POST['timetable_title']
    auth_code = request.POST['auth_code']
    # this_url is a value taken from the details view above, which stored it in the details.html file as a hidden
    # value. this_url is necessary for the authentication flow. The urlparse functions pull it apart and reassemble it.
    this_url = urlparse.urlunsplit(urlparse.urlsplit(request.POST['redir_url'])[:3] + ('', ''))
    try:
        selected_pbl_choice = pblq.pblchoice_set.get(pk=request.POST['pblchoice'])
    except (KeyError, PBLChoice.DoesNotExist):
        return render(request, 'timetable/details.html', {
            'numq': numq,
            'pblq': pblq,
            'error_message': "You forgot to pick a PBL Group!",
        })
    else:
        try:
            selected_num_choice = numq.numchoice_set.get(pk=request.POST['numchoice'])
        except (KeyError, NumChoice.DoesNotExist):
            return render(request, 'timetable/details.html', {
                'numq': numq,
                'pblq': pblq,
                'error_message': "You forgot to pick a PBL Group Number!",
            })
        else:
            selected_num_choice = str(selected_num_choice)
            selected_pbl_choice = str(selected_pbl_choice)
            timetable = JMPConverterSem2.create_timetable(selected_pbl_choice, selected_num_choice)
            if destination == 'gcal':
                JMPConverterSem2.export_calendar(auth_code, timetable, this_url, timetable_title)
                return HttpResponseRedirect(reverse('timetable:results'))
            elif destination == 'csv':
                csv_name = JMPConverterSem2.make_csv(timetable)
                csv_name = csv_name.strip('app-root/runtime/repo/wsgi/static/exported_timetables/timetable_.csv')
                return HttpResponseRedirect(reverse('timetable:download', args=(csv_name, timetable_title.replace(' ','_'))))
            else:
                return render(request, 'timetable/details.html', {
                    'error_message': "Unknown destination error. Please try again.",
                })



def results(request):
    return HttpResponse("Processing Finished.")


def download(request, csv_name, timetable_title):
    csv_name = 'app-root/runtime/repo/wsgi/static/exported_timetables/timetable_' + csv_name + '.csv'
    with open(csv_name, 'rb') as infile:
        response = HttpResponse(infile, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{timetable_title}'.format(timetable_title=timetable_title)
        return response
