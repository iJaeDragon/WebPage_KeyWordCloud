import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel, Label
import threading
import requests
from bs4 import BeautifulSoup
from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import webbrowser

# 결과 이미지를 저장할 디렉터리 경로
result_dir = './result'

# Okt 객체 초기화
okt = Okt()

def fetch_urls(urls):
    texts = []
    for url in urls:
        if not url.startswith(('http://', 'https://')):
            continue
        try:
            response = requests.get(url.strip())
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                texts.append(' '.join([p.text for p in soup.find_all('p')]))
        except Exception as e:
            print(f"Failed to fetch {url}: {str(e)}")
    return texts

def generate_ngrams(words, n=2):
    ngrams = zip(*[words[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in ngrams]

def analyze_keywords(texts, n=2):
    words = []
    for text in texts:
        words.extend(okt.nouns(text))
    words = [word for word in words if len(word) > 1]

    ngrams = generate_ngrams(words, n)
    return Counter(ngrams)

def create_and_save_wordcloud(counter, file_path):
    # WordCloud 객체 생성 시 이미지 크기를 늘립니다.
    wordcloud = WordCloud(font_path='./ttf/malgun.ttf', width=800, height=400, background_color='white').generate_from_frequencies(counter)

    # matplotlib의 Figure를 사용하여 워드클라우드를 그립니다.
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    # savefig를 사용하여 이미지를 저장하며, dpi 값을 높여 해상도를 개선합니다.
    plt.savefig(file_path, dpi=300)
    plt.close()

def on_analyze():
    urls = text_input.get('1.0', tk.END).split('\n')
    urls = [url.strip() for url in urls if url.strip()]
    if not urls:
        messagebox.showinfo("Error", "Please enter at least one URL")
        return

    # 결과 디렉터리 확인 및 생성
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    loading_window = Toplevel(root)
    loading_window.title("Loading")
    loading_label = Label(loading_window, text="Analyzing, please wait...")
    loading_label.pack(padx=20, pady=20)
    loading_window.update()

    def background_task():
        texts = fetch_urls(urls)
        if not texts:
            messagebox.showinfo("Error", "Failed to fetch texts from URLs")
            loading_window.destroy()
            return
        counter = analyze_keywords(texts, n=2)
        file_path = os.path.join(result_dir, 'wordcloud.png')

        # 워드클라우드 이미지 저장
        create_and_save_wordcloud(counter, file_path)

        # 백그라운드 스레드에서 이미지 열기
        def open_image():
            webbrowser.open('file://' + os.path.realpath(file_path))
            loading_window.destroy()

        root.after(0, open_image)

    threading.Thread(target=background_task).start()

# GUI setup
root = tk.Tk()
root.title("Keyword Analyzer")

text_input = scrolledtext.ScrolledText(root, height=10)
text_input.pack(pady=10)

analyze_button = tk.Button(root, text="Analyze Keywords", command=on_analyze)
analyze_button.pack(pady=5)

root.mainloop()