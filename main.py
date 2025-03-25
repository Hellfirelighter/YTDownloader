from pytubefix import YouTube, Channel, Playlist
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, _tkinter_finder
import requests
from io import BytesIO
import os
import sys
import subprocess
import threading

global urls, download_path
urls = []
download_path = os.path.expanduser("~")


def get_download_path():
    global download_path
    folder = filedialog.askdirectory()
    if folder:
        download_path = folder


def setup_ui(window):
    def load_image_from_url(url, max_width=390):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            width, height = img.size
            aspect_ratio = height / width
            new_width = min(max_width, width)
            new_height = int(new_width * aspect_ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Помилка завантаження зображення: {e}")
            return None

    def extract_formats(obj):
        try:
            lst = [
                f"{s.type}{'-only' if not s.is_progressive else ''}\t {s.resolution or s.abr}\t {f'{s.fps} fps' if s.type == 'video' else ''}\t {int(s.filesize / (1024 * 1024))}MB"
                for s in obj.streams if s.filesize]
            if lst:
                ComboBox1['values'] = lst
                cb_default_text.set(lst[0])
                img = load_image_from_url(obj.thumbnail_url)
                if img:
                    ImgLabel1.config(image=img)
                    ImgLabel1.image = img
                window.geometry('400x480')
                window.title(obj.title)
            else:
                window.title('No valid formats found')
        except Exception:
            window.title('Invalid URL')

    def download_url_list(lst):
        global download_path
        for n, url in enumerate(lst):
            try:
                Button1['state'] = DISABLED
                window.title(f'Downloading {n + 1}/{len(lst)} - {url}')
                yt = YouTube(url, on_progress_callback=on_progress)
                stream_index = ComboBox1.current()
                if stream_index >= 0:
                    yt.streams[stream_index].download(download_path)
                else:
                    raise Exception("No stream selected")
                if n == len(lst) - 1:
                    messagebox.showinfo(title='Done!', message='File(s) downloaded successfully')
            except Exception as e:
                window.title(f'Download failed: {e}')
        Button1['state'] = ACTIVE

    def on_paste(event):
        global urls
        url = window.clipboard_get()
        ComboBox1['values'] = []
        urls.clear()
        try:
            if 'youtube.com/c' in url:
                c = Channel(url)
                extract_formats(c.videos[0])
                urls = c.video_urls
            elif 'youtube.com/playlist' in url:
                p = Playlist(url)
                extract_formats(p.videos[0])
                urls = p.video_urls
            else:
                yt = YouTube(url)
                extract_formats(yt)
                urls.append(url)
        except Exception:
            window.title('Invalid URL')

    def on_start():
        if urls:
            get_download_path()
            threading.Thread(target=download_url_list, args=(urls,)).start()

    def on_open():
        global download_path
        if sys.platform == "win32":
            subprocess.Popen(f'explorer "{download_path}"')
        else:
            subprocess.Popen(["xdg-open", download_path])

    def on_progress(stream, chunk, bytes_remaining):
        size = stream.filesize
        current_progress.set(int(((size - bytes_remaining) / size) * 100))

    def show_contextmenu(event):
        e_widget = event.widget
        context_menu = ttk.Menu(window, tearoff=0)
        context_menu.add_command(label="Cut", command=lambda: e_widget.event_generate("<<Cut>>"))
        context_menu.add_command(label="Copy", command=lambda: e_widget.event_generate("<<Copy>>"))
        context_menu.add_command(label="Paste", command=lambda: e_widget.event_generate("<<Paste>>"))
        context_menu.add_separator()
        context_menu.add_command(label="Select all", command=lambda: e_widget.select_range(0, 'end'))
        context_menu.tk.call("tk_popup", context_menu, event.x_root, event.y_root)

    current_url = ttk.StringVar()
    Edit1 = ttk.Entry(window, bootstyle='default', textvariable=current_url)
    Edit1.bind("<<Paste>>", on_paste)
    Edit1.bind("<Button-3><ButtonRelease-3>", show_contextmenu)
    Edit1.pack(fill=X, padx=5, pady=(10, 5))

    cb_default_text = ttk.StringVar()
    ComboBox1 = ttk.Combobox(window, state='readonly', bootstyle='default', textvariable=cb_default_text)
    ComboBox1.pack(fill=X, padx=5, pady=5)

    ImgLabel1 = ttk.Label(window)
    ImgLabel1.pack(fill=X, padx=5)

    current_progress = ttk.IntVar()
    ProgressBar1 = ttk.Floodgauge(window, bootstyle="danger", mask='{} %', variable=current_progress)
    ProgressBar1.pack(fill=X, padx=5, pady=5)

    Button1 = ttk.Button(window, text='Start', bootstyle='danger-outline', command=on_start)
    Button1.pack(side=LEFT, fill=X, padx=5, expand=True)

    Button2 = ttk.Button(window, text='Open', bootstyle='secondary-outline', command=on_open)
    Button2.pack(side=RIGHT, fill=X, padx=5, expand=True)


if __name__ == "__main__":
    app = ttk.Window()
    app.geometry('400x200')
    app.resizable(False, False)
    app.eval('tk::PlaceWindow . center')
    app.title('YouTube Downloader')
    app.style.theme_use('darkly')
    app.iconphoto(True, ttk.PhotoImage(file=os.path.join(os.path.dirname(__file__), 'mainicon.png')))
    setup_ui(window=app)
    app.mainloop()
