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

## Bilgisayarda deneme
```
python -m http.server 5070 --directory C:\Users\User\projects\meb-soru-portali
```
Sonra tarayıcıda http://localhost:5070 adresini açın.
