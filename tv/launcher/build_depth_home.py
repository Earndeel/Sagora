# Copie de référence (2026-11-06) : la version exécutée est sur le Mac, ~/walter-tv/depth-home-build/.
# Le mot de passe de la clé du lanceur n'est pas dans le dépôt : variable HOME_KS_PASS (voir docs/EXPLOITATION.md).
from pathlib import os
import Path
import subprocess
import zipfile
import hashlib
import shutil

root = Path(__file__).resolve().parent
project = root / 'depth-home'
resources = project / 'res' / 'drawable'
resources.mkdir(parents=True, exist_ok=True)
(resources / 'home_icon.xml').write_text('''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="96dp" android:height="96dp" android:viewportWidth="96" android:viewportHeight="96">
<path android:fillColor="#143147" android:pathData="M0,0H96V96H0Z"/>
<path android:fillColor="#8DB9CC" android:pathData="M0,76L32,30L51,57L69,20L96,76Z"/>
<path android:fillColor="#EDF3F4" android:pathData="M54,42L69,20L82,43L70,35L65,42L61,36Z"/>
</vector>''')
(resources / 'home_banner.xml').write_text('''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="320dp" android:height="180dp" android:viewportWidth="320" android:viewportHeight="180">
<path android:fillColor="#143147" android:pathData="M0,0H320V180H0Z"/>
<path android:fillColor="#8DB9CC" android:pathData="M0,180L88,55L150,130L230,35L320,180Z"/>
<path android:fillColor="#EDF3F4" android:pathData="M195,79L230,35L266,89L237,68L225,81L215,67Z"/>
</vector>''')
sdk = root / 'android-tools'
aapt = next(sdk.rglob('aapt2'))
build_tools = aapt.parent
android_jar = next(sdk.rglob('android.jar'))
java_home = next((root / 'java-runtime').glob('*/Contents/Home'))
java = java_home / 'bin' / 'java'

def run(args):
    result = subprocess.run([str(arg) for arg in args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)

classes = project / 'classes'
dex = project / 'dex'
shutil.rmtree(classes, ignore_errors=True)
shutil.rmtree(dex, ignore_errors=True)
classes.mkdir()
dex.mkdir()
run([aapt, 'compile', '--dir', project / 'res', '-o', project / 'resources.zip'])
run([aapt, 'link', '-o', project / 'base.apk', '-I', android_jar, '--manifest', project / 'AndroidManifest.xml', '--min-sdk-version', '24', '--target-sdk-version', '29', '--version-code', '7', '--version-name', '1.6-sagora', '-A', project / 'assets', project / 'resources.zip'])
sources = sorted((project / 'src').rglob('*.java'))
run([java_home / 'bin' / 'javac', '--release', '8', '-encoding', 'UTF-8', '-classpath', android_jar, '-d', classes] + sources)
run([java, '-cp', build_tools / 'lib' / 'd8.jar', 'com.android.tools.r8.D8', '--min-api', '24', '--lib', android_jar, '--output', dex] + sorted(classes.rglob('*.class')))
with zipfile.ZipFile(project / 'base.apk', 'a', compression=zipfile.ZIP_DEFLATED) as z:
    z.write(dex / 'classes.dex', 'classes.dex')
run([build_tools / 'zipalign', '-f', '4', project / 'base.apk', project / 'aligned.apk'])
keystore = root / 'depth-home-signing.p12'
if not keystore.exists():
    run([java_home / 'bin' / 'keytool', '-genkeypair', '-keystore', keystore, '-storepass', os.environ['HOME_KS_PASS'], '-keypass', os.environ['HOME_KS_PASS'], '-alias', 'home', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '3650', '-dname', 'CN=Local Landscape Home'])
    keystore.chmod(0o600)
apk = root / 'depth-home.apk'
run([java, '-jar', build_tools / 'lib' / 'apksigner.jar', 'sign', '--ks', keystore, '--ks-pass', 'pass:' + os.environ['HOME_KS_PASS'], '--ks-key-alias', 'home', '--out', apk, project / 'aligned.apk'])
run([java, '-jar', build_tools / 'lib' / 'apksigner.jar', 'verify', apk])
(root / 'depth-home.sha256').write_text(hashlib.sha256(apk.read_bytes()).hexdigest())
print('Accueil construit et signature vérifiée : ' + str(apk.stat().st_size) + ' octets.')
