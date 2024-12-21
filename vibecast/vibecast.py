import tkinter as tk
from tkinter import filedialog
import vlc

class MediaPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("VibeCast")
        root.iconbitmap(default="favicon.ico")
        self.master.geometry("800x600")

        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.current_media = None  # Переменная для хранения текущего медиафайла

        self.create_widgets()

    def create_widgets(self):
        self.video_frame = tk.Frame(self.master)
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.video_frame, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Убрана метка для отображения длительности

        self.play_button = tk.Button(self.master, text="Воспроизвести", command=self.play)
        self.play_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.master, text="Пауза", command=self.pause)
        self.pause_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.master, text="Стоп", command=self.stop)
        self.stop_button.pack(side=tk.LEFT)

        self.repeat_button = tk.Button(self.master, text="Повтор", command=self.repeat)
        self.repeat_button.pack(side=tk.LEFT)

        self.open_button = tk.Button(self.master, text="Открыть", command=self.open_file)
        self.open_button.pack(side=tk.LEFT)

        # Ползунок громкости
        self.volume_scale = tk.Scale(self.master, from_=0, to=100, orient=tk.HORIZONTAL, label="Громкость")
        self.volume_scale.set(100)  # Установить начальную громкость на максимум
        self.volume_scale.pack(side=tk.RIGHT, padx=10, pady=10)
        self.volume_scale.bind("<Motion>", self.change_volume)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Медиафайлы", "*.mp4;*.mkv;*.mov;*.wmv;*.mp3;*.wav;*.avi")])
        if file_path:
            self.current_media = self.vlc_instance.media_new(file_path)
            self.player.set_media(self.current_media)
            self.player.set_hwnd(self.canvas.winfo_id())

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def repeat(self):
        if self.current_media:
            self.player.set_media(self.current_media)
            self.player.play()

    def change_volume(self, event):
        volume = self.volume_scale.get()
        self.player.audio_set_volume(volume)

if __name__ == "__main__":
    root = tk.Tk()
    media_player = MediaPlayer(root)
    root.mainloop()