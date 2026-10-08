$ErrorActionPreference = "Stop"

$JAVA_DIR = "C:\Program Files\Android\Android Studio\jbr\bin"
$SDK_BUILD_TOOLS = "C:\android sdk\build-tools\36.0.0"
$ANDROID_JAR = "C:\android sdk\platforms\android-37.0\android.jar"

$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
$env:PATH = "$JAVA_DIR;$SDK_BUILD_TOOLS;$env:PATH"

$BASE = "D:\Privada\bocchi\PinkChan_Shimeji\PinkChan_Final\android_app"
$APP_SRC = "$BASE\app\src\main"
$BUILD_DIR = "$BASE\build"

Write-Host "==============================================" -ForegroundColor Magenta
Write-Host "   Compilando PinkChan Shimeji APK para Android" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Magenta

# Limpiar build anterior
if (Test-Path $BUILD_DIR) {
    Remove-Item -Recurse -Force $BUILD_DIR
}
New-Item -ItemType Directory -Force -Path "$BUILD_DIR\gen", "$BUILD_DIR\obj", "$BUILD_DIR\dex" | Out-Null

# 1. Crear debug keystore si no existe
$KEYSTORE = "$BASE\debug.keystore"
if (-not (Test-Path $KEYSTORE)) {
    Write-Host "[1/7] Generando keystore de firma..." -ForegroundColor Yellow
    & "$JAVA_DIR\keytool.exe" -genkeypair -validity 10000 `
      -dname "CN=PinkChan,O=Bocchi,C=US" `
      -keystore $KEYSTORE -storepass android -keypass android `
      -alias androiddebugkey -keyalg RSA -keysize 2048
}

# 2. Compilar recursos con AAPT2
Write-Host "[2/7] Compilando recursos XML e imagenes con AAPT2..." -ForegroundColor Yellow
& "$SDK_BUILD_TOOLS\aapt2.exe" compile --dir "$APP_SRC\res" -o "$BUILD_DIR\compiled_res.zip"

# 3. Vincular recursos y generar R.java
Write-Host "[3/7] Vinculando recursos y generando R.java..." -ForegroundColor Yellow
& "$SDK_BUILD_TOOLS\aapt2.exe" link `
  -I $ANDROID_JAR `
  "$BUILD_DIR\compiled_res.zip" `
  --manifest "$APP_SRC\AndroidManifest.xml" `
  --java "$BUILD_DIR\gen" `
  --auto-add-overlay `
  --min-sdk-version 26 `
  --target-sdk-version 35 `
  -o "$BUILD_DIR\base.apk"
if ($LASTEXITCODE -ne 0) { throw "Error en aapt2 link" }

# 4. Compilar codigo Java con javac
Write-Host "[4/7] Compilando clases Java con OpenJDK 25 (--release 8)..." -ForegroundColor Yellow
$javaSources = Get-ChildItem -Path "$APP_SRC\java", "$BUILD_DIR\gen" -Recurse -Filter "*.java" | Select-Object -ExpandProperty FullName
& "$JAVA_DIR\javac.exe" --release 8 -cp $ANDROID_JAR -d "$BUILD_DIR\obj" $javaSources
if ($LASTEXITCODE -ne 0) { throw "Error en javac" }

# 5. Generar bytecode Dalvik con D8
Write-Host "[5/7] Generando classes.dex con D8..." -ForegroundColor Yellow
$classFiles = Get-ChildItem -Path "$BUILD_DIR\obj" -Recurse -Filter "*.class" | Select-Object -ExpandProperty FullName
& "$SDK_BUILD_TOOLS\d8.bat" --release --min-api 26 --output "$BUILD_DIR\dex" $classFiles
if ($LASTEXITCODE -ne 0) { throw "Error en d8" }

# 6. Empaquetar classes.dex y assets en el APK
Write-Host "[6/7] Empaquetando dex y skins assets en base.apk..." -ForegroundColor Yellow
Push-Location "$BUILD_DIR\dex"
& "$JAVA_DIR\jar.exe" -uf "$BUILD_DIR\base.apk" classes.dex
Pop-Location

Push-Location "$APP_SRC"
& "$JAVA_DIR\jar.exe" -uf "$BUILD_DIR\base.apk" assets
Pop-Location

# 7. Zipalign y Apksigner
Write-Host "[7/7] Alineando (zipalign) y firmando APK con apksigner..." -ForegroundColor Yellow
$ALIGNED_APK = "$BUILD_DIR\aligned.apk"
$FINAL_APK = "$BASE\PinkChan_Shimeji.apk"
$ROOT_APK = "D:\Privada\bocchi\PinkChan_Shimeji\PinkChan_Final\PinkChan_Shimeji.apk"

& "$SDK_BUILD_TOOLS\zipalign.exe" -p -f 4 "$BUILD_DIR\base.apk" $ALIGNED_APK

& "$SDK_BUILD_TOOLS\apksigner.bat" sign `
  --ks $KEYSTORE `
  --ks-pass pass:android `
  --key-pass pass:android `
  --ks-key-alias androiddebugkey `
  --out $FINAL_APK `
  $ALIGNED_APK

Copy-Item $FINAL_APK $ROOT_APK -Force

Write-Host "==============================================" -ForegroundColor Green
Write-Host " [OK] APK COMPILADO Y FIRMADO EXITOSAMENTE!" -ForegroundColor Green
Write-Host " Ubicacion: $FINAL_APK" -ForegroundColor Cyan
Write-Host " Raiz:      $ROOT_APK" -ForegroundColor Cyan
$sizeMb = [math]::Round((Get-Item $FINAL_APK).Length / 1MB, 2)
Write-Host " Tamano:    $sizeMb MB" -ForegroundColor Yellow
Write-Host "==============================================" -ForegroundColor Green

