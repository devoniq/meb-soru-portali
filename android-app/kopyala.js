// Portal dosyalarını (bir üst klasör) www klasörüne kopyalar; Capacitor uygulamaya bunları koyar.
const fs = require("fs"), path = require("path");
const kaynak = path.join(__dirname, ".."), hedef = path.join(__dirname, "www");
fs.rmSync(hedef, {recursive: true, force: true});
fs.mkdirSync(hedef);
for (const f of ["index.html", "veri.js", "ikon.svg", "ikon-192.png", "ikon-512.png"])
  fs.copyFileSync(path.join(kaynak, f), path.join(hedef, f));
console.log("www klasörü hazır.");
