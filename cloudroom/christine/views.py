from django.shortcuts import render


def room(request):
    return render(request, 'christine/room.html')
