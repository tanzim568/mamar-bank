from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .constants import GENDER_TYPE,ACCOUNT_TYPE
from django import forms
from .models import UserBankAccounts,UserAddress

class RegistrationForm(UserCreationForm):# usercreation form ke inherit korechi mane user model er field gulo to form e thakbei sathe nicher additional data ba form field gulao thakbe etia inheritance
    account_type=forms.ChoiceField(choices=ACCOUNT_TYPE)
    birth_date=forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender=forms.ChoiceField(choices=GENDER_TYPE)
    street_address=forms.CharField(max_length=100)
    city=forms.CharField(max_length=100)
    postal_code=forms.IntegerField()
    country=forms.CharField(max_length=100)
    
    class Meta:
        model=User
        fields=['username','password1','password2','first_name','last_name','email','account_type','birth_date','gender','postal_code','city','country','street_address']    
    def save(self,commit=True):
        form=super().save(commit=False) #Usercreation form parent class er ba User model er je form field gulo chilo oi gula form e store kore rekhechi
        if commit==True:
            form.save() #user model e data save hoise baki 2 ta model e data save kora baki // jokhon e user .save() use korbe tokhon user(Usercreation model ba parent class theke ja ja inherit kora hoise ) model er data save hobe and 
     # sthe amra jei additional field gula add korsi oi field er value niche capture kore jei jei mdoel er ekta object create kroe database e rekhe dise.. save mehtod e sob eksthe save hoise
            account_type=self.cleaned_data.get('account_type')
            gender=self.cleaned_data.get('gender')
            birth_date=self.cleaned_data.get('birth_date')
            account_type=self.cleaned_data.get('account_type')
            street_address=self.cleaned_data.get('street_address')
            city=self.cleaned_data.get('city')
            country=self.cleaned_data.get('country')
            postal_code=self.cleaned_data.get('postal_code')
            
            UserBankAccounts.objects.create(
                user=form,
                account_type=account_type,
                gender=gender,
                birth_date=birth_date,
                account_no=100000+form.id
            )
            UserAddress.objects.create(
                user=form,
                postal_code=postal_code,
                country=country,
                city=city,
                street_address=street_address
            )
        return form
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) #constructor call kora hoise parent class er kichu field (self.field diye kichu class attibute) ke overwrite kora hoise
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class':(
                    'appearence-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500 '
                )
            })
            
class UserUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length= 100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })
        # jodi user er account thake 
        if self.instance:
            try:
                user_account = self.instance.account  #UserBankAccounts er related name
                user_address = self.instance.address  #UserAddress er related name
            except UserBankAccounts.DoesNotExist:
                user_account = None
                user_address = None

            if user_account:
                self.fields['account_type'].initial = user_account.account_type
                self.fields['gender'].initial = user_account.gender
                self.fields['birth_date'].initial = user_account.birth_date
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_account, created = UserBankAccounts.objects.get_or_create(user=user) # jodi account thake taile seta jabe user_account ar jodi account na thake taile create hobe ar seta created er moddhe jabe
            user_address, created = UserAddress.objects.get_or_create(user=user) 

            user_account.account_type = self.cleaned_data['account_type']
            user_account.gender = self.cleaned_data['gender']
            user_account.birth_date = self.cleaned_data['birth_date']
            user_account.save()

            user_address.street_address = self.cleaned_data['street_address']
            user_address.city = self.cleaned_data['city']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.country = self.cleaned_data['country']
            user_address.save()

        return user
                
                           