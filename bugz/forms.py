from django import forms
import pyparsing as pp


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(), required=True)


def search_parser():
    quoted = pp.dblQuotedString()
    literal = pp.Word(pp.pyparsing_unicode.printables)


class SearchForm(forms.Form):
    q = forms.CharField(initial="")

    def apply_qs(self, qs):
        q = self.cleaned_data.get("q", "")
        return qs
