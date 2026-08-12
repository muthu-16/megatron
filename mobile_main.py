import kivy
kivy.require('2.3.0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.utils import get_color_from_hex
import threading
import time
import math
import random

try:
    from jnius import autoclass, cast
    from android.permissions import request_permissions, Permission
    ANDROID_MODE = True
except ImportError:
    ANDROID_MODE = False

# Mark-L Theme Colors
C_BG = get_color_from_hex("#00060a")
C_PANEL = get_color_from_hex("#010d14")
C_BORDER = get_color_from_hex("#0d3347")
C_PRI = get_color_from_hex("#00d4ff")
C_TEXT = get_color_from_hex("#d8f8ff")
C_TEXT_DIM = get_color_from_hex("#3a8a9a")

class RoundedPanel(BoxLayout):
    def __init__(self, bg_color=C_PANEL, radius=[20], **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class BubbleLabel(Label):
    def __init__(self, bg_color, is_user=False, **kwargs):
        super().__init__(**kwargs)
        self.color = C_TEXT
        self.font_size = '16sp'
        self.size_hint_y = None
        self.halign = 'left'
        self.valign = 'top'
        self.padding = (20, 20)
        self.bg_color = bg_color
        # Adjust border radius based on sender
        r = [25, 25, 5, 25] if is_user else [25, 25, 25, 5]
        
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=r)
            if not is_user:
                Color(*C_BORDER)
                self.line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 25, 25, 25, 5), width=1)
            else:
                self.line = None
                
        self.bind(pos=self.update_rect, size=self.update_rect, texture_size=self.update_texture)
        
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        if self.line:
            self.line.rounded_rectangle = (self.x, self.y, self.width, self.height, 25, 25, 25, 5)

    def update_texture(self, *args):
        self.size = self.texture_size

class AnimatedWaveform(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bars = [0.1] * 10
        self.target_bars = [0.1] * 10
        self.state = "idle"
        Clock.schedule_interval(self.update_waveform, 1.0 / 30.0)

    def idle_animate(self):
        self.state = "idle"
        self.target_bars = [0.1] * 10

    def record_animate(self):
        self.state = "record"
        
    def update_waveform(self, dt):
        if self.state == "record":
            self.target_bars = [random.uniform(0.3, 0.9) for _ in range(10)]
        elif self.state == "idle":
            t = time.time() * 3
            self.target_bars = [0.1 + math.sin(t + i) * 0.08 for i in range(10)]

        for i in range(10):
            self.bars[i] += (self.target_bars[i] - self.bars[i]) * 0.2

        self.canvas.clear()
        with self.canvas:
            Color(*C_PRI)
            width = self.width
            height = self.height
            bar_w = width / 15
            spacing = bar_w * 0.5
            start_x = self.x + (width - (10 * bar_w + 9 * spacing)) / 2
            
            for i, val in enumerate(self.bars):
                h = height * val
                x = start_x + i * (bar_w + spacing)
                y = self.y + (height - h) / 2
                RoundedRectangle(pos=(x, y), size=(bar_w, h), radius=[bar_w/2])

class PTTButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0,0,0,0) # transparent to use canvas
        self.bg_color = C_PRI
        with self.canvas.before:
            Color(*C_BORDER)
            self.line_border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 25), width=2)
            self.c = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[25])
        self.bind(pos=self.update_rect, size=self.update_rect, state=self.update_state)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.line_border.rounded_rectangle = (self.x, self.y, self.width, self.height, 25)

    def update_state(self, instance, value):
        if value == 'down':
            self.c.rgba = (0, 0.5, 0.6, 1) # Darker cyan
        else:
            self.c.rgba = self.bg_color

