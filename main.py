import tkinter as tk
from tkinter import filedialog, ttk
import vlc
import os
import platform

class MediaPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("VibeCast")
        root.iconbitmap(default="favicon.ico")
        self.root.geometry("1024x768")  # Увеличенный размер окна
        self.root.state('zoomed')  # Развернуть на весь экран
        
        # Инициализация VLC
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        
        # Переменные
        self.is_playing = False
        self.is_paused = False
        self.current_media = None
        self.playlist = []
        self.current_playlist_index = -1
        self.repeat = False
        
        # Создание интерфейса
        self.create_ui()
        
    def create_ui(self):
        # Основной фрейм для видео (занимает 80% высоты окна)
        self.video_frame = tk.Frame(self.root, bg='black')
        self.video_frame.pack(fill=tk.BOTH, expand=True)
        
        # Нижняя панель управления
        control_panel = tk.Frame(self.root)
        control_panel.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        # Левая часть панели (кнопки управления)
        left_control = tk.Frame(control_panel)
        left_control.pack(side=tk.LEFT)
        
        # Кнопки управления (увеличенные)
        btn_width = 8
        btn_font = ('Arial', 10)
        
        self.play_btn = tk.Button(left_control, text="▶ Играть", width=btn_width, 
                                 font=btn_font, command=self.play)
        self.play_btn.pack(side=tk.LEFT, padx=2)
        
        self.pause_btn = tk.Button(left_control, text="⏸ Пауза", width=btn_width, 
                                  font=btn_font, command=self.pause)
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = tk.Button(left_control, text="⏹ Стоп", width=btn_width, 
                                 font=btn_font, command=self.stop)
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        self.repeat_btn = tk.Button(left_control, text="🔁 Повтор", width=btn_width, 
                                   font=btn_font, command=self.toggle_repeat)
        self.repeat_btn.pack(side=tk.LEFT, padx=2)
        
        self.open_btn = tk.Button(left_control, text="📂 Открыть", width=btn_width, 
                                 font=btn_font, command=self.open_file)
        self.open_btn.pack(side=tk.LEFT, padx=2)
        
        # Правая часть панели (громкость)
        right_control = tk.Frame(control_panel)
        right_control.pack(side=tk.RIGHT)
        
        # Регулятор громкости (увеличенный)
        self.volume_label = tk.Label(right_control, text="🔊 Громкость", font=btn_font)
        self.volume_label.pack(side=tk.LEFT)
        
        self.volume_slider = ttk.Scale(right_control, from_=0, to=100, orient=tk.HORIZONTAL, 
                                     command=self.set_volume, length=150)
        self.volume_slider.set(100)
        self.volume_slider.pack(side=tk.LEFT, padx=5)
        
        # Метка текущего файла (увеличенный шрифт)
        self.current_file_label = tk.Label(self.root, text="Файл не выбран", 
                                         anchor='w', font=('Arial', 10))
        self.current_file_label.pack(fill=tk.X, side=tk.BOTTOM, before=control_panel)
        
        # Плейлист (компактный, под видео)
        self.playlist_box = tk.Listbox(self.root, height=6, font=('Arial', 10))
        self.playlist_box.pack(fill=tk.BOTH, before=self.current_file_label)
        self.playlist_box.bind('<<ListboxSelect>>', self.playlist_select)
        
        # Установка громкости при запуске
        self.player.audio_set_volume(100)
        
        # Обновление ID окна после его создания
        self.root.after(100, self.set_vlc_window)
    
    def set_vlc_window(self):
        if platform.system() == 'Windows':
            self.player.set_hwnd(self.video_frame.winfo_id())
        else:
            self.player.set_xwindow(self.video_frame.winfo_id())
    
    def play(self):
        if not self.is_playing and self.playlist:
            if self.current_playlist_index == -1:
                self.play_media(0)
            else:
                self.player.play()
                self.is_playing = True
                self.is_paused = False
        elif self.is_paused:
            self.player.play()
            self.is_paused = False
            self.is_playing = True
    
    def pause(self):
        if self.is_playing and not self.is_paused:
            self.player.pause()
            self.is_paused = True
            self.is_playing = False
    
    def stop(self):
        if self.is_playing or self.is_paused:
            self.player.stop()
            self.is_playing = False
            self.is_paused = False
    
    def toggle_repeat(self):
        self.repeat = not self.repeat
        if self.repeat:
            self.repeat_btn.config(relief=tk.SUNKEN, bg='#d9d9d9')
        else:
            self.repeat_btn.config(relief=tk.RAISED, bg='SystemButtonFace')
    
    def set_volume(self, volume):
        self.player.audio_set_volume(int(float(volume)))
    
    def open_file(self):
        filetypes = [
            ("Медиафайлы", "*.mp3 *.mp4 *.avi *.mkv *.mov *.wmv *.flv *.m3u *.m3u8"),
            ("Плейлисты", "*.m3u *.m3u8"),
            ("Все файлы", "*.*")
        ]
        
        filenames = filedialog.askopenfilenames(title="Выберите файл или плейлист", 
                                              filetypes=filetypes)
        
        if filenames:
            if filenames[0].lower().endswith(('.m3u', '.m3u8')):
                self.load_playlist(filenames[0])
            else:
                self.playlist = list(filenames)
                self.update_playlist_box()
                self.play_media(0)
    
    def load_playlist(self, playlist_path):
        try:
            with open(playlist_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.playlist = []
            for line in lines:
                line = line.strip()
                if not line.startswith('#') and line:
                    if not os.path.isabs(line):
                        playlist_dir = os.path.dirname(playlist_path)
                        line = os.path.join(playlist_dir, line)
                    self.playlist.append(line)
            
            if self.playlist:
                self.update_playlist_box()
                self.play_media(0)
            else:
                self.current_file_label.config(text="Плейлист пуст")
        except Exception as e:
            self.current_file_label.config(text=f"Ошибка загрузки: {str(e)}")
    
    def update_playlist_box(self):
        self.playlist_box.delete(0, tk.END)
        for item in self.playlist:
            name = os.path.basename(item)
            self.playlist_box.insert(tk.END, name[:40] + "..." if len(name) > 40 else name)
    
    def play_media(self, index):
        if 0 <= index < len(self.playlist):
            media_path = self.playlist[index]
            self.current_media = self.instance.media_new(media_path)
            self.player.set_media(self.current_media)
            
            self.player.play()
            self.is_playing = True
            self.is_paused = False
            self.current_playlist_index = index
            name = os.path.basename(media_path)
            self.current_file_label.config(text=f"Сейчас: {name[:50]}{'...' if len(name) > 50 else ''}")
            
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.selection_set(index)
            self.playlist_box.see(index)
            
            self.root.after(1000, self.check_end_of_media)
    
    def playlist_select(self, event):
        if not self.playlist_box.curselection():
            return
        
        index = self.playlist_box.curselection()[0]
        if index != self.current_playlist_index:
            self.play_media(index)
    
    def check_end_of_media(self):
        if self.is_playing:
            state = self.player.get_state()
            
            if state == vlc.State.Ended:
                self.is_playing = False
                
                if self.repeat:
                    self.play_media(self.current_playlist_index)
                elif self.current_playlist_index + 1 < len(self.playlist):
                    self.play_media(self.current_playlist_index + 1)
                else:
                    self.current_file_label.config(text="Воспроизведение завершено")
            
            self.root.after(1000, self.check_end_of_media)

if __name__ == "__main__":
    root = tk.Tk()
    player = MediaPlayer(root)
    root.mainloop()