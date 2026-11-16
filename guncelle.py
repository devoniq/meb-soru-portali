"""MEB Öğrenme Etkinlikleri bağlantılarını toplar ve veri.js dosyasını yazar.

Çalıştırma:  python guncelle.py
- MEB ODSGM sınıf sayfalarından her dersin kitap bağlantısını okur.
- Her kitap PDF'ini indirir (_onbellek klasörüne), içindeki karekod bağlantılarını
  bulur ve türüne göre ayırır: cevap anahtarı, dinleme (mp3), video/EBA, ek metin.
- Sonucu veri.js dosyasına yazar; portal bu dosyayı okur.
Soru/metin kopyalanmaz: yalnızca bağlantılar, dosya boyutları ve kazanım/tema başlıkları.
"""
import collections
import concurrent.futures as cf
import datetime
import html
import json
import os
import re
import sys
import urllib.request

import pymupdf

KOK = os.path.dirname(os.path.abspath(__file__))
ONBELLEK = os.path.join(KOK, "_onbellek")
DUYURU = ("https://odsgm.meb.gov.tr/www/milli-egitim-bakanliginca-turkiye-yuzyili-maarif-modeli-"
          "olcme-ve-degerlendirme-yaklasimi-dogrultusunda-hazirlanan-ogrenme-etkinlikleri-seti039nin-"
          "ikinci-bolumu-yayimlandi/icerik/1765/tr")
SINIFLAR = {5: 1659, 6: 1660, 7: 1763, 9: 1661, 10: 1662, 11: 1764}
ILETISIM = "etkinlikrehberiapp@gmail.com"  # sorun bildirimlerinin gideceği adres (uygulama buradan okur)
UA = {"User-Agent": "Mozilla/5.0 (meb-soru-portali)"}

KOD = r"[A-ZÇĞİÖŞÜ]{1,8}(?:\.\d+){3,4}"
KAZANIM = re.compile(rf"\b({KOD})\.?\s*(.+?)\s+a\)", re.S)          # kazanım sayfası: "KOD Başlık a) ..."
ICINDEKILER = re.compile(rf"\b({KOD})\.?\s*(.+?)\s*\.{{5,}}\s*(\d+)")  # "KOD Başlık ...... 9"
BUYUK = r"[A-ZÇĞİÖŞÜÂÎÛ’'!?,&:\-]+"
TEMA = re.compile(rf"\b(\d+)\.\s*TEMA\s*:?\s*((?:{BUYUK}(?=\s|$)\s?)+)"
                  r"|\bTHEME\s*(\d+)\s+(.{2,70}?)\s*$")
BASILI = re.compile(r"^\s*(\d+)\s+\d+\.\s*Sınıf")


def istek(url, yontem="GET"):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA, method=yontem), timeout=120)


def coz(url):
    """Kısa bağlantının son adresini ve dosya boyutunu döndürür."""
    with istek(url, "HEAD") as r:
        return r.geturl(), int(r.headers.get("Content-Length") or 0)


def sinif_dersleri(sinif, sayfa_id):
    url = f"https://odsgm.meb.gov.tr/www/{sinif}sinif-ogrenme-etkinlikleri/icerik/{sayfa_id}"
    with istek(url) as r:
        metin = r.read().decode("utf-8", "replace")
    dersler = []
    for baslik, link in re.findall(r'<a [^>]*title="([^"]+)"[^>]*href="(https://meb\.ai/ankmac\d+)"', metin):
        ad = html.unescape(baslik)
        ad = re.sub(r"^\d+\.\s*Sınıf\s*", "", ad)
        ad = re.sub(r"\s*[–-]\s*PDF\s*$", "", ad).strip()
        dersler.append({"ad": ad, "kisa": link})
    return url, dersler


def indir(url, boyut):
    os.makedirs(ONBELLEK, exist_ok=True)
    yol = os.path.join(ONBELLEK, url.rsplit("/", 1)[-1])
    if os.path.exists(yol) and os.path.getsize(yol) == boyut:
        return yol
    with istek(url) as r, open(yol + ".part", "wb") as f:
        while parca := r.read(1 << 20):
            f.write(parca)
    os.replace(yol + ".part", yol)
    return yol


