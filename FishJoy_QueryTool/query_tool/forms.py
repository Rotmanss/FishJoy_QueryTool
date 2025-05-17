from django import forms

from .models import Spots, Baits, Fish


class AddSpotsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['spot_category'].empty_label = 'Category is not selected'

    class Meta:
        model = Spots
        fields = '__all__'


class AddFishForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fish_category'].empty_label = 'Category is not selected'

    class Meta:
        model = Fish
        fields = '__all__'


class AddBaitsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Baits
        fields = '__all__'
