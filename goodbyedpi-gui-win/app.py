import os
import sys
import subprocess

# Ensure directory is correct
if getattr(sys, 'frozen', False):
    APP_DIR = sys._MEIPASS
    REAL_APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    REAL_APP_DIR = APP_DIR

BIN_DIR = os.path.join(APP_DIR, "bin")

# Global crash logger to capture any startup or runtime errors
def global_excepthook(exctype, value, tb):
    import traceback
    import time
    try:
        with open(os.path.join(REAL_APP_DIR, "crash_log.txt"), "a", encoding="utf-8") as f:
            f.write(f"\n================ CRASH LOG ({time.strftime('%Y-%m-%d %H:%M:%S')}) ================\n")
            f.write("".join(traceback.format_exception(exctype, value, tb)))
    except:
        pass
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = global_excepthook

# Auto-install missing packages
try:
    import customtkinter as ctk
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    try:
        requirements_path = os.path.join(APP_DIR, "requirements.txt")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path], 
                       check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("Kurulum basarili! Uygulama yukleniyor...")
    except Exception as e:
        print(f"Kutubhaneler otomatik kurulurken hata olustu: {e}")
        print("Lutfen komut satirinda 'pip install -r requirements.txt' komutunu calistirin.")
        input("Cikmak icin Enter'a basin...")
        sys.exit(1)

# Now we can safely import them
import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw
import json
import ctypes
import platform
import urllib.request
import zipfile
import io
import shutil
import time
import winreg
import shlex
import socket
import threading

