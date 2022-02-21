import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from .models import BookInstance


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text='Insira uma data entre agora e 4 semanas (padrão 3 semanas).')

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']
        
        # Para checar se a data não está no passado.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))
        
        # Para checar se a data está dentro do valor permitido (+4 semanas a partir do dia de hoje).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))
        
        # Lembrar de sempre retornar o dado "limpo".
        return data


# exemplo de ModelForm:
# class RenewBookModelForm(ModelForm):
#     def clean_due_back(self):
#         data = self.cleaned_data['due_back']
#
#         # Para checar se a data está no passado:
#         if data < datetime.date.today():
#             raise ValidationError(_('Invalid date - renewal in past'))
#
#         # Para checar se a data está dentro do valor permitido (+4 semanas a partir do dia de hoje).
#         if data > datetime.date.today() + datetime.timedelta(weeks=4):
#             raise ValidationError(_('Invalid date = renewal more than 4 weeks ahead'))
#
#         # Lembrar de sempre retornar o dado "limpo".
#         return data
#
#     class Meta:
#         model = BookInstance
#         fields = ['due_back']
#         labels = {'due_back': _('Renewal date')}
#         help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).')}
