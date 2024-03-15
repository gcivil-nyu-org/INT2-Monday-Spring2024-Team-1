from django import forms

class HealthRecordForm(forms.Form):
    user_id = forms.IntegerField(disabled=True)
    hospital = forms.CharField()
    doctor = forms.ChoiceField()
    appointment = forms.CharField()
    health_document = forms.JSONField()