LOCALIZATION = {
    "TR": {
        "window_title": "Intra Windows Güvenli Kalkan",
        "status_active": "KORUMA AKTİF",
        "status_disabled": "KORUMA DEVRE DIŞI",
        "status_desc_active": "İnternet trafiğiniz sansüre karşı maskeleniyor.",
        "status_desc_disabled": "ISS sansür filtreleri devrede. İnternetiniz kısıtlanmış olabilir.",
        "btn_start": "⚡ KALKANI BAŞLAT",
        "btn_stop": "🛡️ KALKANI DURDUR",
        "btn_discord": "🎮 DISCORD'U GÜVENLİ BAŞLAT",
        "discord_hint": "* Discord starting ekranında takılı kalıyorsa veya mesajlar yüklenmiyorsa buradan başlatın.",
        "tab_settings": "Ayarlar",
        "tab_dns": "Sistem DNS",
        "tab_logs": "Log Kayıtları",
        "lbl_doh": "Güvenli DNS (DoH) Sunucusu:",
        "lbl_port": "Yerel Tünel Dinleme Portu (SOCKS5):",
        "cb_startup": "Windows başladığında otomatik çalıştır",
        "cb_tray_close": "Kapatıldığında sistem tepsisine (arka plana) küçült",
        "cb_tray_start": "Başlangıçta sistem tepsisinde (gizli) başlat",
        "cb_dns_enable": "Sistem Ağ Kartı DNS Ayarını De Değiştir (Ekstra Koruma)",
        "cb_dns_reset": "Kalkan kapandığında Sistem DNS ayarını sıfırla (DHCP)",
        "lbl_dns_status": "Aktif Ağ Kartı DNS Adresi:",
        "btn_clear_logs": "🗑️ Günlüğü Temizle",
        "lbl_lang": "Dil / Language:",
        "lang_restart_msg": "Dil değişimi uygulamanın bir sonraki başlatılmasında geçerli olacaktır.",
        "sys_start_log": "[SİSTEM] Otomatik başlatma kaydı eklendi.",
        "sys_stop_log": "[SİSTEM] Otomatik başlatma kaydı silindi.",
        "proxy_active_log": "[PROXY] Windows Sistem Proxy aktif edildi: HTTP/HTTPS {addr}",
        "proxy_disabled_log": "[PROXY] Windows Sistem Proxy devredışı bırakıldı.",
        "kalkan_start_log": "[KALKAN] Kalkan başlatıldı. SOCKS5: 127.0.0.1:{socks_port}, HTTP: 127.0.0.1:{http_port}",
        "kalkan_stop_log": "[KALKAN] Kalkan durduruldu.",
        "dns_update_log": "[DNS] Sistem DNS adresi güncellendi: {dns}",
        "dns_error_log": "[DNS HATA] DNS değiştirilemedi: {err}",
        "btn_refresh_dns": "🔄 DNS Durumunu Yenile",
        "lbl_querying": "Sorgulanıyor...",
        "tray_show": "Göster",
        "tray_toggle": "Aç / Kapat",
        "tray_exit": "Çıkış"
    },
    "EN": {
        "window_title": "Intra Windows Secure Shield",
        "status_active": "PROTECTION ACTIVE",
        "status_disabled": "PROTECTION DISABLED",
        "status_desc_active": "Your internet traffic is masked against censorship.",
        "status_desc_disabled": "ISP censorship filters are active. Your internet may be restricted.",
        "btn_start": "⚡ START SHIELD",
        "btn_stop": "🛡️ STOP SHIELD",
        "btn_discord": "🎮 LAUNCH DISCORD SECURELY",
        "discord_hint": "* If Discord hangs on starting screen or messages fail to load, launch here.",
        "tab_settings": "Settings",
        "tab_dns": "System DNS",
        "tab_logs": "Log Records",
        "lbl_doh": "Secure DNS (DoH) Server:",
        "lbl_port": "Local Tunnel Listening Port (SOCKS5):",
        "cb_startup": "Launch automatically when Windows starts",
        "cb_tray_close": "Minimize to system tray (background) when closed",
        "cb_tray_start": "Start minimized in system tray (hidden) at startup",
        "cb_dns_enable": "Also Change System Network Card DNS Settings (Extra Protection)",
        "cb_dns_reset": "Reset System DNS settings (DHCP) when shield stops",
        "lbl_dns_status": "Active Network Card DNS Address:",
        "btn_clear_logs": "🗑️ Clear Logs",
        "lbl_lang": "Language / Dil:",
        "lang_restart_msg": "Language changes will take effect on the next launch of the application.",
        "sys_start_log": "[SYSTEM] Auto-start entry added.",
        "sys_stop_log": "[SYSTEM] Auto-start entry deleted.",
        "proxy_active_log": "[PROXY] Windows System Proxy enabled: HTTP/HTTPS {addr}",
        "proxy_disabled_log": "[PROXY] Windows System Proxy disabled.",
        "kalkan_start_log": "[SHIELD] Shield started. SOCKS5: 127.0.0.1:{socks_port}, HTTP: 127.0.0.1:{http_port}",
        "kalkan_stop_log": "[SHIELD] Shield stopped.",
        "dns_update_log": "[DNS] System DNS address updated: {dns}",
        "dns_error_log": "[DNS ERROR] DNS could not be changed: {err}",
        "btn_refresh_dns": "🔄 Refresh DNS Status",
        "lbl_querying": "Querying...",
        "tray_show": "Show",
        "tray_toggle": "Toggle Shield",
        "tray_exit": "Exit"
    },
    "RU": {
        "window_title": "Intra Windows Secure Shield",
        "status_active": "ЗАЩИТА АКТИВНА",
        "status_disabled": "ЗАЩИТА ОТКЛЮЧЕНА",
        "status_desc_active": "Ваш интернет-трафик маскируется от цензуры.",
        "status_desc_disabled": "Фильтры цензуры провайдера активны. Интернет может быть ограничен.",
        "btn_start": "⚡ ЗАПУСТИТЬ ЩИТ",
        "btn_stop": "🛡️ ОСТАНОВИТЬ ЩИТ",
        "btn_discord": "🎮 БЕЗОПАСНЫЙ ЗАПУСК DISCORD",
        "discord_hint": "* Если Discord зависает на экране запуска, запустите здесь.",
        "tab_settings": "Настройки",
        "tab_dns": "Системный DNS",
        "tab_logs": "Логи работы",
        "lbl_doh": "Безопасный DNS (DoH) сервер:",
        "lbl_port": "Локальный порт (SOCKS5):",
        "cb_startup": "Запускать автоматически при старте Windows",
        "cb_tray_close": "Сворачивать в трей при закрытии",
        "cb_tray_start": "Запускать свернутым в трей при старте",
        "cb_dns_enable": "Изменить DNS сетевой карты (Доп. защита)",
        "cb_dns_reset": "Сбросить DNS на DHCP при отключении щита",
        "lbl_dns_status": "Активный DNS-адрес сетевой карты:",
        "btn_clear_logs": "🗑️ Очистить логи",
        "lbl_lang": "Язык / Language:",
        "lang_restart_msg": "Изменение языка вступит в силу при следующем запуске приложения.",
        "sys_start_log": "[СИСТЕМА] Запись автозапуска добавлена.",
        "sys_stop_log": "[СИСТЕМА] Запись автозапуска удалена.",
        "proxy_active_log": "[PROXY] Системный прокси включен: HTTP/HTTPS {addr}",
        "proxy_disabled_log": "[PROXY] Системный прокси выключен.",
        "kalkan_start_log": "[ЩИТ] Щит запущен. SOCKS5: 127.0.0.1:{socks_port}, HTTP: 127.0.0.1:{http_port}",
        "kalkan_stop_log": "[ЩИТ] Щит остановлен.",
        "dns_update_log": "[DNS] Системный DNS обновлен: {dns}",
        "dns_error_log": "[DNS ОШИБКА] Не удалось изменить DNS: {err}",
        "btn_refresh_dns": "🔄 Обновить статус DNS",
        "lbl_querying": "Опрос...",
        "tray_show": "Показать",
        "tray_toggle": "Запуск / Стоп",
        "tray_exit": "Выход"
    },
    "DE": {
        "window_title": "Intra Windows Sicherer Schild",
        "status_active": "SCHUTZ AKTIV",
        "status_disabled": "SCHUTZ DEAKTIVIERT",
        "status_desc_active": "Ihr Internetverkehr wird gegen Zensur maskiert.",
        "status_desc_disabled": "Zensurfilter des Anbieters sind aktiv. Internet könnte eingeschränkt sein.",
        "btn_start": "⚡ SCHILD STARTEN",
        "btn_stop": "🛡️ SCHILD STOPPEN",
        "btn_discord": "🎮 DISCORD SICHER STARTEN",
        "discord_hint": "* Wenn Discord beim Starten hängen bleibt, starten Sie hier.",
        "tab_settings": "Einstellungen",
        "tab_dns": "System DNS",
        "tab_logs": "Protokolle",
        "lbl_doh": "Sicherer DNS (DoH) Server:",
        "lbl_port": "Lokaler Tunnel-Listening-Port (SOCKS5):",
        "cb_startup": "Beim Windows-Start automatisch ausführen",
        "cb_tray_close": "Beim Schließen im System-Tray minimieren",
        "cb_tray_start": "Beim Start im System-Tray minimiert starten",
        "cb_dns_enable": "Auch System-Netzwerkkarten-DNS ändern (Extra Schutz)",
        "cb_dns_reset": "System-DNS auf DHCP zurücksetzen, wenn Schild stoppt",
        "lbl_dns_status": "Aktive Netzwerkkarten-DNS-Adresse:",
        "btn_clear_logs": "🗑️ Protokoll leeren",
        "lbl_lang": "Sprache / Language:",
        "lang_restart_msg": "Die Spracheinstellungen werden beim nächsten Start der Anwendung wirksam.",
        "sys_start_log": "[SYSTEM] Autostart-Eintrag hinzugefügt.",
        "sys_stop_log": "[SYSTEM] Autostart-Eintrag gelöscht.",
        "proxy_active_log": "[PROXY] Windows-Systemproxy aktiviert: HTTP/HTTPS {addr}",
        "proxy_disabled_log": "[PROXY] Windows-Systemproxy deaktiviert.",
        "kalkan_start_log": "[SCHILD] Schild gestartet. SOCKS5: 127.0.0.1:{socks_port}, HTTP: 127.0.0.1:{http_port}",
        "kalkan_stop_log": "[SCHILD] Schild gestoppt.",
        "dns_update_log": "[DNS] System-DNS-Adresse aktualisiert: {dns}",
        "dns_error_log": "[DNS FEHLER] DNS konnte nicht geändert werden: {err}",
        "btn_refresh_dns": "🔄 DNS-Status aktualisieren",
        "lbl_querying": "Abfragen...",
        "tray_show": "Anzeigen",
        "tray_toggle": "Ein / Aus",
        "tray_exit": "Beenden"
    },
    "AZ": {
        "window_title": "Intra Windows Təhlükəsiz Qalxan",
        "status_active": "QORUMA AKTİVDİR",
        "status_disabled": "QORUMA DEAKTİVDİR",
        "status_desc_active": "İnternet trafikiniz senzura qarşı maskalanır.",
        "status_desc_disabled": "İSS senzura filtrləri aktivdir. İnternetiniz məhdudlaşdırıla bilər.",
        "btn_start": "⚡ QALXANI BAŞLAT",
        "btn_stop": "🛡️ QALXANI DAYANDIR",
        "btn_discord": "🎮 DİSCORD-U TƏHLÜKƏSİZ BAŞLAT",
        "discord_hint": "* Əgər Discord başlanğıc ekranda ilişibsə, buradan başladın.",
        "tab_settings": "Ayarlar",
        "tab_dns": "Sistem DNS",
        "tab_logs": "Log Qeydləri",
        "lbl_doh": "Təhlükəsiz DNS (DoH) Serveri:",
        "lbl_port": "Yerli Tunel Dinləmə Portu (SOCKS5):",
        "cb_startup": "Windows başladıqda avtomatik işə sal",
        "cb_tray_close": "Bağlandıqda arxa plana (sistem tepsisinə) kiçilt",
        "cb_tray_start": "Başlanğıcda sistem tepsisində (gizli) başlat",
        "cb_dns_enable": "Sistem Şəbəkə Kartı DNS Ayarlarını Da Dəyişdir (Əlavə Qoruma)",
        "cb_dns_reset": "Qalxan dayandıqda Sistem DNS ayarlarını sıfırla (DHCP)",
        "lbl_dns_status": "Aktiv Şəbəkə Kartı DNS Ünvanı:",
        "btn_clear_logs": "🗑️ Gündəliyi Təmizlə",
        "lbl_lang": "Dil / Language:",
        "lang_restart_msg": "Dil dəyişikliyi tətbiqin növbəti işə salınmasında qüvvəyə minəcək.",
        "sys_start_log": "[SİSTEM] Avtomatik işə salma qeydi əlavə edildi.",
        "sys_stop_log": "[SİSTEM] Avtomatik işə salma qeydi silindi.",
        "proxy_active_log": "[PROXY] Windows Sistem Proksisi aktiv edildi: HTTP/HTTPS {addr}",
        "proxy_disabled_log": "[PROXY] Windows Sistem Proksisi deaktiv edildi.",
        "kalkan_start_log": "[QALXAN] Qalxan başladıldı. SOCKS5: 127.0.0.1:{socks_port}, HTTP: 127.0.0.1:{http_port}",
        "kalkan_stop_log": "[QALXAN] Qalxan dayandırıldı.",
        "dns_update_log": "[DNS] Sistem DNS ünvanı yeniləndi: {dns}",
        "dns_error_log": "[DNS XƏTA] DNS dəyişdirilə bilmədi: {err}",
        "btn_refresh_dns": "🔄 DNS Statusunu Yenilə",
        "lbl_querying": "Sorğulanır...",
        "tray_show": "Göstər",
        "tray_toggle": "Aç / Bağla",
        "tray_exit": "Çıxış"
    }
}

