# Etkinlik Kitapları Rehberi - Android APK üretir.
# Çalıştırma: cd C:\Users\User\projects\meb-soru-portali; .\apk-yap.ps1
# Sonuç: bu klasörde "Etkinlik-Kitaplari-Rehberi.apk"
$ErrorActionPreference = "Stop"
$kok = $PSScriptRoot
$jdk = Get-ChildItem "$kok\_araclar" -Directory -Filter "jdk-*" | Select-Object -First 1
if (-not $jdk) { throw "Java 21 bulunamadı (_araclar klasörü). Claude'a 'APK için Java'yı yeniden indir' deyin." }
if (-not (Test-Path "$kok\android-app\imza\imza.properties")) { throw "İmza anahtarı bulunamadı (android-app\imza). Yedekten geri koyun." }
$env:JAVA_HOME = $jdk.FullName
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"

Push-Location "$kok\android-app"
try {
    npm run esitle
    if ($LASTEXITCODE) { throw "Dosyalar uygulamaya kopyalanamadı." }
    Push-Location android
    try {
        .\gradlew.bat assembleRelease --console=plain
        if ($LASTEXITCODE) { throw "Derleme başarısız." }
    } finally { Pop-Location }
} finally { Pop-Location }

Copy-Item "$kok\android-app\android\app\build\outputs\apk\release\app-release.apk" "$kok\Etkinlik-Kitaplari-Rehberi.apk" -Force
Write-Host "`nHazır: $kok\Etkinlik-Kitaplari-Rehberi.apk" -ForegroundColor Green
