from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect # For testing purposes
from django import forms

from . import util

from markdown2 import markdown
from string import ascii_lowercase as lowercase
from random import randint


class editorForm(forms.Form):
    title = forms.TextInput(attrs={
        "class": "form-control"
    })
    body = forms.Textarea(attrs={
        "class": "form-control"
    })


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


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
    

def page(request, title):
    FORMAT_CHECK = format_checker(title, "page")
    if not format_checker(title, "page"):
        entry = util.get_entry(title)
        entry["body"] = (markdown('\n'.join(entry["body"].split('\n')[1:])) 
                         if (entry["body"] is not None) else None)
        return render(request, "encyclopedia/page.html", {
            "title": entry["title"],
            "page": entry["body"]
        })
    return FORMAT_CHECK


def random_page(request):
    entries = util.list_entries()
    return HttpResponseRedirect(reverse("page", kwargs={
        "title": entries[randint(0, len(entries) - 1)]
    }))


def edit_page(request, title):
    if request.method == "POST":
        form = editorForm(request.POST)
        if form.is_valid():
            util.save_entry(form.data['title'], form.data['body'])
            return HttpResponseRedirect(reverse("page", kwargs={
                "title": title
            })) 
        else:
            return render(request, "encyclopedia/editor.html", {
                "form": form,
                "action": "/edit/" + title
            })
    FORMAT_CHECK = format_checker(title, "edit-page")
    if not FORMAT_CHECK:
        body = util.get_entry(title)["body"]
        if body is None:
            return HttpResponseRedirect(reverse("page", kwargs={
                "title": title
            }))
        form = editorForm()
        form.title = form.title.render("title", title)
        form.body = form.body.render("body", body)
        return render(request, "encyclopedia/editor.html", {
            "form": form,
            "action": "/edit/" + title
        })
    return FORMAT_CHECK


def new_page(request, title=None):
    form = editorForm()
    if title is not None:
        # Lesser format check that only be used in this particular
        # Function
        if title[0].islower():
            return HttpResponseRedirect(reverse("new-page", kwargs={
                "title": title.capitalize()
            }))
        if util.get_entry(title)["body"]:
            return HttpResponseRedirect(reverse("edit-page", kwargs={
                "title": title
            }))
        body = f"# {title}\r\n\r\n"
        form.title.attrs["autofocus"] = False
        form.body.attrs["autofocus"] = True
    else:
        title = ""
        body = ""
        form.title.attrs["autofocus"] = True
        form.body.attrs["autofocus"] = False
    form.title = form.title.render("title", title)
    form.body = form.body.render("body", body)
    return render(request, "encyclopedia/editor.html", {
        "form": form,
        "action": "/edit/" + title
    })