_instance_socket = None

def check_single_instance():
    global _instance_socket
    try:
        _instance_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _instance_socket.bind(('127.0.0.1', 10810))
    except socket.error:
        try:
            for title in ["Intra Windows Güvenli Kalkan", 
                         "Intra Windows Secure Shield", 
                         "Intra Windows Sicherer Schild", 
                         "Intra Windows Təhlükəsiz Qalxan"]:
                hwnd = ctypes.windll.user32.FindWindowW(None, title)
                if hwnd:
                    ctypes.windll.user32.ShowWindow(hwnd, 9)
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                    break
        except:
            pass
        sys.exit(0)

def sanitize_system_proxy_on_startup():
    """Automatically cleans up any leftover proxy settings from crash or unexpected power off."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0,
            winreg.KEY_READ
        )
        try:
            proxy_enable = winreg.QueryValueEx(key, "ProxyEnable")[0]
            proxy_server = winreg.QueryValueEx(key, "ProxyServer")[0]
        except FileNotFoundError:
            proxy_enable = 0
            proxy_server = ""
        winreg.CloseKey(key)

        # If proxy was left pointing to localhost 10809/10808 from a past shutdown or power outage
        if proxy_enable == 1 and ("10809" in proxy_server or "10808" in proxy_server):
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                0,
                winreg.KEY_WRITE
            )
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            try:
                winreg.DeleteValue(key, "ProxyServer")
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
            ctypes.windll.wininet.InternetSetOptionW(0, 39, 0, 0)
            ctypes.windll.wininet.InternetSetOptionW(0, 37, 0, 0)
    except Exception as e:
        print(f"Startup sanitizer error: {e}")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False



def get_current_dns():
    try:
        ps_cmd = 'Get-DnsClientServerAddress -AddressFamily IPv4 | Select-Object -ExpandProperty ServerAddresses'
        res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if res.returncode == 0:
            dns_list = res.stdout.strip().splitlines()
            cleaned_dns = [d.strip() for d in dns_list if d.strip()]
            if cleaned_dns:
                return ", ".join(cleaned_dns)
    except Exception as e:
        print(f"Error getting DNS: {e}")
    return "DHCP / Otomatik"

def ensure_icon_files():
    icon_png = os.path.join(APP_DIR, "icon.png")
    icon_ico = os.path.join(APP_DIR, "icon.ico")
    if not os.path.exists(icon_png) or not os.path.exists(icon_ico):
        try:
            im = Image.new("RGBA", (256, 256), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(im)
            draw.rounded_rectangle([10, 10, 246, 246], radius=45, fill=(15, 23, 42, 255), outline=(99, 102, 241, 255), width=10)
            
            shield_pts = [
                (128, 50),
                (196, 75),
                (196, 140),
                (128, 215),
                (60, 140),
                (60, 75)
            ]
            draw.polygon(shield_pts, fill=(99, 102, 241, 40), outline=(99, 102, 241, 255), width=8)
            draw.line([(95, 125), (122, 152), (165, 95)], fill=(16, 185, 129, 255), width=12, joint="round")
            
            im.save(icon_png, format="PNG")
            im.save(icon_ico, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        except Exception as e:
            print(f"Failed to generate icons: {e}")

class GoodbyeDpiGUI:
    def __init__(self, root):
        self.root = root
        
        self.app_dir = APP_DIR
        self.bin_dir = BIN_DIR
        self.process = None
        self.tray_icon = None
        
        self.cleanup_orphaned_processes()
        self.load_config()
        self.lang = self.config.get("language", "TR")
        self.lang_dict = LOCALIZATION.get(self.lang, LOCALIZATION["TR"])
        
        self.root.title(self.lang_dict["window_title"])
        self.root.geometry("540x700")
        self.root.resizable(True, True)
        self.root.minsize(540, 600)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.root.configure(fg_color="#0F172A")
        
        # Original Proxy settings backup
        self.original_proxy_enable = 0
        self.original_proxy_server = ""
        self.original_proxy_override = ""
        self.save_original_proxy_settings()
        
        # Watchdog & Reconnection States
        self.should_be_running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        ensure_icon_files()
        icon_ico_path = os.path.join(self.app_dir, "icon.ico")
        if os.path.exists(icon_ico_path):
            self.root.after(200, lambda: self.root.iconbitmap(icon_ico_path))
            
        self.setup_ui()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.check_binaries()
        
        if "--minimized" in sys.argv or self.config.get("tray_start", False):
            self.setup_tray_icon()
            self.root.after(100, self.root.withdraw)
        else:
            self.setup_tray_icon()

    def save_original_proxy_settings(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                0,
                winreg.KEY_READ
            )
            try:
                self.original_proxy_enable = winreg.QueryValueEx(key, "ProxyEnable")[0]
            except FileNotFoundError:
                self.original_proxy_enable = 0
                
            try:
                self.original_proxy_server = winreg.QueryValueEx(key, "ProxyServer")[0]
            except FileNotFoundError:
                self.original_proxy_server = ""
                
            try:
                self.original_proxy_override = winreg.QueryValueEx(key, "ProxyOverride")[0]
            except FileNotFoundError:
                self.original_proxy_override = ""
                
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error reading proxy: {e}")

    def setup_ui(self):
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.header_frame = ctk.CTkFrame(self.root, fg_color="#1E293B", height=85, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_propagate(False)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="🛡️ INTRA WINDOWS SECURE SHIELD", 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#F8FAFC"
        )
        self.title_label.pack(pady=(16, 2))
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame, 
            text="Jigsaw Intra Engine Windows SOCKS5 Proxy & DNS-over-HTTPS", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94A3B8"
        )
        self.subtitle_label.pack(pady=(0, 10))
        
        self.status_frame = ctk.CTkFrame(self.root, fg_color="#1E293B", corner_radius=12)
        self.status_frame.grid(row=1, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.status_frame.grid_columnconfigure(1, weight=1)
        
        self.canvas = ctk.CTkCanvas(self.status_frame, width=50, height=50, bg="#1E293B", highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=20, pady=15, rowspan=2)
        self.status_dot = self.canvas.create_oval(8, 8, 42, 42, fill="#EF4444", outline="#F87171", width=3)
        
        self.status_title = ctk.CTkLabel(
            self.status_frame, 
            text=self.lang_dict["status_disabled"], 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#F87171"
        )
        self.status_title.grid(row=0, column=1, sticky="w", pady=(12, 1))
        
        self.status_desc = ctk.CTkLabel(
            self.status_frame, 
            text=self.lang_dict["status_desc_disabled"], 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94A3B8"
        )
        self.status_desc.grid(row=1, column=1, sticky="w", pady=(0, 12))
        
        self.toggle_btn = ctk.CTkButton(
            self.root, 
            text=self.lang_dict["btn_start"], 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            height=50,
            corner_radius=10,
            fg_color="#6366F1",
            hover_color="#4F46E5",
            command=self.toggle_bypass
        )
        self.toggle_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # Discord Safe Launcher Button
        self.discord_btn = ctk.CTkButton(
            self.root,
            text=self.lang_dict["btn_discord"],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=40,
            corner_radius=10,
            fg_color="#5865F2",
            hover_color="#4752C4",
            command=self.launch_discord_with_proxy
        )
        self.discord_btn.grid(row=3, column=0, padx=20, pady=(5, 0), sticky="ew")
        
        # Discord Hint Label below the button
        self.discord_hint_lbl = ctk.CTkLabel(
            self.root,
            text=self.lang_dict["discord_hint"],
            font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"),
            text_color="#94A3B8"
        )
        self.discord_hint_lbl.grid(row=4, column=0, padx=24, pady=(2, 10), sticky="w")
        
        self.tabview = ctk.CTkTabview(self.root, fg_color="#1E293B", corner_radius=12)
        self.tabview.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="nsew")
        
        self.tab_settings = self.tabview.add(self.lang_dict["tab_settings"])
        self.tab_dns = self.tabview.add(self.lang_dict["tab_dns"])
        self.tab_logs = self.tabview.add(self.lang_dict["tab_logs"])
        
        self.setup_settings_tab()
        self.setup_dns_tab()
        self.setup_logs_tab()

    def launch_discord_with_proxy(self):
        local_appdata = os.environ.get("LOCALAPPDATA")
        if not local_appdata:
            self.log_message("[HATA] LOCALAPPDATA klasörü bulunamadı." if self.lang == "TR" else "[ERROR] LOCALAPPDATA directory not found.")
            return
            
        discord_updater = os.path.join(local_appdata, "Discord", "Update.exe")
        if os.path.exists(discord_updater):
            socks_port = self.config.get("socks_port", "10808")
            cmd = f'"{discord_updater}" --processStart Discord.exe --process-start-args="--proxy-server=socks5://127.0.0.1:{socks_port}"'
            try:
                subprocess.Popen(cmd, shell=True)
                self.log_message("[SİSTEM] Discord tünel ve proxy parametreleriyle başlatılıyor..." if self.lang == "TR" else "[SYSTEM] Launching Discord with tunnel proxy parameters...")
            except Exception as e:
                self.log_message(f"[HATA] Discord başlatılamadı: {e}" if self.lang == "TR" else f"[ERROR] Could not start Discord: {e}")
        else:
            self.log_message("[HATA] Discord kurulumu bulunamadı. Lütfen varsayılan dizinde olduğundan emin olun." if self.lang == "TR" else "[ERROR] Discord installation not found. Please ensure it is in the default directory.")

    def setup_settings_tab(self):
        self.tab_settings.grid_columnconfigure(0, weight=1)
        self.tab_settings.grid_rowconfigure(0, weight=1)
        
        self.settings_scroll = ctk.CTkScrollableFrame(self.tab_settings, fg_color="transparent")
        self.settings_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.dns_provider_lbl = ctk.CTkLabel(
            self.settings_scroll, 
            text=self.lang_dict["lbl_doh"], 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.dns_provider_lbl.pack(anchor="w", padx=10, pady=(15, 5))
        
        self.dns_doh_providers = {
            "Cloudflare DNS (1.1.1.1)": {
                "url": "https://cloudflare-dns.com/dns-query",
                "bootstrap": "1.1.1.1,1.0.0.1"
            },
            "Google DNS (8.8.8.8)": {
                "url": "https://dns.google/dns-query",
                "bootstrap": "8.8.8.8,8.8.4.4"
            },
            "Quad9 DNS (9.9.9.9)": {
                "url": "https://dns.quad9.net/dns-query",
                "bootstrap": "9.9.9.9,149.112.112.112"
            },
            "AdGuard DNS": {
                "url": "https://dns.adguard-dns.com/dns-query",
                "bootstrap": "94.140.14.14,94.140.15.15"
            }
        }
        
        self.doh_dropdown = ctk.CTkOptionMenu(
            self.settings_scroll,
            values=list(self.dns_doh_providers.keys()),
            command=self.on_doh_change,
            width=400,
            fg_color="#334155",
            button_color="#475569",
            button_hover_color="#64748B"
        )
        self.doh_dropdown.pack(anchor="w", padx=10, pady=(0, 15))
        
        self.port_lbl = ctk.CTkLabel(
            self.settings_scroll, 
            text=self.lang_dict["lbl_port"], 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.port_lbl.pack(anchor="w", padx=10, pady=(0, 2))
        
        self.port_entry = ctk.CTkEntry(
            self.settings_scroll,
            placeholder_text="10808",
            width=150,
            fg_color="#0F172A",
            border_color="#475569"
        )
        self.port_entry.pack(anchor="w", padx=10, pady=(0, 10))
        
        self.sep = ctk.CTkFrame(self.settings_scroll, height=2, fg_color="#334155")
        self.sep.pack(fill="x", padx=10, pady=12)
        
        self.startup_var = ctk.BooleanVar()
        self.startup_cb = ctk.CTkCheckBox(
            self.settings_scroll,
            text=self.lang_dict["cb_startup"],
            variable=self.startup_var,
            command=self.toggle_startup,
            fg_color="#6366F1"
        )
        self.startup_cb.pack(anchor="w", padx=10, pady=6)
        
        self.tray_close_var = ctk.BooleanVar()
        self.tray_close_cb = ctk.CTkCheckBox(
            self.settings_scroll,
            text=self.lang_dict["cb_tray_close"],
            variable=self.tray_close_var,
            command=self.update_config_vars,
            fg_color="#6366F1"
        )
        self.tray_close_cb.pack(anchor="w", padx=10, pady=6)
        
        self.tray_start_var = ctk.BooleanVar()
        self.tray_start_cb = ctk.CTkCheckBox(
            self.settings_scroll,
            text=self.lang_dict["cb_tray_start"],
            variable=self.tray_start_var,
            command=self.update_config_vars,
            fg_color="#6366F1"
        )
        self.tray_start_cb.pack(anchor="w", padx=10, pady=6)
 
        # Language selection
        self.lang_sep = ctk.CTkFrame(self.settings_scroll, height=2, fg_color="#334155")
        self.lang_sep.pack(fill="x", padx=10, pady=12)
 
        self.lang_lbl = ctk.CTkLabel(
            self.settings_scroll, 
            text=self.lang_dict["lbl_lang"], 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.lang_lbl.pack(anchor="w", padx=10, pady=(0, 2))
        
        self.lang_dropdown = ctk.CTkOptionMenu(
            self.settings_scroll,
            values=["Türkçe (TR)", "English (EN)", "Русский (RU)", "Deutsch (DE)", "Azərbaycan (AZ)"],
            command=self.on_language_change,
            width=200,
            fg_color="#334155",
            button_color="#475569",
            button_hover_color="#64748B"
        )
        self.lang_dropdown.pack(anchor="w", padx=10, pady=(0, 10))
        lang_map = {"TR": "Türkçe (TR)", "EN": "English (EN)", "RU": "Русский (RU)", "DE": "Deutsch (DE)", "AZ": "Azərbaycan (AZ)"}
        self.lang_dropdown.set(lang_map.get(self.lang, "Türkçe (TR)"))

    def on_language_change(self, val):
        code = val.split("(")[-1].replace(")", "").strip()
        self.config["language"] = code
        self.save_config()
        
        from tkinter import messagebox
        messagebox.showinfo("Language / Dil", LOCALIZATION[code]["lang_restart_msg"])

    def setup_dns_tab(self):
        self.dns_enable_var = ctk.BooleanVar()
        self.dns_enable_cb = ctk.CTkCheckBox(
            self.tab_dns,
            text=self.lang_dict["cb_dns_enable"],
            variable=self.dns_enable_var,
            command=self.toggle_dns_changer_ui,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#6366F1"
        )
        self.dns_enable_cb.pack(anchor="w", padx=20, pady=(20, 10))
        
        self.dns_reset_var = ctk.BooleanVar()
        self.dns_reset_cb = ctk.CTkCheckBox(
            self.tab_dns,
            text=self.lang_dict["cb_dns_reset"],
            variable=self.dns_reset_var,
            command=self.update_config_vars,
            fg_color="#6366F1"
        )
        self.dns_reset_cb.pack(anchor="w", padx=20, pady=6)
        
        self.dns_sep = ctk.CTkFrame(self.tab_dns, height=2, fg_color="#334155")
        self.dns_sep.pack(fill="x", padx=20, pady=15)
        
        self.dns_info_lbl = ctk.CTkLabel(
            self.tab_dns, 
            text=self.lang_dict["lbl_dns_status"], 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#94A3B8"
        )
        self.dns_info_lbl.pack(anchor="w", padx=20, pady=(0, 2))
        
        self.dns_val_label = ctk.CTkLabel(
            self.tab_dns, 
            text=self.lang_dict["lbl_querying"], 
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#10B981"
        )
        self.dns_val_label.pack(anchor="w", padx=20, pady=(0, 12))
        
        self.dns_refresh_btn = ctk.CTkButton(
            self.tab_dns,
            text=self.lang_dict["btn_refresh_dns"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self.refresh_dns_display,
            width=180,
            fg_color="#334155",
            hover_color="#475569"
        )
        self.dns_refresh_btn.pack(anchor="w", padx=20)

    def setup_logs_tab(self):
        self.log_text = ctk.CTkTextbox(
            self.tab_logs,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color="#0F172A",
            text_color="#34D399",
            border_color="#334155",
            border_width=1
        )
        self.log_text.pack(padx=15, pady=(15, 10), fill="both", expand=True)
        
        self.clear_logs_btn = ctk.CTkButton(
            self.tab_logs,
            text=self.lang_dict["btn_clear_logs"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self.clear_logs,
            fg_color="#334155",
            hover_color="#475569",
            width=140
        )
        self.clear_logs_btn.pack(padx=15, pady=(0, 15), side="right")

    def load_config(self):
        self.config_path = os.path.join(REAL_APP_DIR, "config.json")
        default_config = {
            "doh_provider": "Cloudflare DNS (1.1.1.1)",
            "socks_port": "10808",
            "startup": False,
            "tray_close": True,
            "tray_start": False,
            "system_dns_enabled": False,
            "dns_reset_on_exit": True
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                    for k, v in default_config.items():
                        if k not in self.config:
                            self.config[k] = v
            except:
                self.config = default_config
        else:
            self.config = default_config
        
        self.root.after(10, self.apply_config_to_ui)

    def apply_config_to_ui(self):
        self.doh_dropdown.set(self.config["doh_provider"])
        self.port_entry.delete(0, "end")
        self.port_entry.insert(0, self.config["socks_port"])
        self.startup_var.set(self.config["startup"])
        self.tray_close_var.set(self.config["tray_close"])
        self.tray_start_var.set(self.config["tray_start"])
        self.dns_enable_var.set(self.config["system_dns_enabled"])
        self.dns_reset_var.set(self.config["dns_reset_on_exit"])
        self.toggle_dns_changer_ui()

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def update_config_vars(self):
        self.config["tray_close"] = self.tray_close_var.get()
        self.config["tray_start"] = self.tray_start_var.get()
        self.config["system_dns_enabled"] = self.dns_enable_var.get()
        self.config["dns_reset_on_exit"] = self.dns_reset_var.get()
        self.config["socks_port"] = self.port_entry.get().strip() or "10808"
        self.config["doh_provider"] = self.doh_dropdown.get()
        self.save_config()

    def on_doh_change(self, val):
        self.update_config_vars()

    def toggle_dns_changer_ui(self):
        self.update_config_vars()
        state = "normal" if self.dns_enable_var.get() else "disabled"
        self.dns_reset_cb.configure(state=state)
        
        if self.process:
            if self.dns_enable_var.get():
                dns_name = self.doh_dropdown.get()
                dns_ips = self.dns_doh_providers[dns_name]["bootstrap"].split(",")
                self.set_dns_servers(dns_ips)
            else:
                self.set_dns_servers(None)

    def check_binaries(self):
        exe_path = os.path.join(self.bin_dir, "intra-windpi.exe")
        if not os.path.exists(exe_path):
            if shutil.which("go"):
                self.show_compilation_overlay()
            else:
                self.show_missing_binary_error()
        else:
            self.refresh_dns_display()
            self.root.after(400, self.start_bypass)

    def show_compilation_overlay(self):
        self.download_frame = ctk.CTkFrame(self.root, fg_color="#0F172A")
        self.download_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.dl_label = ctk.CTkLabel(
            self.download_frame,
            text="⚙️ Intra Go Modülü Derleniyor...\n\nLütfen bekleyin, bu işlem sisteminizdeki Go derleyicisi\nile birkaç saniye sürebilir...",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            justify="center",
            text_color="#F8FAFC"
        )
        self.dl_label.pack(expand=True, pady=(100, 10))
        
        self.progress_bar = ctk.CTkProgressBar(self.download_frame, width=300, fg_color="#1E293B", progress_color="#6366F1")
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)
        self.progress_bar.start()
        
        threading.Thread(target=self.compile_backend_thread, daemon=True).start()

    def compile_backend_thread(self):
        try:
            os.makedirs(self.bin_dir, exist_ok=True)
            # Compile Go backend from parent directory
            root_dir = os.path.dirname(self.app_dir)
            cmd = ["go", "build", "-ldflags=-s -w -H=windowsgui", "-o", os.path.join(self.bin_dir, "intra-windpi.exe"), "./win_backend"]
            
            res = subprocess.run(cmd, cwd=root_dir, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if res.returncode == 0:
                self.root.after(0, self.on_compile_success)
            else:
                self.root.after(0, lambda: self.on_compile_error(res.stderr))
        except Exception as e:
            self.root.after(0, lambda: self.on_compile_error(str(e)))

    def on_compile_success(self):
        self.download_frame.destroy()
        self.refresh_dns_display()
        self.log_message("[SİSTEM] Jigsaw Intra Windows Backend başarıyla derlendi.")
        self.root.after(400, self.start_bypass)

    def on_compile_error(self, err_msg):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.dl_label.configure(
            text=f"❌ Derleme Hatası!\n\nIntra Go modülü derlenemedi.\n\nHata: {err_msg}",
            text_color="#EF4444"
        )

    def show_missing_binary_error(self):
        self.download_frame = ctk.CTkFrame(self.root, fg_color="#0F172A")
        self.download_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.dl_label = ctk.CTkLabel(
            self.download_frame,
            text="❌ HATA: intra-windpi.exe bulunamadı!\n\nLütfen Go derleyicisini kurun ve projeyi yeniden derleyin\nveya binary dosyasını el ile 'bin/' klasörüne kopyalayın.",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            justify="center",
            text_color="#EF4444"
        )
        self.dl_label.pack(expand=True)

    def log_message(self, message):
        self.root.after(0, lambda: self._write_log(message))

    def _write_log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{time.strftime('%H:%M:%S')}] {message.strip()}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def clear_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def cleanup_orphaned_processes(self):
        try:
            subprocess.run(["taskkill", "/F", "/IM", "intra-windpi.exe"], 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            pass

    def refresh_dns_display(self):
        self.dns_val_label.configure(text="Sorgulanıyor...", text_color="#F59E0B")
        def query():
            dns_val = get_current_dns()
            self.root.after(0, lambda: self.dns_val_label.configure(text=dns_val, text_color="#10B981"))
        threading.Thread(target=query, daemon=True).start()

    def set_dns_servers(self, dns_servers):
        def task():
            try:
                # Get active adapter names via netsh (avoids suspicious PowerShell spawning)
                res = subprocess.run(
                    ['netsh', 'interface', 'show', 'interface'],
                    capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
                )
                adapters = []
                for line in res.stdout.splitlines():
                    parts = line.split()
                    if len(parts) >= 4 and parts[1].lower() == 'connected':
                        adapters.append(' '.join(parts[3:]))
                
                if not adapters:
                    # Fallback: get all enabled adapters
                    res2 = subprocess.run(
                        ['netsh', 'interface', 'ipv4', 'show', 'interfaces'],
                        capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    for line in res2.stdout.splitlines():
                        parts = line.split()
                        if len(parts) >= 5 and parts[3].lower() == 'connected':
                            adapters.append(' '.join(parts[4:]))

                if not adapters:
                    self.log_message("[DNS HATA] Aktif ağ adaptörü bulunamadı.")
                    return

                for adapter in adapters:
                    if dns_servers:
                        # Set primary DNS
                        subprocess.run(
                            ['netsh', 'interface', 'ip', 'set', 'dns',
                             f'name={adapter}', 'source=static',
                             f'address={dns_servers[0]}', 'validate=no'],
                            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        # Set secondary DNS servers
                        for i, ip in enumerate(dns_servers[1:], start=2):
                            subprocess.run(
                                ['netsh', 'interface', 'ip', 'add', 'dns',
                                 f'name={adapter}', f'address={ip}',
                                 f'index={i}', 'validate=no'],
                                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
                            )
                    else:
                        # Reset to DHCP
                        subprocess.run(
                            ['netsh', 'interface', 'ip', 'set', 'dns',
                             f'name={adapter}', 'source=dhcp'],
                            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
                        )

                self.log_message(f"[DNS] Sistem DNS güncellendi: {dns_servers if dns_servers else 'DHCP (Varsayılan)'}")
                self.refresh_dns_display()
            except Exception as e:
                self.log_message(f"[DNS HATA] DNS işleminde hata: {e}")
                
        threading.Thread(target=task, daemon=True).start()

    def set_default_connection_settings(self, enabled, proxy_addr=""):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections",
                0,
                winreg.KEY_ALL_ACCESS
            )
            try:
                value, reg_type = winreg.QueryValueEx(key, "DefaultConnectionSettings")
                blob = bytearray(value)
            except FileNotFoundError:
                blob = bytearray([70, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                reg_type = winreg.REG_BINARY

            if enabled:
                server_str = proxy_addr
                server_bytes = server_str.encode('utf-8')
                server_len = len(server_bytes)
                
                bypass_str = "localhost;127.0.0.1;<local>"
                bypass_bytes = bypass_str.encode('utf-8')
                bypass_len = len(bypass_bytes)
                
                # Reconstruct blob
                new_blob = bytearray(blob[:8])
                new_blob.append(3) # Proxy Enabled flag
                new_blob.extend([0, 0, 0])
                new_blob.extend(server_len.to_bytes(4, byteorder='little'))
                new_blob.extend(server_bytes)
                new_blob.extend(bypass_len.to_bytes(4, byteorder='little'))
                new_blob.extend(bypass_bytes)
                new_blob.extend([0] * 36) # padding
                blob = new_blob
            else:
                blob[8] = 1 # Proxy Disabled flag
                if len(blob) >= 16:
                    blob[12:16] = [0, 0, 0, 0] # zero server length
            
            winreg.SetValueEx(key, "DefaultConnectionSettings", 0, reg_type, bytes(blob))
            winreg.SetValueEx(key, "SavedLegacySettings", 0, reg_type, bytes(blob))
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Failed to update DefaultConnectionSettings: {e}")

    def set_system_proxy(self, enabled, proxy_addr=""):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                0,
                winreg.KEY_WRITE
            )
            if enabled:
                # Calculate HTTP proxy address (SOCKS port + 1)
                port_part = proxy_addr.split(":")[-1]
                http_port = int(port_part) + 1
                http_proxy = f"127.0.0.1:{http_port}"
                
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, http_proxy)
                winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, "localhost;127.0.0.1;<local>")
                self.log_message(f"[PROXY] Windows Sistem Proxy aktif edildi: HTTP/HTTPS {http_proxy}")
                
                # Update binary connection settings blobs with standard HTTP proxy
                self.set_default_connection_settings(True, http_proxy)
            else:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, self.original_proxy_enable)
                if self.original_proxy_server:
                    winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, self.original_proxy_server)
                if self.original_proxy_override:
                    winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, self.original_proxy_override)
                self.log_message("[PROXY] Windows Sistem Proxy devredışı bırakıldı.")
                
                # Reset binary connection settings blobs
                self.set_default_connection_settings(False)
                
            winreg.CloseKey(key)
            
            # Refresh network configuration immediately with ctypes signature
            InternetSetOption = ctypes.windll.wininet.InternetSetOptionW
            from ctypes import wintypes
            InternetSetOption.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD]
            InternetSetOption.restype = wintypes.BOOL
            InternetSetOption(None, 39, None, 0)
            InternetSetOption(None, 37, None, 0)
        except Exception as e:
            self.log_message(f"[PROXY HATA] Sistem Proxy uygulanamadı: {e}")

    def toggle_bypass(self):
        if self.process:
            self.stop_bypass()
        else:
            self.start_bypass()

    def start_bypass(self):
        exe_path = os.path.join(self.bin_dir, "intra-windpi.exe")
        if not os.path.exists(exe_path):
            self.log_message("[HATA] Backend bulunamadı.")
            return
            
        self.cleanup_orphaned_processes()
        self.update_config_vars()
        
        socks_port = self.config["socks_port"]
        http_port = int(socks_port) + 1
        dns_name = self.config["doh_provider"]
        doh_url = self.dns_doh_providers[dns_name]["url"]
        bootstrap_ips = self.dns_doh_providers[dns_name]["bootstrap"]
        
        cmd = [
            exe_path,
            "-addr", f"127.0.0.1:{socks_port}",
            "-http", f"127.0.0.1:{http_port}",
            "-doh", doh_url,
            "-bootstrap", bootstrap_ips,
            "-dns", ""
        ]
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=self.bin_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                startupinfo=startupinfo,
                text=True,
                bufsize=1
            )
            
            self.should_be_running = True
            self.reconnect_attempts = 0
            
            threading.Thread(target=self.read_process_output, args=(self.process,), daemon=True).start()
            self.log_message(f"[KALKAN] Kalkan başlatıldı. SOCKS5: 127.0.0.1:{socks_port}, HTTP: 127.0.0.1:{http_port}")
            
            self.set_system_proxy(True, f"127.0.0.1:{socks_port}")
            
            if self.dns_enable_var.get():
                dns_ips = bootstrap_ips.split(",")
                self.set_dns_servers(dns_ips)
                
            self.update_status_ui(True)
            
        except Exception as e:
            self.log_message(f"[HATA] Kalkan başlatılamadı: {e}")

    def read_process_output(self, proc):
        for line in iter(proc.stdout.readline, ''):
            line_str = line.strip()
            if line_str:
                self.log_message(f"[BACKEND] {line_str}")
        proc.stdout.close()
        self.root.after(0, self.on_process_exit)

    def on_process_exit(self):
        self.process = None
        
        if self.should_be_running:
            self.log_message("[UYARI] Backend kapandı. Yeniden bağlanılıyor...")
            self.update_status_ui(False)
            
            self.reconnect_attempts += 1
            if self.reconnect_attempts <= self.max_reconnect_attempts:
                self.root.after(0, lambda: self.status_title.configure(text="YENİDEN BAĞLANIYOR...", text_color="#F59E0B"))
                self.root.after(2000, self.start_bypass)
            else:
                self.log_message("[HATA] Bağlantı denemeleri başarısız oldu.")
                self.should_be_running = False
                self.reconnect_attempts = 0
                self.set_system_proxy(False)
        else:
            self.update_status_ui(False)

    def stop_bypass(self):
        self.should_be_running = False
        self.reconnect_attempts = 0
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                try:
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.process.pid)], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                except:
                    pass
            try:
                self.process.stdout.close()
            except:
                pass
            self.process = None
            
        self.set_system_proxy(False)
        
        if self.dns_enable_var.get() and self.dns_reset_var.get():
            self.set_dns_servers(None)
            
        self.log_message("[KALKAN] Kalkan durduruldu.")
        self.update_status_ui(False)

    def update_status_ui(self, active):
        if active:
            self.canvas.itemconfig(self.status_dot, fill="#0D9488", outline="#2DD4BF")
            self.status_title.configure(text=self.lang_dict["status_active"], text_color="#2DD4BF")
            self.status_desc.configure(text=self.lang_dict["status_desc_active"])
            self.toggle_btn.configure(text=self.lang_dict["btn_stop"], fg_color="#EF4444", hover_color="#DC2626")
        else:
            self.canvas.itemconfig(self.status_dot, fill="#EF4444", outline="#F87171")
            self.status_title.configure(text=self.lang_dict["status_disabled"], text_color="#F87171")
            self.status_desc.configure(text=self.lang_dict["status_desc_disabled"])
            self.toggle_btn.configure(text=self.lang_dict["btn_start"], fg_color="#6366F1", hover_color="#4F46E5")
            
        if self.tray_icon:
            self.tray_icon.title = f"{self.lang_dict['window_title']}: {self.lang_dict['status_active'] if active else self.lang_dict['status_disabled']}"

    def toggle_startup(self):
        enable = self.startup_var.get()
        self.config["startup"] = enable
        self.save_config()
        
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = sys.executable
            
        startup_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
        shortcut_path = os.path.join(startup_dir, "IntraWindows.lnk")
        
        try:
            # 1. HKCU Run Registry Key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
            if enable:
                target_cmd = f'"{exe_path}"'
                if not getattr(sys, 'frozen', False):
                    target_cmd = f'"{exe_path}" "{os.path.abspath(sys.argv[0])}"'
                if self.config.get("tray_start", False):
                    target_cmd += " --minimized"
                winreg.SetValueEx(key, "IntraWindows", 0, winreg.REG_SZ, target_cmd)
                
                # 2. Startup Folder Shortcut (.lnk)
                if os.path.exists(startup_dir):
                    args_flag = "--minimized" if self.config.get("tray_start", False) else ""
                    ps_sc = (
                        f'$s=(New-Object -COM WScript.Shell).CreateShortcut("{shortcut_path}"); '
                        f'$s.TargetPath="{exe_path}"; '
                        f'$s.Arguments="{args_flag}"; '
                        f'$s.WorkingDirectory="{REAL_APP_DIR}"; '
                        f'$s.Save()'
                    )
                    subprocess.run(["powershell", "-Command", ps_sc], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

                # 3. Task Scheduler fallback
                task_name = "IntraWindows"
                tr_cmd = f'"{exe_path}"' + (" --minimized" if self.config.get("tray_start", False) else "")
                subprocess.run(f'schtasks /create /f /tn "{task_name}" /sc onlogon /tr "{tr_cmd}"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

                self.log_message("[SİSTEM] Otomatik başlatma kaydı eklendi." if self.lang == "TR" else "[SYSTEM] Auto-start entry added.")
            else:
                try:
                    winreg.DeleteValue(key, "IntraWindows")
                except FileNotFoundError:
                    pass
                try:
                    if os.path.exists(shortcut_path):
                        os.remove(shortcut_path)
                except:
                    pass
                subprocess.run('schtasks /delete /f /tn "IntraWindows"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.log_message("[SİSTEM] Otomatik başlatma kaydı silindi." if self.lang == "TR" else "[SYSTEM] Auto-start entry deleted.")
            winreg.CloseKey(key)
        except Exception as e:
            self.log_message(f"[SİSTEM HATA] Başlangıç ayarı kaydedilemedi: {e}" if self.lang == "TR" else f"[SYS ERROR] Failed to configure startup: {e}")

    def fast_shutdown_cleanup(self):
        """Instant non-blocking cleanup for Windows shutdown."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                0,
                winreg.KEY_WRITE
            )
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            try:
                winreg.DeleteValue(key, "ProxyServer")
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
            ctypes.windll.wininet.InternetSetOptionW(0, 39, 0, 0)
            ctypes.windll.wininet.InternetSetOptionW(0, 37, 0, 0)
        except:
            pass

        if self.process:
            try:
                self.process.kill()
            except:
                pass
            self.process = None

        global _instance_socket
        if _instance_socket:
            try:
                _instance_socket.close()
            except:
                pass
            _instance_socket = None

        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass

    def setup_shutdown_handler(self):
        """Register OS shutdown signal handlers to prevent 'Apps preventing shutdown' dialogs."""
        try:
            def console_ctrl_handler(ctrl_type):
                self.fast_shutdown_cleanup()
                return True

            self._ctrl_handler = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_ulong)(console_ctrl_handler)
            ctypes.windll.kernel32.SetConsoleCtrlHandler(self._ctrl_handler, True)
        except Exception as e:
            print(f"Error setting console handler: {e}")

    def setup_tray_icon(self):
        if self.tray_icon:
            return
            
        try:
            icon_img_path = os.path.join(self.app_dir, "icon.ico")
            if not os.path.exists(icon_img_path):
                ensure_icon_files()
                
            icon_image = Image.open(icon_img_path)
            
            menu = pystray.Menu(
                pystray.MenuItem(self.lang_dict["tray_show"], lambda: self.root.after(0, self.show_window), default=True),
                pystray.MenuItem(self.lang_dict["tray_toggle"], lambda: self.root.after(0, self.toggle_bypass)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(self.lang_dict["tray_exit"], lambda: self.root.after(0, self.on_closing))
            )
            
            self.tray_icon = pystray.Icon(
                "Intra-Windows-Shield", 
                icon_image, 
                f"{self.lang_dict['window_title']}: {self.lang_dict['status_disabled']}", 
                menu
            )
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"Error starting tray icon: {e}")

    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def on_window_close(self):
        if self.tray_close_var.get():
            if not self.tray_icon:
                self.setup_tray_icon()
            self.root.withdraw()
            self.log_message("[SİSTEM] Arka plana küçültüldü. Sistem tepsisinden yönetebilirsiniz." if self.lang == "TR" else "[SYSTEM] Minimized to system tray.")
        else:
            self.on_closing()

    def on_closing(self):
        self.fast_shutdown_cleanup()
        
        # Reset DNS to DHCP if configured
        try:
            res = subprocess.run(
                ['netsh', 'interface', 'show', 'interface'],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in res.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 4 and parts[1].lower() == 'connected':
                    adapter = ' '.join(parts[3:])
                    subprocess.run(
                        ['netsh', 'interface', 'ip', 'set', 'dns', f'name={adapter}', 'source=dhcp'],
                        capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
                    )
        except:
            pass

        if self.root:
            try:
                self.root.destroy()
            except:
                pass
        sys.exit(0)

if __name__ == "__main__":
    sanitize_system_proxy_on_startup()
    check_single_instance()

    root = ctk.CTk()
    app = GoodbyeDpiGUI(root)
    app.setup_shutdown_handler()
    root.mainloop()
