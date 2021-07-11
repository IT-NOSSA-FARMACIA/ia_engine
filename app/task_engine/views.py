from django.shortcuts import render

# Create your views here.


def schedule_list(request):
    return render(request, 'task_engine/schedule_list.html')