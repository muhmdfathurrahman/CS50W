from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect # For testing purposes
from django.core.exceptions import ValidationError
from django import forms

from . import util

from markdown2 import markdown
from string import ascii_lowercase as lowercase
from random import randint


class editorForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    body = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control"
    }))

    def titleIsAvailable(self):
        title = self.data['title']
        for file_name in util.list_entries():
            if title == file_name:
                self.add_error('title', f'Encyclopedia entry with {title} title is already existed')


def format_checker(title, current_page):
    """
    Control HTTP URL and redirect if user type title incorrectly.
    Arguments:  
        title-> the title of the document.
        current_page -> current page to tell the function which page to redirect.
    Return redirects or True if title's formatted correctly.
    """
     # Format Checking: Doesn't allow user to put non-capitalized path
    if title[0] in lowercase:
        return HttpResponseRedirect(reverse(current_page, kwargs={
            "title": title.capitalize()}))
    
    # Get entry
    entry = util.get_entry(title)

    # Format Checking: Redirect to url path with exactly the same title
    #                  as written in md file
    if not title == entry["title"]:
        return HttpResponseRedirect(reverse(current_page, kwargs={
            "title": entry["title"]
        }))
    return False
    

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def page(request, title):
    FORMAT_CHECK = format_checker(title, "page")
    if not format_checker(title, "page"):
        entry = util.get_entry(title)
        entry["first_line"] = (markdown(entry["body"].split('\n')[0])
                               if (entry["body"] is not None) else None)
        entry["body"] = (markdown('\n'.join(entry["body"].split('\n')[1:])) 
                         if (entry["body"] is not None) else None)
        return render(request, "encyclopedia/page.html", {
            "title": entry["title"],
            "first_line": entry["first_line"],
            "page": entry["body"]
        })
    return FORMAT_CHECK


def random_page(request):
    entries = util.list_entries()
    return HttpResponseRedirect(reverse("page", kwargs={
        "title": entries[randint(0, len(entries) - 1)]
    }))


def edit_page(request, title):
    # User accessing route via POST
    if request.method == "POST":
        form = editorForm(request.POST)
        if form.is_valid():
            util.save_entry(form.data['title'], form.data['body'])
            return HttpResponseRedirect(reverse("page", kwargs={
                "title": form.data['title']
            })) 
        else:
            return render(request, "encyclopedia/editor.html", {
                "form": form,
                "title": title,
                "type": "Edit"
            })
        
    # User accessing route via GET
    FORMAT_CHECK = format_checker(title, "edit-page")
    if not FORMAT_CHECK:
        body = util.get_entry(title)["body"]

        # Redirect to page if there is no page to edit to tell that
        # page doesn't exist
        if body is None:
            return HttpResponseRedirect(reverse("page", kwargs={
                "title": title
            }))
        
        form = editorForm({
            "title": title,
            "body": body
        })
        return render(request, "encyclopedia/editor.html", {
            "form": form,
            "title": title,
            "type": "Edit"
        })
    return FORMAT_CHECK


def new_page(request, title=None):
    if request.method == "POST":
        form = editorForm(request.POST)
        if form.is_valid() and form.titleIsAvailable():
            util.save_entry(form.data['title'], form.data['body'])
            return HttpResponseRedirect(reverse("page", kwargs={
                "title": form.data['title']
            })) 
        else:
            return render(request, "encyclopedia/editor.html", {
                "form": form,
                "title": title,
                "type": "New Page"
            })
    if title is not None:
        # Lesser format check that only be used in this particular
        # Function
        if title[0].islower():
            return HttpResponseRedirect(reverse("new-page", kwargs={
                "title": title.capitalize()
            }))
        # Redirect to edit page if page already exists
        if util.get_entry(title)["body"]:
            return HttpResponseRedirect(reverse("edit-page", kwargs={
                "title": title
            }))
        body = f"# {title}\r\n\r\n"
        form = editorForm({
            "title": title,
            "body": body
        })
    else:
        form = editorForm()
    return render(request, "encyclopedia/editor.html", {
        "form": form,
        "title": title,
        "type": "New Page"
    })


def search(request):
    if "q" not in request.GET.keys():
        return HttpResponseRedirect(reverse("index"))
    query = request.GET["q"]
    possible_entries = []
    for file in util.list_entries():
        if query.lower() == file.lower():
            return HttpResponseRedirect(reverse("page", kwargs={
                "title": query
            }))
        elif query.lower() in file.lower():
            possible_entries.append(file)
    return render(request, "encyclopedia/search-result.html", {
        "query": query,
        "possible_entries": possible_entries
    })