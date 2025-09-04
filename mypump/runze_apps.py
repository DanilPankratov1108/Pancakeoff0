import flet as ft
from flet import Icons, Icon
from runze6 import mypump
import assets
import subprocess

mp = mypump()

def main(page: ft.Page):
    page.title = 'Runze Apps'
    page.theme_mode = 'light'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    checkbox1 = ft.Checkbox(label = 'На вход', value = False)
    checkbox2 = ft.Checkbox(label = 'На выход', value = False)

    # theme_switch = ft.Switch(label='Тёмная тема', value=False, on_change=toggle_theme())
    # theme_text = ft.TextField(label='Текущая тема: Светлая')

    def change_theme(page: ft.Page):
        page.theme_mode = "dark" if page.theme_mode == "light" else "light"
        page.update()

    # def on_check_box(e):
    #     if checkbox1 == True or checkbox1.value:
    #         checkbox2.value = False
    #     elif checkbox2 == True or checkbox2.value:
    #         checkbox1.value = False

    Volume1 = ft.TextField(width=180)
    valve1 = ft.TextField(width=180)
    volume1 = ft.TextField(width=180)
    flow_rate1 = ft.TextField(width=180)

    """Домашняя страница"""

    def show_home():
        page.clean()
        page.add(ft.Column([ft.Row([ft.Icon('HOME', size = 24), ft.Text('Главная страница', size =24)]),
                            ft.Row([ft.IconButton('INFO', tooltip='О программе', on_click = lambda e: show_info()),
                            ft.IconButton('SETTINGS', tooltip='Настройки', on_click = lambda e: settings())]),
                            ft.Text('Выберите режим работы с устройством', size = 24),
                            ft.ElevatedButton(content = ft.Row([ft.Icon('FORMAT_LIST_BULLETED'), ft.Text('Создание рецепта')],
                            alignment = ft.MainAxisAlignment.START, spacing = 8,), on_click = lambda e: show_recipe(), width = 180),
                            ft.ElevatedButton(content = ft.Row([ft.Icon('HANDYMAN'), ft.Text('Ручное управление')],
                            alignment = ft.MainAxisAlignment.START, spacing = 8,), on_click = lambda e: show_manual(), width = 180)],
                 alignment = ft.MainAxisAlignment.CENTER,))

    """Страница для написания рецептов"""

    def show_recipe():
        page.clean()
        page.add(ft.Column(
            [ft.Row([ft.IconButton('HOME', tooltip='Главная страница', on_click=lambda e: show_home()),
             ft.IconButton('INFO')]),
             ft.Row([ft.Icon('FORMAT_LIST_BULLETED'), ft.Text('Создание рецепта', size = 24)]),
             ft.Text('Добавляйте команды для создания рецепта'),
             ft.Row([ft.Button('Инициализация', on_click=lambda e: mp.init()), ft.Button('Смена шприца', on_click=lambda e: mp.change_syringe())]),
             ft.Button('Добавить блок рецепта', on_click = lambda e: recipe_block()),
             ft.Row([ft.Button('Подать', on_click=lambda e: on_button_click_1()),
                     ft.Button('Остановка', on_click=lambda e: mp.stop())])
             ],
            alignment = ft.MainAxisAlignment.CENTER,
        ))

    """Блок функций, добавляемый в рецепт"""

    def recipe_block():
        page.add(ft.Column([
                            ft.Row([ft.Text('Объём шприца:'), Volume1, ft.Text('мкл')]),
                            ft.Row([ft.Text('Номер клапана:'), valve1]),
                            ft.Row([checkbox1, checkbox2]),
                            ft.Row([ft.Text('Объём:'), volume1, ft.Text('мкл')]),
                            ft.Row([ft.Text('Расход:'), flow_rate1, ft.Text('мкл/мин')]),
                            ],
                           alignment=ft.MainAxisAlignment.CENTER,
                           ))

    """Ручное управление"""

    def show_manual():
        page.clean()
        page.add(ft.Column([ft.Row([ft.IconButton('HOME', on_click=lambda e: show_home()),
             ft.IconButton('INFO')]),
             ft.Row([ft.Icon('HANDYMAN'), ft.Text('Управление вручную', size = 24)]),
             ft.Text('Здесь можно управлять насосом вручную'),
             ft.Row([ft.Button('Инициализация', on_click=lambda e: mp.init()), ft.Button('Смена шприца', on_click=lambda e: mp.change_syringe())]),
             ft.Row([ft.Text('Объём шприца:'), Volume1, ft.Text('мкл')]),
             ft.Row([ft.Text('Номер клапана:'), valve1]),
             ft.Row([checkbox1, checkbox2]),
             ft.Row([ft.Text('Объём:'), volume1, ft.Text('мкл')]),
             ft.Row([ft.Text('Расход:'), flow_rate1, ft.Text('мкл/мин')]),
                            ft.Row([ft.Button('Подать', on_click = lambda e: on_button_click_1()), ft.Button('Остановка', on_click = lambda e: mp.stop())])],
            alignment = ft.MainAxisAlignment.CENTER,
        ))

    """Чекбокс для выбора направления потока"""

    def on_button_click_1():
        if checkbox1.value and not checkbox2.value:
            if int(Volume1.value) == 125 or mp.REAL_MIN_STEP_1 <= float(volume1.value) <= mp.REAL_MAX_STEP_1 or mp.REAL_MIN_VEL_1 <= float(flow_rate1.value) <= mp.REAL_MAX_VEL_1 or 1 <= int(valve1.value) <= mp.VALVE:
                mp.set_volume(int(Volume1.value))
                mp.refill(float(volume1.value), float(flow_rate1.value), int(valve1.value))
            elif int(Volume1.value) == 500 or mp.REAL_MIN_STEP_2 <= float(volume1.value) <= mp.REAL_MAX_STEP_2 or mp.REAL_MIN_VEL_2 <= float(flow_rate1.value) <= mp.REAL_MAX_VEL_2 or 1 <= int(valve1.value) <= mp.VALVE:
                mp.set_volume(int(Volume1.value))
                mp.refill(float(volume1.value), float(flow_rate1.value), int(valve1.value))
        elif checkbox2.value and not checkbox1.value:
            if int(Volume1.value) == 125 or mp.REAL_MIN_STEP_1 <= float(volume1.value) <= mp.REAL_MAX_STEP_1 or mp.REAL_MIN_VEL_1 <= float(flow_rate1.value) <= mp.REAL_MAX_VEL_1 or 1 <= int(valve1.value) <= mp.VALVE:
                mp.set_volume(int(Volume1.value))
                mp.infuse(float(volume1.value), float(flow_rate1.value), int(valve1.value))
            elif int(Volume1.value) == 500 or mp.REAL_MIN_STEP_2 <= float(volume1.value) <= mp.REAL_MAX_STEP_2 or mp.REAL_MIN_VEL_2 <= float(flow_rate1.value) <= mp.REAL_MAX_VEL_2 or 1 <= int(valve1.value) <= mp.VALVE:
                mp.set_volume(int(Volume1.value))
                mp.infuse(float(volume1.value), float(flow_rate1.value), int(valve1.value))
        elif checkbox2.value or checkbox1.value:
            page.add(ft.Row([ft.Text('Нужно выбрать одно из направлений потока')], alignment = ft.MainAxisAlignment.CENTER,))
        elif not checkbox2.value and not checkbox1.value:
            page.add(ft.Row([ft.Text('Нужно выбрать направление потока')], alignment=ft.MainAxisAlignment.CENTER, ))

    """Страница с информацией о работе с приложением"""

    def show_info():
        page.clean()
        page.add(ft.Column(
            [ft.Row([ft.IconButton('HOME', tooltip='Главная страница', icon_size = 24, on_click = lambda e: show_home()),
                     ft.IconButton('SETTINGS', tooltip='Настройки приложения', icon_size = 24, on_click = lambda e: settings())]),
             ft.Row([ft.Icon('INFO'),
                     ft.Text('Здесь будет описана вся информация, необходимая для работы с устройством', size=18)]),
             ],
            alignment=ft.MainAxisAlignment.CENTER,
        ))

    def settings():
        page.clean()
        page.add(ft.Column(
            [ft.Row([ft.IconButton('HOME', tooltip='Главная страница', icon_size=24, on_click=lambda e: show_home()),
                     ft.IconButton('INFO', tooltip='О приложении', icon_size = 24, on_click = lambda e: show_info())]),
             ft.Row([ft.Icon('SETTINGS'),
                     ft.Text('Настройки приложения', size=18)]), ft.Checkbox(label="Тёмная тема", on_change=lambda e: change_theme(page))
             ],
            alignment=ft.MainAxisAlignment.CENTER,
        ))

    show_home()

ft.app(target=main, assets_dir="assets")
