# 🛡️ Jigsaw Intra Windows Secure Shield (Güvenli Kalkan GUI)

Bu proje, Jigsaw'un ünlü mobil sansür aşma aracı olan **Intra** (DNS-over-HTTPS ve TCP Client Hello fragmentation) motorunu temel alan, Windows için özel olarak geliştirilmiş **hafif ve güçlü** bir arayüz ve proxy yazılımıdır.

GoodbyeDPI gibi araçlar Windows çekirdek düzeyinde sürücü (WinDivert) kurup sistemi riske atabilirken; bu proje, Jigsaw Intra'nın Go dilindeki orijinal paket bölme (split-hello) ve DNS-over-HTTPS (DoH) kütüphanelerini kullanarak **Local SOCKS5 Proxy** kurar ve Windows sistem proxy ayarlarınızı anlık olarak yönetir.

Arayüz **CustomTkinter** kullanılarak geliştirilmiştir. Sadece **12-18 MB RAM** tüketir ve 0% CPU ile arka planda sessizce çalışır.

## ✨ Öne Çıkan Özellikler

*   **Jigsaw Go Engine:** DoH çözücü ve TLS Client Hello paket bölme (sni-splitting) işlemleri, Jigsaw Intra'nın kendi resmi Go kodları ile doğrudan Windows üzerinde çalıştırılır.
*   **Tek Tıkla Başlat/Durdur:** Kalkanı saniyeler içinde devreye alabilir veya devreden çıkarabilirsiniz.
*   **Windows Sistem Proxy Entegrasyonu:** Kalkan başladığında Windows SOCKS5 proxy ayarı (Varsayılan: `127.0.0.1:10808`) otomatik etkinleştirilir. Chrome, Edge, Brave, Spotify ve Discord gibi sistem proxy'sini kullanan tüm uygulamalar anında sansürsüz bağlantıya geçer.
*   **Orijinal Proxy Koruma Ayarı:** Uygulama durdurulduğunda veya kapatıldığında, Windows proxy ayarlarınızı bozmaz; eğer şirket proxy'si gibi özel bir ayarınız varsa otomatik olarak onu geri yükler.
*   **Görsel Durum Göstergesi:** Canlı renk değiştiren parlayan durum ışığı ile bypass durumunu anında görebilirsiniz.
*   **Seçilebilir Güvenli DoH Servisi:** Arayüz üzerinden **Cloudflare**, **Google**, **Quad9** veya **AdGuard** gibi DoH sunucularını seçebilirsiniz. DNS sorguları şifrelenerek ISS (Türk Telekom, Superonline vb.) engellemelerini %100 aşar.
*   **Otomatik Geri Bağlanma Watchdog:** Arka planda çalışan Go proxy süreci çökerse veya sonlanırsa, sistem bunu otomatik algılayıp 2 saniye içinde tekrar bağlanır.
*   **Sistem Tepsisine (System Tray) Küçülme:** Uygulama kapatıldığında veya simge durumuna alındığında arka planda çalışmaya devam eder ve Windows bildirim alanında (sağ altta) gizlenir. Çift tıklayarak arayüzü tekrar açabilirsiniz.
*   **Windows Başlangıcında Otomatik Başlatma:** Bilgisayarınız her açıldığında kalkanın otomatik olarak (arka planda / sistem tepsisinde sessizce) çalışmasını sağlayabilirsiniz.

## 🚀 Çalıştırma Talimatları

Uygulamanın çalışabilmesi için bilgisayarınızda Python yüklü olmalıdır.

1.  **Tek Tıkla Kurun ve Çalıştırın:**
    *   Klasördeki **`run_admin.bat`** dosyasına çift tıklayın.
    *   Script, sisteminizde gerekli Python kütüphaneleri (customtkinter, pystray, pillow) yüklü değilse onları otomatik olarak kuracak ve uygulamayı başlatacaktır.
    *   Eğer ilk açılışta `bin/intra-windpi.exe` dosyası bulunamazsa, sisteminizde kurulu Go derleyicisini otomatik kullanarak arka planda kodu derleyecektir (Derlenmiş dosya şu an klasörde hazırdır, bu yüzden doğrudan çalışacaktır!).

## 🛠️ Klasör Yapısı

*   `app.py`: Ana Python arayüz kodu (Proxy ayarları, UI ve Tray yönetimi).
*   `run_admin.bat`: Tek tıkla bağımlılıkları yükleme ve yönetici yetkisi ile çalıştırma betiği.
*   `requirements.txt`: Python paket bağımlılıkları listesi.
*   `config.json`: Seçtiğiniz DNS, port ve başlangıç ayarlarını tutan otomatik oluşturulan ayar dosyası.
*   `bin/intra-windpi.exe`: Jigsaw Intra Go kütüphaneleriyle derlenmiş hafif Windows arka plan proxy servisi.
*   `win_backend/`: Go kaynak kodları (Portlama ve SOCKS5 proxy entegrasyonu).