class MobileUI(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_box = BoxLayout(orientation='vertical', padding=[15, 40, 15, 20], spacing=20)
        
        # Header
        header = Label(text="M E G A T R O N", size_hint_y=0.08, font_size='20sp', color=C_PRI, bold=True)
        main_box.add_widget(header)
        
        # Chat Log
        self.scroll = ScrollView(size_hint_y=0.65)
        self.log_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=[10,10,10,10])
        self.log_box.bind(minimum_height=self.log_box.setter('height'))
        self.scroll.add_widget(self.log_box)
        main_box.add_widget(self.scroll)
        
        # Waveform Container
        wave_box = BoxLayout(size_hint_y=0.15, padding=[40, 0, 40, 0])
        self.waveform = AnimatedWaveform()
        wave_box.add_widget(self.waveform)
        main_box.add_widget(wave_box)
        
        # Controls
        controls = BoxLayout(size_hint_y=0.12, padding=[20, 0, 20, 0])
        self.ptt_btn = PTTButton(
            text="🎙 PUSH TO TALK", 
            font_size='18sp',
            bold=True,
            color=C_BG
        )
        self.ptt_btn.bind(on_press=self.start_voice)
        controls.add_widget(self.ptt_btn)
        main_box.add_widget(controls)
        
        self.add_widget(main_box)
        self.add_message("System", "Megatron Mobile initialized.\nListening for 'Megatron' wake word...")

    def add_message(self, sender, text):
        box = BoxLayout(orientation='horizontal', size_hint_y=None, padding=[0,0,0,0])
        lbl = BubbleLabel(
            bg_color=C_BORDER if sender == "User" else C_PANEL,
            is_user=(sender=="User"),
            text=f"{text}"
        )
        if sender == "User":
            box.add_widget(Widget()) # spacer left
            box.add_widget(lbl)
        else:
            box.add_widget(lbl)
            box.add_widget(Widget()) # spacer right
            
        box.bind(minimum_height=box.setter('height'))
        lbl.bind(texture_size=lambda instance, size: setattr(box, 'height', size[1]))
        
        self.log_box.add_widget(box)
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    def start_voice(self, instance):
        self.ptt_btn.text = "LISTENING..."
        self.waveform.record_animate()
        threading.Thread(target=self._mock_voice_process).start()

    def _mock_voice_process(self):
        time.sleep(2.5) # Simulate listening/processing
        Clock.schedule_once(lambda dt: self.process_command("call noni"))

    def process_command(self, command):
        self.ptt_btn.text = "🎙 PUSH TO TALK"
        self.waveform.idle_animate()
        self.add_message("User", command)
        
        cmd_lower = command.lower()
        if "call" in cmd_lower:
            name = cmd_lower.replace("call", "").strip()
            self.make_call(name)
        elif "tell" in cmd_lower or "message" in cmd_lower:
            self.send_sms("Noni", "I will be there in 5 minutes.")

    # Native Android Integrations via Pyjnius
    def make_call(self, contact_name):
        if not ANDROID_MODE:
            self.add_message("Megatron", f"[SIMULATION] Initiating secure connection to contact: {contact_name.title()}...")
            return
            
        try:
            Context = autoclass('android.content.Context')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            # Exact Match Logic simulation
            intent = Intent(Intent.ACTION_CALL)
            intent.setData(Uri.parse("tel:1234567890"))
            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            currentActivity.startActivity(intent)
            self.add_message("Megatron", f"Calling exact match for {contact_name.title()}...")
        except Exception as e:
            self.add_message("Megatron", f"System Failure: Unable to establish call path.\nError: {str(e)}")

    def send_sms(self, contact_name, message):
        if not ANDROID_MODE:
            self.add_message("Megatron", f"[SIMULATION] Sending encrypted transmission to {contact_name.title()}:\n'{message}'")
            return
            
        try:
            SmsManager = autoclass('android.telephony.SmsManager')
            manager = SmsManager.getDefault()
            manager.sendTextMessage("1234567890", None, message, None, None)
            self.add_message("Megatron", f"Transmission delivered successfully to {contact_name.title()}.")
        except Exception as e:
            self.add_message("Megatron", f"System Failure: Transmission blocked.\nError: {str(e)}")

class MegatronApp(App):
    def build(self):
        Window.clearcolor = C_BG
        if ANDROID_MODE:
            request_permissions([
                Permission.RECORD_AUDIO,
                Permission.READ_CONTACTS,
                Permission.CALL_PHONE,
                Permission.SEND_SMS
            ])
        return MobileUI()

if __name__ == '__main__':
    # Force phone-like window size on desktop for testing
    Window.size = (400, 750)
    MegatronApp().run()
