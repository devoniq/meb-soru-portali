# MEB Etkinlik Kitapları – Nasıl güncellenir?

## Bu portal ne yapıyor?
MEB'in "Öğrenme Etkinlikleri Seti" kitaplarını (5, 6, 7, 9, 10, 11. sınıflar) sınıf → ders
düzeninde listeler. Her dersin altında **cevap anahtarları** ve **ek materyaller**
(İngilizce/Türkçe dinleme sesleri, EBA videoları, ek okuma metinleri) vardır.

Hiçbir soru veya metin kopyalanmaz: portal yalnızca MEB'in kendi dosyalarına bağlantı verir.
(Kitapların 4. sayfasında "metin, soru ve şekiller… alınıp yayımlanamaz" yazar; bu yüzden böyle.)

## Neden bir "güncelleme" komutu var?
Cevap anahtarı bağlantıları kitapların **içindeki karekodlarda** saklı ve numaraları tahmin
edilemiyor. Bu yüzden `guncelle.py` her kitabı indirip içini okur, bağlantıları çıkarır ve
`veri.js` dosyasına yazar. Portal sadece bu dosyayı okur.

## Ne zaman çalıştırmalı?
- MEB yeni bir set/bölüm yayımladığında,
- 9. sınıf Tarih gibi çalışmayan bir kitabı MEB düzelttiğinde,
- Ayda bir kontrol amaçlı.

## Nasıl çalıştırılır?
Komut satırına (PowerShell) şunu yapıştırın:

```
cd C:\Users\User\projects\meb-soru-portali; python -X utf8 guncelle.py
```

İlk çalıştırmada kitapları indirdiği için birkaç dakika sürer (~700 MB, `_onbellek`
klasörüne). Sonraki çalıştırmalarda değişmeyen kitaplar tekrar indirilmez.

Sonunda şöyle bir özet görürsünüz:

```
Bitti: 45 ders, 351 cevap anahtarı, 57 ek materyal, 0 kırık karekod bağlantısı, 1 çalışmayan kitap, 0 hata.
```

"çalışmayan kitap" = MEB'in sayfasındaki bağlantı bozuk (16.11.2026 itibarıyla 9. sınıf Tarih).

## Canlı siteye gönderme
Portal https://devoniq.github.io/meb-soru-portali/ adresinde yayında. Yukarıdaki komut yalnızca
bu bilgisayardaki `veri.js` dosyasını yeniler; telefonlarda da görünmesi için gönderin:

```
cd C:\Users\User\projects\meb-soru-portali; git commit -am "Bağlantılar güncellendi"; git push
```

GitHub sitesi yaklaşık 1 dakika içinde yenilenir. "nothing to commit" yazarsa değişen bir şey
yok demektir, sorun değil.

## Yeni bir set yayımlanırsa
Sınıf sayfalarının adresleri `guncelle.py` dosyasının başındaki `SINIFLAR` satırındadır
(sınıf → MEB sayfa numarası). MEB yeni sayfa açarsa bu satırın güncellenmesi gerekir;
bunu Claude'a "MEB yeni set yayımladı, portalı güncelle" diyerek yaptırabilirsiniz.

## Android uygulaması (APK)
Uygulamanın adı **Etkinlik Kitapları Rehberi** (bilerek "MEB" ile başlamıyor, MEB logosu yok,
ilk açılışta "resmî değildir" bilgilendirmesi çıkıyor). Uygulama listeyi her açılışta canlı siteden
(`veri.js`) çeker. Bu yüzden **bağlantıları güncelleyip `git push` yapmanız yeterli; yeni APK gerekmez.**
İnternet yoksa uygulamanın içindeki son liste gösterilir.

Yeni APK yalnızca görünüş veya davranış (index.html) değiştiğinde gerekir:

```
cd C:\Users\User\projects\meb-soru-portali; powershell -ExecutionPolicy Bypass -File .\apk-yap.ps1
```

Sonuç bu klasörde `Etkinlik-Kitaplari-Rehberi.apk` olarak çıkar (~3 MB). Yeni sürümü dağıtmadan önce
`android-app\android\app\build.gradle` içindeki `versionCode` sayısını 1 artırın (Claude'a yaptırabilirsiniz).

**Telefona kurma:** APK'yı WhatsApp/e-posta ile gönderin → telefonda dosyaya dokunun → "Bu kaynaktan
yüklemeye izin ver" → Yükle.

**⚠️ İmza anahtarı:** `android-app\imza` klasörü uygulamanın imzasıdır ve GitHub'a gönderilmez.
Kaybolursa yeni sürümler eski sürümün üzerine kurulamaz (önce eskisini silmek gerekir).
Bu klasörü bir USB belleğe / Google Drive'a yedekleyin.

Klasörler: `android-app` (Android projesi), `_araclar` (Java 21, yalnızca APK üretmek için;
silinirse Claude yeniden indirir). İkisi de GitHub'a gönderilmez.

## Bilgisayarda deneme
```
python -m http.server 5070 --directory C:\Users\User\projects\meb-soru-portali
```
Sonra tarayıcıda http://localhost:5070 adresini açın.