def icindekiler_mi(t):
    return "İÇİNDEKİLER" in t or len(ICINDEKILER.findall(temiz(t))) >= 2


def temiz(s):
    s = re.sub(r"[\x00-\x08\x0b-\x1f­]", "", s)  # kontrol karakterleri, yumuşak tire
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"(\w)- (\w)", r"\1\2", s)  # satır sonunda bölünmüş kelimeler
    return re.sub(r"(?:\s\S{1,2}){4,}(?=\s)", " …", s)  # formül artıkları: "f x x = ^ h"


def tr_baslik(s):
    """'OYUN DÜNYASI' -> 'Oyun Dünyası' (Türkçe i/ı kurallarıyla)."""
    def kelime(k):
        k = k.replace("I", "ı").replace("İ", "i").lower()
        return (k[0].replace("i", "İ").replace("ı", "I").upper() + k[1:]) if k else k
    kucuk = {"ve", "ile", "ya", "da", "de", "ki", "veya"}
    return " ".join(k.lower() if n and k.lower() in kucuk else kelime(k) for n, k in enumerate(s.split()))


def tur(url):
    """Bağlantının türü: cevap / dinleme / video / metin."""
    ad = url.split("?")[0].rsplit("/", 1)[-1].lower()
    if re.search(r"ck(_\d+)?\.pdf$", ad):
        return "cevap"
    if ad.endswith((".mp3", ".m4a", ".wav")):
        return "dinleme"
    if ad.endswith(".pdf"):
        return "metin"
    return "video"


def kitap_baglantilari(pdf_yolu):
    """Kitaptaki karekod bağlantılarını, basılı sayfa no ve kazanım/tema başlığıyla döndürür."""
    d = pymupdf.open(pdf_yolu)
    metinler = [d[i].get_text() for i in range(d.page_count)]
    # Basılı sayfa no = PDF sırası + sabit fark (kitap boyunca en sık görülen fark)
    farklar = collections.Counter(int(m.group(1)) - i for i, t in enumerate(metinler)
                                  if (m := BASILI.match(t)))
    fark = farklar.most_common(1)[0][0] if farklar else 1
    no = lambda i: i + fark  # noqa: E731

    sonuc, onceki_cevap, tema = [], -1, ""
    for i, sayfa in enumerate(d):
        t = temiz(metinler[i])
        if not icindekiler_mi(metinler[i]) and (m := TEMA.search(t)):
            sira, ad = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
            ad = re.split(r"\s+…|\s+ENGLISH YEAR", ad)[0].strip(" :")
            tema = f"{sira}. Tema: {tr_baslik(ad) if ad.isupper() else ad}"
        linkler = [l["uri"] for l in sayfa.get_links()
                   if re.match(r"https?://([\w-]+\.)*(meb\.ai|eba\.gov\.tr|meb\.gov\.tr)/", l.get("uri", ""))]
        for u in dict.fromkeys(linkler):
            sonuc.append({"kisa": u, "i": i, "tema": tema})
    # Cevap anahtarlarına başlık: önceki cevap anahtarından sonraki ilk kazanım sayfası, yoksa tema
    for c in sonuc:
        c["sayfa"] = str(no(c["i"]))
    return d.page_count, sonuc, metinler, no


def basliklandir(cevaplar, metinler, no):
    # İçindekiler: (basılı sayfa, kod, başlık) — kazanım sayfasında kod okunamazsa yedek
    icindekiler = sorted({(int(m.group(3)), m.group(1), m.group(2).strip(" ."))
                          for t in metinler if icindekiler_mi(t)
                          for m in ICINDEKILER.finditer(temiz(t))})
    onceki = -1
    for c in cevaplar:
        i = c["i"]
        c["baslik"] = c["tema"]
        for j in range(onceki + 1, i + 1):
            if icindekiler_mi(metinler[j]):
                continue
            if m := KAZANIM.search(temiz(metinler[j])[:800]):
                ad = next((e[2] for e in icindekiler if e[1] == m.group(1)), m.group(2))
                c["baslik"] = f"{m.group(1)} {ad}".rstrip(" .")[:220]
                if no(j) != no(i):
                    c["sayfa"] = f"{no(j)}–{no(i)}"
                break
        else:
            bas = no(onceki + 1)
            aday = [e for e in icindekiler if bas <= e[0] <= no(i)]
            if aday:
                sayfa, kod, ad = aday[0]
                c["baslik"] = f"{kod} {ad}"[:220]
                c["sayfa"] = f"{sayfa}–{no(i)}" if sayfa != no(i) else str(sayfa)
        onceki = i


