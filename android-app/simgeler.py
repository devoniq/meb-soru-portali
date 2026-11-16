"""Uygulama simgelerini ve açılış ekranını ../ikon.svg tasarımından üretir (PyMuPDF ile)."""
import glob, os, pymupdf

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "android", "app", "src", "main", "res")
KIRMIZI = "#b3122e"
CIZIM = ('<path d="M116 150c50-20 100-20 140 10v220c-40-30-90-30-140-10z" fill="#fff"/>'
         '<path d="M396 150c-50-20-100-20-140 10v220c40-30 90-30 140-10z" fill="#fde3e7"/>'
         '<circle cx="352" cy="352" r="62" fill="#0f6b5c" stroke="#fff" stroke-width="14"/>'
         '<path d="M326 352l18 18 34-36" fill="none" stroke="#fff" stroke-width="16" '
         'stroke-linecap="round" stroke-linejoin="round"/>')
ORTALI = lambda olcek: f'<g transform="translate(256 256) scale({olcek}) translate(-265 -272)">{CIZIM}</g>'


def ciz(svg_govde, w, h, yol, alfa=False, viewbox="0 0 512 512"):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{viewbox}">'
           f'{svg_govde}</svg>')
    sayfa = pymupdf.open(stream=svg.encode(), filetype="svg")[0]
    pm = sayfa.get_pixmap(matrix=pymupdf.Matrix(w / sayfa.rect.width, h / sayfa.rect.height), alpha=alfa)
    pm.save(yol)


YOGUNLUK = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
for ad, k in YOGUNLUK.items():
    klasor = os.path.join(RES, f"mipmap-{ad}")
    b = round(48 * k)
    ciz(f'<rect width="512" height="512" rx="110" fill="{KIRMIZI}"/>{ORTALI(1)}', b, b,
        os.path.join(klasor, "ic_launcher.png"), alfa=True)
    ciz(f'<circle cx="256" cy="256" r="256" fill="{KIRMIZI}"/>{ORTALI(0.9)}', b, b,
        os.path.join(klasor, "ic_launcher_round.png"), alfa=True)
    f = round(108 * k)  # uyarlanabilir simge ön yüzü: güvenli alan ortadaki 66/108
    ciz(ORTALI(0.62), f, f, os.path.join(klasor, "ic_launcher_foreground.png"), alfa=True)

with open(os.path.join(RES, "values", "ic_launcher_background.xml"), "w", encoding="utf-8") as d:
    d.write(f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
            f'    <color name="ic_launcher_background">{KIRMIZI}</color>\n</resources>\n')

# Açılış ekranı: kırmızı zemin, ortada simge
for yol in glob.glob(os.path.join(RES, "drawable*", "splash.png")):
    w, h = pymupdf.Pixmap(yol).width, pymupdf.Pixmap(yol).height
    s = min(w, h) * 0.45
    govde = (f'<rect width="{w}" height="{h}" fill="{KIRMIZI}"/>'
             f'<g transform="translate({(w - s) / 2} {(h - s) / 2}) scale({s / 512})">'
             f'<g transform="translate(256 256) scale(1.3) translate(-265 -272)">{CIZIM}</g></g>')
    ciz(govde, w, h, yol, viewbox=f"0 0 {w} {h}")
print("Simgeler ve açılış ekranı üretildi.")
