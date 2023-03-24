import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title and its formatted title
    as written in the entry file. If no such entry exists, the function 
    returns None and its title.
    """

    # Check if file exist
    files = list_entries()
    for file in files:
        if title.lower() == file.lower():
            title = file
            break

    try:
        f = default_storage.open(f"entries/{title}.md")
        return {"title": title,
                "body": f.read().decode("utf-8")}
    except FileNotFoundError:
        return {"title": title, "body": None}