def ders_isle(sinif, ders):
    ders.update(cevaplar=[], ekler=[], kirik=[])
    try:
        url, boyut = coz(ders["kisa"])
    except Exception as e:
        ders["hata"] = f"MEB'in kitap bağlantısı çalışmıyor ({e})"
        print(f"  {sinif}. sınıf {ders['ad']}: KİTAP BAĞLANTISI ÇALIŞMIYOR – {e}", flush=True)
        return ders
    ders.update(url=url, boyut=boyut)
    sayfa_sayisi, baglantilar, metinler, no = kitap_baglantilari(indir(url, boyut))
    ders["sayfa"] = sayfa_sayisi
    gorulen = set()
    for b in baglantilar:
        try:
            b["url"], b["boyut"] = coz(b["kisa"]) if "meb.ai/" in b["kisa"] else (b["kisa"], 0)
        except Exception:
            ders["kirik"].append(b["kisa"])
            continue
        if b["url"] in gorulen or b["url"] == url:
            continue
        gorulen.add(b["url"])
        b["tur"] = tur(b["url"])
        (ders["cevaplar"] if b["tur"] == "cevap" else ders["ekler"]).append(b)
    basliklandir(ders["cevaplar"], metinler, no)
    for b in ders["cevaplar"] + ders["ekler"]:
        for k in ("i", "tema") if b["tur"] == "cevap" else ("i",):
            b.pop(k, None)
    print(f"  {sinif}. sınıf {ders['ad']}: {sayfa_sayisi} sayfa, {len(ders['cevaplar'])} cevap anahtarı, "
          f"{len(ders['ekler'])} ek materyal" + (f", {len(ders['kirik'])} KIRIK" if ders["kirik"] else ""),
          flush=True)
    return ders


def main():
    veri = {"guncelleme": datetime.date.today().isoformat(), "duyuru": DUYURU, "iletisim": ILETISIM, "siniflar": []}
    isler, hatalar = [], []
    with cf.ThreadPoolExecutor(4) as havuz:
        for sinif, sid in SINIFLAR.items():
            sayfa, dersler = sinif_dersleri(sinif, sid)
            print(f"{sinif}. sınıf: {len(dersler)} ders bulundu", flush=True)
            veri["siniflar"].append({"sinif": sinif, "sayfa": sayfa, "dersler": dersler})
            isler += [havuz.submit(ders_isle, sinif, d) for d in dersler]
        for f in cf.as_completed(isler):
            try:
                f.result()
            except Exception as e:
                hatalar.append(str(e))
                print("  HATA:", e, flush=True)
    with open(os.path.join(KOK, "veri.js"), "w", encoding="utf-8") as f:
        f.write("window.VERI = " + json.dumps(veri, ensure_ascii=False, indent=1) + ";\n")
    dersler = [d for s in veri["siniflar"] for d in s["dersler"]]
    print(f"\nBitti: {len(dersler)} ders, {sum(len(d['cevaplar']) for d in dersler)} cevap anahtarı, "
          f"{sum(len(d['ekler']) for d in dersler)} ek materyal, "
          f"{sum(len(d['kirik']) for d in dersler)} kırık karekod bağlantısı, "
          f"{sum('hata' in d for d in dersler)} çalışmayan kitap, {len(hatalar)} hata. veri.js yazıldı.")
    return 1 if hatalar else 0


if __name__ == "__main__":
    sys.exit(main())
