import tkinter as tk
import urllib.request
import re
import os
from typing import List
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

api_key = os.environ.get('API_KEY')

class SearchResult:
    def __init__(self, title: str, link: str):
        self.title = title
        self.link = link

def fetch_results(keyword: str, start: int) -> List[SearchResult]:
    params = {
        "api_key": api_key,
        "engine": "google",
        "q": keyword,
        "hl": "en"
    }
    if start:
        params["start"] = str(start)
    search = GoogleSearch(params)
    results = search.get_dict()
    search_results = []
    for i in range(10):
        try:
            title = results['organic_results'][i]['title']
            link = results['organic_results'][i]['link']
            search_results.append(SearchResult(title, link))
        except:
            pass
    return search_results


def extract_pdf_link(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith('.pdf'):
            return href
    return ''



def display_results(search_results: List[SearchResult], append: bool = False) -> None:
    global result_checkbuttons
    if not append:
        result_text.delete("1.0", "end")
        result_checkbuttons = []
    for i, result in enumerate(search_results):
        var = tk.BooleanVar()
        var.set(False)
        checkbutton = tk.Checkbutton(result_text, variable=var)
        result_checkbuttons.append(var)
        result_text.window_create("end", window=checkbutton)
        result_text.insert("end", " ")
        result_text.insert("end", f"{result.title}")
        if result.link.endswith('.pdf'):
            result_text.insert("end", f"\nURL: {result.link}\n\n")
        else:
            pdf_link = extract_pdf_link(result.link)
            if pdf_link:
                result_text.insert("end", f"\nPDF URL: {pdf_link}\n\n")


def clear_results() -> None:
    global search_results, current_start, result_checkbuttons
    search_results = []
    current_start = 0
    result_text.delete("1.0", "end")
    for checkbutton in result_checkbuttons:
        checkbutton.set(False)
    result_checkbuttons = []


def download_selected() -> None:
    selected_results = []
    for i, result in enumerate(search_results):
        if result_checkbuttons[i].get():
            selected_results.append(result)
    for result in selected_results:
        href = extract_pdf_link(result.link)
        if href:
            file_name = result.title.replace("/", "-") + ".pdf"
            urllib.request.urlretrieve(href, file_name)


root = tk.Tk()
root.title("Google Scholar Search")
root.geometry("500x500")

keyword_label = tk.Label(root, text="Keyword:")
keyword_label.pack()

keyword_entry = tk.Entry(root)
keyword_entry.pack()

search_button = tk.Button(root, text="Search", command=lambda: display_results(fetch_results(keyword_entry.get(), 0)))
search_button.pack()

result_text = tk.Text(root)
result_text.pack(expand=True, fill="both")

clear_button = tk.Button(root, text="Clear list", command=clear_results)
clear_button.pack()

search_results: List[SearchResult] = []
current_start: int = 0
result_checkbuttons: List[tk.BooleanVar] = []

download_button = tk.Button(root, text="Download selected", command=download_selected)
download_button.pack()

root.mainloop()
