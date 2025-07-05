import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
import requests
import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading

# Configuration
WEATHER_API_KEY = "a00d096273d746d59ed151955250507"
RECORD_DURATION = 5  # seconds
SAMPLE_RATE = 44100  # Hz

class WeatherNotifier:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.recording_animation = False
        self.animation_thread = None
        self.setup_styles()
        
    def setup_styles(self):
        """Configure custom styles for 3D effects and modern look"""
        style = ttk.Style()
        
        # Main frame style with shadow effect
        style.configure("Main.TFrame", background="#f8f9fa", relief="raised", borderwidth=2)
        
        # Button styles with 3D effect
        style.configure("Accent.TButton", 
                      font=("Segoe UI", 12, "bold"),
                      foreground="white",
                      background="#4285f4",
                      borderwidth=1,
                      relief="raised",
                      padding=10)
        style.map("Accent.TButton",
                background=[('active', '#3367d6'), ('pressed', '#2a56c4')],
                relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        # Entry style
        style.configure("Modern.TEntry",
                      foreground="#333333",
                      fieldbackground="white",
                      bordercolor="#dfe1e5",
                      lightcolor="#dfe1e5",
                      darkcolor="#dfe1e5",
                      padding=8,
                      relief="flat")
        
        # Label styles
        style.configure("Title.TLabel",
                       font=("Segoe UI", 20, "bold"),
                       foreground="#202124",
                       background="#f8f9fa")
        
        style.configure("Subtitle.TLabel",
                      font=("Segoe UI", 10),
                      foreground="#5f6368",
                      background="#f8f9fa")
        
        # Status label style with animation capability
        style.configure("Status.TLabel",
                      font=("Segoe UI", 9),
                      foreground="#5f6368",
                      background="#f8f9fa")
        
    def setup_ui(self):
        """Initialize the professional user interface"""
        self.root.title("Live Weather Notifier AI Pro")
        self.root.geometry("700x550")
        self.root.config(bg="#f8f9fa")
        self.root.resizable(False, False)
        
        # Set window icon (replace with your own icon if available)
        try:
            self.root.iconbitmap("weather_icon.ico")
        except:
            pass
        
        # Main container with shadow effect
        main_container = ttk.Frame(self.root, style="Main.TFrame")
        main_container.pack(pady=30, padx=30, fill=tk.BOTH, expand=True)
        
        # Header section
        header_frame = ttk.Frame(main_container, style="Main.TFrame")
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Title with weather icon
        title_label = ttk.Label(
            header_frame,
            text="🌤️ Live Weather Notifier AI",
            style="Title.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # Current time display
        self.time_label = ttk.Label(
            header_frame,
            text=datetime.now().strftime("%H:%M %p"),
            style="Subtitle.TLabel"
        )
        self.time_label.pack(side=tk.RIGHT)
        self.update_clock()
        
        # Divider
        ttk.Separator(main_container, orient="horizontal").pack(fill=tk.X, padx=20, pady=10)
        
        # Instruction section
        instruction_frame = ttk.Frame(main_container)
        instruction_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        instruction_label = ttk.Label(
            instruction_frame,
            text="Click the microphone button and clearly say your city name (e.g., 'London' or 'New York')",
            style="Subtitle.TLabel"
        )
        instruction_label.pack()
        
        # Voice input section with animation
        self.voice_frame = ttk.Frame(main_container)
        self.voice_frame.pack(pady=(10, 20))
        
        # Animated microphone button
        self.weather_btn = ttk.Button(
            self.voice_frame,
            text="🎤  Get Weather",
            command=self.start_weather_process,
            style="Accent.TButton"
        )
        self.weather_btn.pack(pady=10, ipadx=20, ipady=10)
        
        # Voice visualization placeholder
        self.visualization_frame = ttk.Frame(self.voice_frame, height=50)
        self.visualization_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Weather display area
        self.weather_display = ttk.Frame(main_container)
        self.weather_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Status bar with progress capability
        self.status_frame = ttk.Frame(main_container)
        self.status_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="Ready",
            style="Status.TLabel"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Footer
        footer_frame = ttk.Frame(main_container)
        footer_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        footer_label = ttk.Label(
            footer_frame,
            text="© 2023 Weather Notifier AI Pro | Powered by WeatherAPI",
            style="Status.TLabel"
        )
        footer_label.pack(side=tk.RIGHT)
        
        # Initialize empty weather display
        self.clear_weather_display()
    
    def update_clock(self):
        """Update the time display every minute"""
        self.time_label.config(text=datetime.now().strftime("%H:%M %p"))
        self.root.after(60000, self.update_clock)
    
    def clear_weather_display(self):
        """Clear the weather display area"""
        for widget in self.weather_display.winfo_children():
            widget.destroy()
        
        placeholder = ttk.Label(
            self.weather_display,
            text="Your weather report will appear here",
            style="Subtitle.TLabel"
        )
        placeholder.pack(expand=True)
    
    def update_status(self, message, color="#5f6368"):
        """Update the status label with colored text"""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
    
    def start_weather_process(self):
        """Start the weather process in a separate thread"""
        if self.animation_thread and self.animation_thread.is_alive():
            return
            
        self.animation_thread = threading.Thread(target=self.process_weather_request)
        self.animation_thread.start()
    
    def show_recording_animation(self):
        """Show voice recording animation"""
        self.recording_animation = True
        self.visualization_frame.config(relief="sunken", borderwidth=1)
        
        for i in range(10):
            if not self.recording_animation:
                break
                
            # Create simple animation effect
            for child in self.visualization_frame.winfo_children():
                child.destroy()
                
            bars = min(10, i + 1)
            for j in range(bars):
                height = np.random.randint(5, 30)
                bar = tk.Canvas(self.visualization_frame, width=4, height=height, bg="#4285f4", highlightthickness=0)
                bar.pack(side=tk.LEFT, padx=1, fill=tk.Y, expand=True)
            
            time.sleep(0.1)
            self.root.update()
        
        for child in self.visualization_frame.winfo_children():
            child.destroy()
    
    def recommend_outfit(self, temp_c):
        """AI-based outfit suggestions with more details"""
        if temp_c > 30:
            return ("Extreme Heat", 
                   "🥵 Wear lightweight, breathable clothes (cotton/linen).\n"
                   "• Sunglasses and wide-brimmed hat recommended\n"
                   "• Apply sunscreen (SPF 30+)\n"
                   "• Stay hydrated and avoid direct sun")
        elif 25 <= temp_c <= 30:
            return ("Hot Weather",
                   "😎 Light summer clothing recommended\n"
                   "• T-shirts and shorts\n"
                   "• Sandals or breathable shoes\n"
                   "• Sunglasses for eye protection")
        elif 20 <= temp_c < 25:
            return ("Warm Weather",
                   "😊 Comfortable casual wear\n"
                   "• Light shirts or blouses\n"
                   "• Comfortable pants or skirts\n"
                   "• Light jacket for evening")
        elif 15 <= temp_c < 20:
            return ("Mild Weather",
                   "🧥 Layer your clothing\n"
                   "• Long-sleeve shirts\n"
                   "• Light sweater or jacket\n"
                   "• Comfortable pants")
        elif 10 <= temp_c < 15:
            return ("Cool Weather",
                   "🧣 Warmer layers needed\n"
                   "• Sweaters or fleece\n"
                   "• Light to medium jacket\n"
                   "• Long pants")
        elif 0 <= temp_c < 10:
            return ("Cold Weather",
                   "🧤 Bundle up!\n"
                   "• Heavy coat or parka\n"
                   "• Gloves and scarf\n"
                   "• Warm hat and insulated shoes")
        else:
            return ("Extreme Cold",
                   "❄️ Full winter protection required\n"
                   "• Thermal underwear\n"
                   "• Heavy winter coat\n"
                   "• Insulated gloves and boots\n"
                   "• Face protection in windy conditions")
    
    def get_weather(self, city):
        """Fetch weather data from WeatherAPI with enhanced error handling"""
        try:
            self.update_status(f"Connecting to weather service...", "#1a73e8")
            
            url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
            response = requests.get(url, timeout=15)
            data = response.json()
            
            if "error" in data:
                error_msg = f"{data['error']['message']} (Code: {data['error']['code']})"
                self.update_status(f"API Error: {error_msg}", "#d93025")
                messagebox.showerror("API Error", error_msg)
                return None
            
            # Get forecast for temperature chart
            forecast_url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=3&aqi=no&alerts=no"
            forecast_response = requests.get(forecast_url)
            forecast_data = forecast_response.json()
            
            return {
                'city': f"{data['location']['name']}, {data['location']['country']}",
                'temp_c': data['current']['temp_c'],
                'temp_f': data['current']['temp_f'],
                'condition': data['current']['condition']['text'],
                'humidity': data['current']['humidity'],
                'wind_kph': data['current']['wind_kph'],
                'feelslike_c': data['current']['feelslike_c'],
                'icon': data['current']['condition']['icon'],
                'forecast': forecast_data['forecast']['forecastday']
            }
        except requests.exceptions.Timeout:
            self.update_status("Connection timed out", "#d93025")
            messagebox.showerror("Network Error", "Weather service is not responding. Please try again later.")
            return None
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "#d93025")
            messagebox.showerror("Error", f"Failed to fetch weather data: {str(e)}")
            return None
    
    def record_audio(self):
        """Record audio from microphone with visual feedback"""
        self.update_status("🎤 Recording... Speak now", "#1a73e8")
        self.recording_animation = True
        threading.Thread(target=self.show_recording_animation).start()
        
        try:
            recording = sd.rec(
                int(RECORD_DURATION * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype='int16'
            )
            sd.wait()
            self.recording_animation = False
            return recording
        except Exception as e:
            self.recording_animation = False
            self.update_status(f"Recording failed: {str(e)}", "#d93025")
            messagebox.showerror("Hardware Error", f"Microphone issue: {str(e)}")
            return None
    
    def recognize_speech(self, recording):
        """Convert speech to text with improved error handling"""
        self.update_status("🔍 Processing your voice...", "#1a73e8")
        
        filename = "voice_input.wav"
        wav.write(filename, SAMPLE_RATE, recording)
        
        r = sr.Recognizer()
        try:
            with sr.AudioFile(filename) as source:
                audio = r.record(source)
                city = r.recognize_google(audio)
                self.update_status(f"Recognized: {city}", "#0b8043")
                return city
        except sr.UnknownValueError:
            self.update_status("Could not understand audio", "#d93025")
            messagebox.showerror("Recognition Error", "Could not understand your speech. Please try again.")
            return None
        except sr.RequestError as e:
            self.update_status("Speech service unavailable", "#d93025")
            messagebox.showerror("Service Error", f"Could not access speech recognition service: {str(e)}")
            return None
    
    def create_temperature_chart(self, forecast_data):
        """Create a temperature forecast chart"""
        fig, ax = plt.subplots(figsize=(6, 3), dpi=80)
        
        dates = []
        max_temps = []
        min_temps = []
        
        for day in forecast_data:
            date = datetime.strptime(day['date'], "%Y-%m-%d").strftime("%a")
            dates.append(date)
            max_temps.append(day['day']['maxtemp_c'])
            min_temps.append(day['day']['mintemp_c'])
        
        ax.plot(dates, max_temps, marker='o', label='Max Temp (°C)', color='#d62728')
        ax.plot(dates, min_temps, marker='o', label='Min Temp (°C)', color='#1f77b4')
        
        ax.set_ylabel('Temperature (°C)')
        ax.set_title('3-Day Forecast')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        fig.tight_layout()
        
        return fig
    
    def display_weather_report(self, weather_data):
        """Display the weather report with professional layout"""
        for widget in self.weather_display.winfo_children():
            widget.destroy()
        
        # Main weather frame
        main_weather_frame = ttk.Frame(self.weather_display)
        main_weather_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Current weather section
        current_frame = ttk.Frame(main_weather_frame)
        current_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Location and time
        location_label = ttk.Label(
            current_frame,
            text=f"📍 {weather_data['city']}",
            font=("Segoe UI", 14, "bold"),
            foreground="#202124"
        )
        location_label.pack(anchor=tk.W, pady=(0, 5))
        
        time_label = ttk.Label(
            current_frame,
            text=f"⏰ {datetime.now().strftime('%A, %b %d %Y %H:%M %p')}",
            font=("Segoe UI", 10),
            foreground="#5f6368"
        )
        time_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Current conditions
        conditions_frame = ttk.Frame(current_frame)
        conditions_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Temperature display
        temp_frame = ttk.Frame(conditions_frame)
        temp_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        temp_label = ttk.Label(
            temp_frame,
            text=f"{weather_data['temp_c']:.1f}°C",
            font=("Segoe UI", 36, "bold"),
            foreground="#202124"
        )
        temp_label.pack(anchor=tk.W)
        
        feels_like_label = ttk.Label(
            temp_frame,
            text=f"Feels like: {weather_data['feelslike_c']:.1f}°C",
            font=("Segoe UI", 10),
            foreground="#5f6368"
        )
        feels_like_label.pack(anchor=tk.W)
        
        # Weather details
        details_frame = ttk.Frame(conditions_frame)
        details_frame.pack(side=tk.LEFT)
        
        condition_label = ttk.Label(
            details_frame,
            text=f"{weather_data['condition']}",
            font=("Segoe UI", 12),
            foreground="#202124"
        )
        condition_label.pack(anchor=tk.W)
        
        humidity_label = ttk.Label(
            details_frame,
            text=f"💧 Humidity: {weather_data['humidity']}%",
            font=("Segoe UI", 10),
            foreground="#5f6368"
        )
        humidity_label.pack(anchor=tk.W)
        
        wind_label = ttk.Label(
            details_frame,
            text=f"💨 Wind: {weather_data['wind_kph']} km/h",
            font=("Segoe UI", 10),
            foreground="#5f6368"
        )
        wind_label.pack(anchor=tk.W)
        
        # Outfit recommendation
        outfit_type, outfit_details = self.recommend_outfit(weather_data['temp_c'])
        
        outfit_frame = ttk.LabelFrame(
            current_frame,
            text=f"👕 Outfit Recommendation: {outfit_type}",
            padding=(10, 5)
        )
        outfit_frame.pack(fill=tk.X, pady=(10, 0))
        
        outfit_label = ttk.Label(
            outfit_frame,
            text=outfit_details,
            font=("Segoe UI", 10),
            foreground="#202124"
        )
        outfit_label.pack(anchor=tk.W)
        
        # Forecast chart
        forecast_frame = ttk.Frame(main_weather_frame, width=250)
        forecast_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        
        chart_title = ttk.Label(
            forecast_frame,
            text="3-Day Temperature Forecast",
            font=("Segoe UI", 10, "bold"),
            foreground="#202124"
        )
        chart_title.pack()
        
        fig = self.create_temperature_chart(weather_data['forecast'])
        canvas = FigureCanvasTkAgg(fig, master=forecast_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def process_weather_request(self):
        """Main workflow: Record → Recognize → Fetch → Display"""
        self.weather_btn.config(state=tk.DISABLED)
        self.clear_weather_display()
        
        try:
            # Step 1: Record audio
            recording = self.record_audio()
            if recording is None:
                self.weather_btn.config(state=tk.NORMAL)
                return
            
            # Step 2: Recognize speech
            city = self.recognize_speech(recording)
            if not city:
                self.weather_btn.config(state=tk.NORMAL)
                return
            
            # Step 3: Fetch weather data
            self.update_status(f"⏳ Fetching weather for {city}...", "#1a73e8")
            weather_data = self.get_weather(city)
            if not weather_data:
                self.weather_btn.config(state=tk.NORMAL)
                return
            
            # Step 4: Display results
            self.display_weather_report(weather_data)
            self.update_status("✅ Weather report ready! Click to refresh.", "#0b8043")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "#d93025")
            messagebox.showerror("Unexpected Error", f"An error occurred: {str(e)}")
        finally:
            self.weather_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set Windows 10/11 theme if available
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = WeatherNotifier(root)
    root.mainloop()