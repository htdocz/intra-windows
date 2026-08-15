# 🛡️ Intra Turkey Windows Secure Shield

Select Language:
* [Türkçe Kılavuz (TR)](#-intra-turkey-windows-secure-shield-tr)
* [English Guide (EN)](#-intra-turkey-windows-secure-shield-en)

---

## 🛡️ Intra Turkey Windows Secure Shield (TR)

Intra Turkey, Jigsaw's Android Intra kütüphanelerini temel alarak Windows için özel olarak geliştirilmiş **çift protokol tünelleme (SOCKS5 + HTTP Proxy)** ve **paket parçalama (DPI Bypass)** aracıdır. Türkiye'deki İnternet Servis Sağlayıcılarının (Türk Telekom, Superonline vb.) uyguladığı DNS zehirlemelerini ve TLS el sikışması (Client Hello) bazlı sansürleri (Discord, YouTube, sosyal medya engelleri vb.) aşmak için tasarlanmıştır.

### ✨ Öne Çıkan Özellikler

* **🚀 Çift Protokol Desteği:** Aynı anda hem SOCKS5 (`127.0.0.1:10808`) hem de evrensel olarak tüm Windows uygulamalarının tanıdığı HTTP/HTTPS Proxy (`127.0.0.1:10809`) protokollerini çalıştırır.
* **🛡️ Paket Parçalama (SNI Splitting):** Giden TLS el sıkışma paketlerini küçük parçalara bölerek sansür mekanizmalarının (DPI - Deep Packet Inspection) paket içeriğini okumasını engeller ve bağlantı kesilmesinin (RST) önüne geçer.
* **🔒 Şifreli DNS (DoH):** Alan adı sorgularını şifreli DNS-over-HTTPS (Cloudflare, Google, Quad9, AdGuard vb.) üzerinden yaparak DNS zehirlemelerini tamamen engeller.
* **🌍 Çoklu Dil Desteği:** TR / EN / RU / DE / AZ dillerinde tam yerelleştirilmiş arayüz desteği.
* **💻 Modern Slate Temalı GUI:** CustomTkinter ile oluşturulmuş, karanlık mod uyumlu, pürüzsüz geçişlere sahip şık bir kullanıcı arayüzü.
* **🎮 Tek Tıkla Discord Güvenli Başlat:** Discord'un güncelleme sunucularına bağlanırken yaşadığı kilitlenmeleri aşmak için tasarlanmış özel güvenli başlatıcı.
* **🚨 Acil Durum Kurtarıcısı:** Tünel açıkken bilgisayarda yaşanabilecek olası ağ kilitlenmelerini tek tıkla çözen `ACIL_DURUM_AG_SIFIRLAMA.bat` aracı.

### 📁 Proje Klasör Yapısı

```text
├── win_backend/                  # Go dilinde yazılmış tünel ve DoH motoru
│   ├── main.go                   # Tünel ana kaynak kodu
│   ├── go.mod                    # Go bağımlılık dosyası
│   └── ...
├── goodbyedpi-gui-win/           # Python ile yazılmış Slate temalı arayüz (GUI)
│   ├── app.py                    # Arayüz ana kaynak kodu
│   ├── requirements.txt          # Gerekli Python kütüphaneleri
│   ├── bin/                      # Derlenmiş Go binary dosyasının konumu (intra-windpi.exe)
│   └── ...
├── derle.bat                     # Projeyi tek dosya EXE (IntraTurkey.exe) yapan derleme betiği
├── ACIL_DURUM_AG_SIFIRLAMA.bat   # Windows ağ ayarlarını sıfırlayan acil durum betiği
├── .gitignore                    # Gereksiz/geçici build dosyalarını filtreleyen Git dosyası
└── README.md                     # Proje tanıtım belgesi (Bu dosya)
```

### 🚀 Kurulum ve Çalıştırma

#### Yöntem 1: Kaynak Koddan Çalıştırma (Geliştiriciler İçin)

Projenin çalışması için bilgisayarınızda **Python 3.10+** ve Go backend'i derlemek için **Go 1.20+** kurulu olmalıdır.

1. Bağımlılıkları yükleyin:
   ```bash
   pip install -r goodbyedpi-gui-win/requirements.txt
   ```
2. Go backend modülünü derleyin:
   ```bash
   go build -ldflags="-s -w" -o goodbyedpi-gui-win/bin/intra-windpi.exe ./win_backend
   ```
3. Arayüzü başlatın (Yönetici yetkileri istenir):
   ```bash
   python goodbyedpi-gui-win/app.py
   ```

#### Yöntem 2: Tek Parça EXE Olarak Derleme (Her Bilgisayarda Çalıştırma)

Projeyi bilgisayarında Python veya Go yüklü olmayan herhangi bir Windows kullanıcısıyla paylaşmak için tek bir `.exe` haline getirebilirsiniz.

1. Ana klasörde bulunan **`derle.bat`** dosyasına çift tıklayın.
2. Derleyici otomatik olarak `pyinstaller` kütüphanesini kuracak, simgeleri hazırlayacak ve paketleme işlemini yapacaktır.
3. İşlem tamamlandığında, ana dizinde **`IntraTurkey.exe`** adında tek parçalık bağımsız bir dosya oluşacaktır.

---

## 🛡️ Intra Turkey Windows Secure Shield (EN)

Intra Turkey is a **dual-protocol tunneling (SOCKS5 + HTTP Proxy)** and **packet fragmentation (DPI Bypass)** tool developed specifically for Windows, based on Jigsaw's Android Intra libraries. It is designed to bypass DNS poisoning and TLS handshake (Client Hello) based censorship (such as Discord, YouTube, social media blocks, etc.) implemented by Turkish ISPs (Turk Telekom, Superonline, etc.).

### ✨ Features

* **🚀 Dual Protocol Support:** Runs both SOCKS5 (`127.0.0.1:10808`) and standard HTTP/HTTPS Proxy (`127.0.0.1:10809`) protocols, natively supported by all Windows applications.
* **🛡️ Packet Fragmentation (SNI Splitting):** Splits outbound TLS handshake packets into smaller fragments, preventing DPI (Deep Packet Inspection) filters from reading the host headers, bypassing connection resets (RST).
* **🔒 Encrypted DNS (DoH):** Resolves DNS queries via encrypted DNS-over-HTTPS (Cloudflare, Google, Quad9, AdGuard, etc.) to completely bypass DNS poisoning.
* **🌍 Multi-Language Support:** Fully localized user interface in TR / EN / RU / DE / AZ.
* **💻 Modern Slate-Themed GUI:** Sleek dark-mode interface built with CustomTkinter.
* **🎮 1-Click Secure Discord Launcher:** Special launcher designed to bypass update connection freezes in Discord.
* **🚨 Emergency Restorer:** A 1-click batch script `ACIL_DURUM_AG_SIFIRLAMA.bat` to restore Windows network settings to default DHCP.

### 📁 Project Folder Structure

```text
├── win_backend/                  # Go-based tunnel and DoH engine
│   ├── main.go                   # Tunnel source code
│   ├── go.mod                    # Go module dependencies
│   └── ...
├── goodbyedpi-gui-win/           # Python-based CustomTkinter GUI
│   ├── app.py                    # GUI source code
│   ├── requirements.txt          # Python dependencies
│   ├── bin/                      # Compiled Go binary (intra-windpi.exe)
│   └── ...
├── derle.bat                     # Compiler script to build IntraTurkey.exe
├── ACIL_DURUM_AG_SIFIRLAMA.bat   # Emergency network settings restorer
├── .gitignore                    # Files excluded from git
└── README.md                     # Documentation (This file)
```

### 🚀 Setup and Installation

#### Method 1: Running from Source (For Developers)

To run the project, you must have **Python 3.10+** and **Go 1.20+** installed on your system.

1. Install dependencies:
   ```bash
   pip install -r goodbyedpi-gui-win/requirements.txt
   ```
2. Compile the Go backend module:
   ```bash
   go build -ldflags="-s -w" -o goodbyedpi-gui-win/bin/intra-windpi.exe ./win_backend
   ```
3. Run the GUI application (Administrator privileges required):
   ```bash
   python goodbyedpi-gui-win/app.py
   ```

#### Method 2: Compile as Standalone EXE (Portable Mode)

To compile the application into a single executable that can run on any Windows PC without Python/Go:

1. Double-click the **`derle.bat`** file in the root directory.
2. The compiler will check dependencies, install PyInstaller, and bundle everything.
3. Once complete, you will find a standalone **`IntraTurkey.exe`** in the root directory.
