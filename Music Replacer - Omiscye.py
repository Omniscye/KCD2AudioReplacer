import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment

def get_durations_from_ogg(folder):
    durations = []
    for file in sorted(os.listdir(folder)):
        if file.lower().endswith(".ogg"):
            full_path = os.path.join(folder, file)
            try:
                audio = AudioSegment.from_file(full_path)
                duration = audio.duration_seconds
                durations.append((file, duration))
            except Exception as e:
                print(f"Error reading {file}: {e}")
    return durations

def slice_and_export(audio_path, durations, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    audio = AudioSegment.from_file(audio_path)
    audio_length = len(audio)
    print(f"Audio length: {audio_length / 1000:.2f}s")

    for name, dur in durations:
        ms = int(dur * 1000)
        if ms >= audio_length:
            print(f"WARNING: {name} duration {ms}ms exceeds audio length. Using full track.")
            segment = audio[:ms]
        else:
            start = random.randint(0, audio_length - ms)
            segment = audio[start:start + ms]
            print(f"Exporting {name} with {ms}ms from {start}ms")

        output_path = os.path.join(output_folder, name)
        try:
            segment.export(output_path, format="ogg", codec="libvorbis", bitrate="192k")
        except Exception as e:
            print(f"Failed to export {name}: {e}")

    messagebox.showinfo("Done", f"Exported {len(durations)} .ogg files to {output_folder}")

def resource_path(relative_path):
    """Get absolute path to resource, works for PyInstaller bundles"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

def run_gui():
    def browse_source():
        folder = filedialog.askdirectory()
        source_var.set(folder)

    def browse_audio():
        file = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3 *.wav *.ogg")])
        audio_var.set(file)

    def browse_output():
        folder = filedialog.askdirectory()
        output_var.set(folder)

    def start():
        source = source_var.get()
        audio = audio_var.get()
        output = output_var.get()
        if not (source and audio and output):
            messagebox.showerror("Missing Info", "Please fill in all fields.")
            return
        durations = get_durations_from_ogg(source)
        if not durations:
            messagebox.showerror("No OGGs Found", "No valid .ogg files found in source folder.")
            return
        slice_and_export(audio, durations, output)

    root = tk.Tk()
    root.title("Audio Replacer")
    
    # Set icon
    icon_path = resource_path("kcd2_icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    else:
        print(f"Icon file not found at: {icon_path}")

    source_var = tk.StringVar()
    audio_var = tk.StringVar()
    output_var = tk.StringVar()

    tk.Label(root, text="Source Folder (OGG files):").grid(row=0, column=0, sticky='w')
    tk.Entry(root, textvariable=source_var, width=50).grid(row=0, column=1)
    tk.Button(root, text="Browse", command=browse_source).grid(row=0, column=2)

    tk.Label(root, text="Audio File (MP3/OGG/WAV):").grid(row=1, column=0, sticky='w')
    tk.Entry(root, textvariable=audio_var, width=50).grid(row=1, column=1)
    tk.Button(root, text="Browse", command=browse_audio).grid(row=1, column=2)

    tk.Label(root, text="Output Folder:").grid(row=2, column=0, sticky='w')
    tk.Entry(root, textvariable=output_var, width=50).grid(row=2, column=1)
    tk.Button(root, text="Browse", command=browse_output).grid(row=2, column=2)

    tk.Button(root, text="Start", command=start, bg="green", fg="white").grid(row=3, column=1, pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()