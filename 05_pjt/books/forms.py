from django import forms

from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'description', 'rating', 'author']
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ENTER TITLE',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ENTER DETAILED DESCRIPTION',
                    'rows': 4,
                    'style': 'height: 120px !important; resize: none;',
                }
            ),
            'rating': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'author': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
        }
        labels = {
            'title': 'TITLE',
            'description': 'DESCRIPTION',
            'rating': 'RATING',
            'author': 'AUTHOR',
        }
        
        
class UpdateBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'description', 'rating', 'author']
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ENTER TITLE',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ENTER DETAILED DESCRIPTION',
                    'rows': 4,
                    'style': 'height: 120px !important; resize: none;',
                }
            ),
            'rating': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'author': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
        }
        labels = {
            'title': 'TITLE',
            'description': 'DESCRIPTION',
            'rating': 'RATING',
            'author': 'AUTHOR',
        }