from pytube import YouTube, Channel, Playlist
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import os
import sys
import subprocess
import threading

global urls
urls = []


def setup_ui(window):
    def extract_formats(obj):
        lst = []
        try:
            for stream in obj.streams:
                only = ''
                if not stream.is_progressive:
                    only = '-only'
                if stream.type == 'video':
                    lst.append(
                        f'{stream.type}{only}    {stream.resolution}    {stream.fps} fps    {int(stream.filesize / (1024 * 1024))} MB')
                else:
                    lst.append(f'{stream.type}{only}    {stream.abr}    {int(stream.filesize / (1024 * 1024))} MB')
            ComboBox1['values'] = lst
            cb_default_text.set(lst[0])
        except Exception as _ex:
            window.title('URL is not valid...')

    def download_url_list(lst):
        for i, url in enumerate(lst):
            try:
                if Button1['state'] == NORMAL or ACTIVE:
                    Button1['state'] = DISABLED
                window.title(f'YouTube DownLoader {i+1}/{len(lst)} - {url}')
                yt = YouTube(url, on_progress_callback=on_progress, on_complete_callback=on_complete)
                i = ComboBox1.current()
                yt.streams[i].download()
            except Exception as _ex:
                window.title('URL is not valid...')

    def on_paste(event):
        global urls
        url = window.clipboard_get()
        ComboBox1['values'] = []
        urls.clear()
        try:
            if url.startswith('https://www.youtube.com/c'):
                c = Channel(url)
                extract_formats(c.videos[0])
                urls = c.video_urls
            elif url.startswith('https://www.youtube.com/playlist?list='):
                p = Playlist(url)
                extract_formats(p.videos[0])
                urls = p.video_urls
            else:
                yt = YouTube(url)
                extract_formats(yt)
                urls.append(url)
        except Exception as _ex:
            window.title('URL is not valid...')

    def on_start():
        t = threading.Thread(target=download_url_list, args=(urls,), )
        t.start()

    def on_open():
        subprocess.Popen(r'explorer "{dir}"'.format(dir=os.path.dirname(sys.argv[0]).replace('/', '\\')))

    def on_complete(stream, file_path):
        current_progress.set(0)
        Button1['state'] = ACTIVE
        messagebox.showinfo(title='Done!', message='file(s) was successfully downloaded')

    def on_progress(stream, chunk, bytes_remaining):
        size = stream.filesize
        p = int(float(abs(bytes_remaining - size) / size) * float(100))
        current_progress.set(p)

    current_url = ttk.StringVar()
    Edit1 = ttk.Entry(window, bootstyle='default', textvariable=current_url)
    Edit1.bind("<<Paste>>", on_paste)
    Edit1.pack(fill=X, padx=5, pady=5)
    cb_default_text = ttk.StringVar()
    ComboBox1 = ttk.Combobox(window, state='readonly', bootstyle='default', textvariable=cb_default_text)
    ComboBox1.pack(fill=X, padx=5, pady=5)
    current_progress = ttk.IntVar()
    current_progress.set(100)
    ProgressBar1 = ttk.Floodgauge(window, bootstyle="danger", mask='{} %', variable=current_progress)
    ProgressBar1.pack(fill=X, padx=5, pady=5)
    Button1 = ttk.Button(window, text='Start', bootstyle='danger-outline', command=lambda: on_start())
    Button1.pack(side=LEFT, fill=X, padx=5, expand=True)
    Button2 = ttk.Button(window, text='Open', bootstyle='secondary-outline', command=lambda: on_open())
    Button2.pack(side=RIGHT, fill=X, padx=5, expand=True)


if __name__ == "__main__":
    app = ttk.Window()
    app.geometry('400x200')
    app.resizable(False, False)
    app.eval('tk::PlaceWindow . center')
    app.title('YouTube DownLoader')
    app.style.theme_use('darkly')
    # app.iconbitmap('mainicon.ico')
    app.iconphoto(True, ttk.PhotoImage(file=os.path.dirname(__file__)+'/mainicon.png'))
    setup_ui(window=app)
    # app.protocol("WM_DELETE_WINDOW", on_app_closing)
    app.mainloop()
