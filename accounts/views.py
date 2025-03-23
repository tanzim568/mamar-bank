from django.shortcuts import render,redirect
from django.views.generic import FormView,View
from django.contrib.auth.views import LoginView,LogoutView
from .forms import RegistrationForm,UserUpdateForm
from django.contrib.auth import login,logout
from django.urls import reverse_lazy
# Create your views here.

class UserRegistrationView(FormView):
    template_name='./accounts/user_registration.html'
    form_class=RegistrationForm
    success_url=reverse_lazy('register')
    
    def form_valid(self,form):
        user=form.save()
        login(self.request,user)
        print(user)
        return super().form_valid(form)
    
class UpdateProfileView(View):
    template_name='./accounts/profile.html'
    form_class=UserUpdateForm
    success_url=reverse_lazy('register')
    
    # def form_valid(self,form):
    #     # user=form.save()
    #     # login(self.request,user)
    #     # print(user)
    #     return super().form_valid(form)
    def get(self,request):
        form=UserUpdateForm(instance=request.user)
        return render(request,self.template_name,{'form':form})
    
    def post(self,request):
        form=UserUpdateForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return  render(request,self.template_name,{'form':form})

class UserLoginView(LoginView):
    template_name='./accounts/user_login.html'
    # success_url=reverse_lazy('homepage')

    def get(self,request):
        return render(request,'./accounts/user_login.html')
    
    def get_success_url(self):
        return reverse_lazy('homepage')
    
class CustomLogoutView(LogoutView): #dispatch runs before django process the request
    def dispatch(self, request, *args, **kwargs):
        """Ensure user is logged out before redirecting"""
        if request.user.is_authenticated:
            logout(request)  # Log out the user
        return redirect(reverse_lazy('homepage'))  # Redirect to homepage