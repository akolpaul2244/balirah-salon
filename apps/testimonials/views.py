from django.contrib import messages
from django.shortcuts import render, redirect
from django_ratelimit.decorators import ratelimit
from .forms import TestimonialForm
from .models import Testimonial


def testimonial_list(request):
    testimonials = Testimonial.objects.filter(is_approved=True).select_related('service')
    return render(request, 'testimonials/testimonial_list.html', {'testimonials': testimonials})


@ratelimit(key='ip', rate='3/h', method='POST', block=True)
def submit_testimonial(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            t = form.save(commit=False)
            if request.user.is_authenticated:
                t.user = request.user
                t.client_name = request.user.get_full_name()
            t.save()
            messages.success(request, 'Thank you! Your review will appear after approval.')
            return redirect('testimonials:list')
    else:
        form = TestimonialForm(user=request.user)
    return render(request, 'testimonials/submit.html', {'form': form})
