"""Views for user profile management and updates."""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile

@login_required
def profile(request):
    """Render and handle the user profile update form.
    
    Processes GET requests to display current profile data and POST requests
    to validate and save updates to both user account and extended profile.
    Ensures a profile instance exists before rendering.
    
    Args:
        request: The HTTP request object containing user session data.
        
    Returns:
        HttpResponse: Rendered profile template or redirect after successful update.
    """
    # Ensure profile instance exists for the authenticated user
    Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users_profile/profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })