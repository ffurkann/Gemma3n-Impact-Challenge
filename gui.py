from nicegui import ui, app
import asyncio
from datetime import datetime
import json
import os

from main import make_input_main, ask_gemma, parse_response, update_memory
from emergency_mode import emergency_chat_with_text


class GemmAidUI:
    def __init__(self):
        self.current_mode = "main"
        self.memory_path = "Memory/memory_main.json"

    def setup_ui(self):
        ui.add_head_html('''
        <style>
        .turquoise-gradient {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .chat-gradient {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .user-msg-gradient {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .emergency-simple {
            background: #ffffff;
            border: 3px solid #ff0000;
        }
        .emergency-header {
            background: #ff0000;
        }
        .modern-card {
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .modern-input {
            border-radius: 15px;
            border: 2px solid #e0e0e0;
            transition: all 0.3s ease;
        }
        .modern-input:focus {
            border-color: #11998e;
            box-shadow: 0 0 0 3px rgba(17,153,142,0.1);
        }
        </style>
        ''')

        with ui.header().classes('emergency-header' if self.current_mode == 'emergency' else 'turquoise-gradient'):
            with ui.row().classes('w-full items-center'):
                ui.icon('medical_services', size='2em').classes('text-white')
                ui.label('Gemm-Aid').classes('text-2xl text-white font-bold')
                ui.space()
                with ui.row().classes('gap-2'):
                    self.main_btn = ui.button('Main Mode', on_click=lambda: self.switch_mode('main'),
                                              icon='chat').classes(
                        'bg-white/20 hover:bg-white/30 text-white'
                        if self.current_mode == 'main' else
                        'bg-transparent hover:bg-white/10 text-white/80')
                    self.emergency_btn = ui.button('EMERGENCY', on_click=lambda: self.switch_mode('emergency'),
                                                   icon='emergency').classes(
                        'bg-white text-red-600 font-bold'
                        if self.current_mode == 'emergency' else
                        'bg-transparent hover:bg-white/10 text-white/80')

        with ui.column().classes('w-full min-h-screen').style(
                'background: #f0f0f0' if self.current_mode == 'emergency'
                else 'background: linear-gradient(180deg, #f5f7fa 0%, #e9ecef 100%)'):
            with ui.column().classes('w-full max-w-4xl mx-auto p-4'):
                self.mode_indicator = ui.card().classes(
                    'w-full mb-4 modern-card' if self.current_mode == 'main' else 'w-full max-w-4xl mx-auto mb-4 emergency-simple')
                self.update_mode_indicator()

                chat_classes = ('w-full modern-card chat-gradient'
                                if self.current_mode == 'main'
                                else 'w-full emergency-simple')
                with ui.card().classes(chat_classes).style('height: 400px'):
                    self.chat_container = ui.column().classes('w-full h-full overflow-y-auto p-4')
                    self.display_welcome_message()

                input_classes = ('w-full mt-4 modern-card'
                                 if self.current_mode == 'main'
                                 else 'w-full mt-4 emergency-simple')
                self.input_card = ui.card().classes(input_classes)
                self.setup_input_area()

                if self.current_mode == 'main':
                    with ui.expansion('View Memory', icon='psychology').classes('w-full mt-4 modern-card'):
                        self.memory_viewer = ui.column().classes('w-full')
                        self.load_memory_display()

    def update_mode_indicator(self):
        self.mode_indicator.clear()
        with self.mode_indicator:
            if self.current_mode == 'main':
                with ui.row().classes('items-center p-4'):
                    ui.icon('chat', size='lg').classes('text-teal-600')
                    with ui.column():
                        ui.label('Main Mode - Text Input').classes('text-lg font-semibold text-gray-800')
                        ui.label('Ask about symptoms for personalized advice').classes('text-gray-600')
            else:
                with ui.row().classes('items-center p-4'):
                    ui.icon('emergency', size='lg').classes('text-red-600')
                    with ui.column():
                        ui.label('EMERGENCY MODE - TEXT INPUT').classes('text-lg font-bold text-red-600')
                        ui.label('Type your emergency symptoms below').classes('text-gray-700')

    def setup_input_area(self):
        self.input_card.clear()
        with self.input_card:
            with ui.row().classes('w-full items-end p-4 gap-2'):
                self.text_input = ui.textarea(
                    'Describe your symptoms...' if self.current_mode == 'main'
                    else 'Describe emergency symptoms...') \
                    .classes('flex-grow modern-input') \
                    .props('rows=2 outlined') \
                    .style('font-size:16px;')

                self.text_input.on('keydown.enter.shift', lambda e: None)
                self.text_input.on('keydown.enter', lambda e: self.handle_text_input())

                btn_color = ('turquoise-gradient text-white hover:shadow-lg'
                             if self.current_mode == 'main'
                             else 'bg-red-600 text-white hover:bg-red-700')
                send_btn = ui.button('Send', icon='send', on_click=self.handle_text_input) \
                    .classes(btn_color).style('border-radius:15px; padding:12px 24px;')

    def display_welcome_message(self):
        with self.chat_container:
            if self.current_mode == 'main':
                with ui.card().classes('w-full mb-2 turquoise-gradient text-white modern-card'):
                    with ui.column().classes('p-4'):
                        ui.label('Welcome to Gemm-Aid!').classes('font-bold text-xl')
                        ui.label('I’m here to help with your health concerns.').classes('text-sm opacity-90')
                        ui.html('<ul class="text-sm ml-4 mt-2 opacity-90">'
                                '<li>• Ask about symptoms</li>'
                                '<li>• Get personalized advice</li>'
                                '<li>• Conversations are remembered</li>'
                                '</ul>')
            else:
                with ui.card().classes('w-full mb-2 emergency-simple'):
                    with ui.column().classes('p-4'):
                        ui.label('EMERGENCY MODE ACTIVE').classes('font-bold text-xl text-red-600')
                        ui.label('Type your emergency message below and press Send.').classes('text-lg')

    def handle_text_input(self):
        text = self.text_input.value.strip()
        if not text:
            ui.notify('Please enter a message', type='warning')
            return

        self.text_input.value = ''
        self.add_message(text, is_user=True)
        loading = self.add_message('Processing...', is_user=False, is_loading=True)
        container = self.chat_container

        async def process():
            try:
                if self.current_mode == 'main':
                    prompt = make_input_main(text)
                    resp = await asyncio.to_thread(ask_gemma, prompt)
                    answer, mem = parse_response(resp)
                    await asyncio.to_thread(update_memory, self.memory_path, mem)
                else:
                    answer = await asyncio.to_thread(emergency_chat_with_text, text)
                with container:
                    loading.delete()
                    self.add_message(answer, is_user=False, is_emergency=(self.current_mode=='emergency'))
                if self.current_mode == 'main' and hasattr(self, 'memory_viewer'):
                    with self.memory_viewer:
                        self.load_memory_display()
            except Exception as e:
                with container:
                    loading.delete()
                    self.add_message(f'Error: {e}', is_user=False, is_error=True)
                ui.timer(0, lambda: ui.notify('An error occurred', type='negative'), once=True)

        asyncio.create_task(process())

    def add_message(self, text, is_user=False, is_loading=False, is_error=False, is_emergency=False):
        with self.chat_container:
            with ui.row().classes('w-full mb-3'):
                if is_user:
                    ui.space()
                    cls = 'user-msg-gradient text-white modern-card' if self.current_mode=='main' else 'bg-gray-200 border-2 border-gray-400'
                    msg = ui.card().classes(f'max-w-md {cls}')
                else:
                    if is_emergency:
                        msg = ui.card().classes('max-w-md bg-white border-4 border-red-600')
                    elif is_error:
                        msg = ui.card().classes('max-w-md bg-red-50 text-red-700 modern-card')
                    elif self.current_mode=='main':
                        msg = ui.card().classes('max-w-md bg-white modern-card shadow-md')
                    else:
                        msg = ui.card().classes('max-w-md bg-white border-2 border-gray-400')
                with msg:
                    with ui.column().classes('p-3'):
                        if is_loading:
                            with ui.row().classes('items-center gap-2'):
                                ui.spinner(size='sm')
                                ui.label('Processing...').classes('text-sm')
                        else:
                            if is_emergency and not is_user:
                                with ui.row().classes('items-center mb-2'):
                                    ui.icon('warning', size='sm').classes('text-red-600')
                                    ui.label('EMERGENCY RESPONSE').classes('font-bold text-red-600')
                            ui.markdown(text)
                            ui.label(datetime.now().strftime('%H:%M')).classes('text-xs opacity-70 mt-1')
                if not is_user:
                    ui.space()
        try:
            self.chat_container.scroll_to(percent=1.0)
        except:
            pass
        return msg

    def switch_mode(self, mode):
        if mode == self.current_mode:
            return
        self.current_mode = mode
        ui.run_javascript('window.location.reload()')

    def load_memory_display(self):
        self.memory_viewer.clear()
        try:
            data = json.load(open(self.memory_path, encoding='utf-8'))
            if not data:
                ui.label('No memory entries yet').classes('text-gray-500 p-2')
                return
            for date in sorted(data.keys(), reverse=True)[:5]:
                with ui.card().classes('w-full mb-2 bg-gradient-to-r from-teal-50 to-green-50'):
                    with ui.column().classes('p-3'):
                        ui.label(f'📅 {date}').classes('font-semibold text-sm text-teal-700')
                        ui.label(data[date]).classes('text-sm text-gray-700')
        except Exception:
            ui.label('Error loading memory').classes('text-red-500 p-2')


def main():
    app.storage.general['mode'] = app.storage.general.get('mode', 'main')

    @ui.page('/')
    def index():
        ui.enabled = True
        app_ui = GemmAidUI()
        app_ui.current_mode = app.storage.general['mode']
        app_ui.setup_ui()
        original = app_ui.switch_mode
        def wrapped(m):
            app.storage.general['mode'] = m
            original(m)
        app_ui.switch_mode = wrapped

    os.makedirs('Memory', exist_ok=True)
    os.makedirs('Knowledge', exist_ok=True)

    ui.run(title='Gemm-Aid', favicon='🏥', dark=False, storage_secret='gemm-aid-secret-key')


if __name__ in {"__main__", "__mp_main__"}:
    main()
