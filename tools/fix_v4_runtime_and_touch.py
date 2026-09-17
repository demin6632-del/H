from pathlib import Path
import re
import base64
import io
import subprocess
import sys
import tempfile

FILES = [Path('NEW_DARK_RPG/index.html'), Path('android/app/src/main/assets/index.html')]

# Исправляем закрытие внешнего V4 script.
for p in FILES:
    s = p.read_text(encoding='utf-8')
    s = s.replace('<script src="art-atlas-v4.js">', '<script src="art-atlas-v4.js"></script><script>')
    p.write_text(s, encoding='utf-8')

# Перед установкой финального V60 удаляем любой старый native touch bridge.
p = Path('android/app/src/main/java/com/chronicles/abyss/MainActivity.java')
s = p.read_text(encoding='utf-8')
s = s.replace('import android.view.MotionEvent;\n', '')
start = s.find('    /* ANDROID-NATIVE-TOUCH-FALLBACK-V60')
if start >= 0:
    class_start = s.find('    private static final class TouchWebView', start)
    class_end = s.find('\n    @Override\n    protected void onCreate', class_start)
    if class_start < 0 or class_end < 0:
        raise SystemExit('MainActivity V60 TouchWebView block found but could not be removed')
    s = s[:start] + s[class_end:]
    s = s.replace('    private TouchWebView web;\n', '    private WebView web;\n')
    s = s.replace('        web = new TouchWebView(this);\n', '        web = new WebView(this);\n')
for token in ['import android.os.Handler;\n','import android.os.Looper;\n','import android.view.ViewConfiguration;\n']:
    s=s.replace(token,'')
p.write_text(s, encoding='utf-8')

# V4 exact crop. В исходной игре .scene имеет background-size/position: ... !important,
# поэтому обычные inline-свойства V4 проигрывают. Заменяем setScene целиком regex-ом.
for p in [Path('NEW_DARK_RPG/art-atlas-v4.js'), Path('android/app/src/main/assets/art-atlas-v4.js')]:
    s = p.read_text(encoding='utf-8')
    pattern = r"function setScene\(id,key\)\{.*?\}\nfunction roomKeyV4"
    replacement = """function setScene(id,key){
const s=document.querySelector('#'+id+' .scene');if(!s)return;
const i=idx[key];if(i==null)return;
s.classList.add('art-v4-scene');
s.style.setProperty('background-image','url(\\\"'+SHEET+'\\\")','important');
s.style.setProperty('background-size','400% 600%','important');
s.style.setProperty('background-position',((i%4)*100/3)+'% '+(Math.floor(i/4)*100/5)+'%','important');
s.style.setProperty('background-repeat','no-repeat','important');
}
function roomKeyV4"""
    s2,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
    if n != 1:
        raise SystemExit(f'{p}: setScene function not found for robust replacement')
    s=s2
    if 'art-v4-scene:before' not in s:
        marker="const names=['shadow'"
        style="const V4_STYLE=document.createElement('style');V4_STYLE.textContent='.scene.art-v4-scene:before,.scene.art-v4-scene:after{display:none!important}.scene.art-v4-scene{background-repeat:no-repeat!important;}';document.head.appendChild(V4_STYLE);"
        if marker not in s: raise SystemExit(f'{p}: atlas name table missing')
        s=s.replace(marker,style+marker,1)
    # Точное отображение клетки существа без cover, который растягивал весь атлас.
    s=s.replace("e.style.backgroundSize='400% 600%';", "e.style.setProperty('background-size','400% 600%','important');e.style.setProperty('background-position',((idx[k]%4)*100/3)+'% '+(Math.floor(idx[k]/4)*100/5)+'%','important');")
    p.write_text(s,encoding='utf-8')

# Улучшаем разрешение V4-атласа перед упаковкой APK.
# Старый V4 содержит 256x384 (64x64 на клетку); увеличиваем до 1024x1536
# и применяем умеренное повышение резкости. Композиция и сами изображения не меняются.
try:
    from PIL import Image, ImageFilter, ImageEnhance
except ImportError:
    subprocess.run([sys.executable,'-m','pip','install','--user','--break-system-packages','Pillow','-q'],check=True)
    from PIL import Image, ImageFilter, ImageEnhance

for p in [Path('NEW_DARK_RPG/art-atlas-v4.js'), Path('android/app/src/main/assets/art-atlas-v4.js')]:
    s=p.read_text(encoding='utf-8')
    m=re.search(r"data:image/webp;base64,([^']+)'",s)
    if not m:
        raise SystemExit(f'{p}: V4 WebP not found')
    im=Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGB')
    if im.width < 1024 or im.height < 1536:
        im=im.resize((1024,1536),Image.Resampling.LANCZOS)
        im=ImageEnhance.Contrast(im).enhance(1.025)
        im=im.filter(ImageFilter.UnsharpMask(radius=1.15,percent=115,threshold=3))
    out=io.BytesIO();im.save(out,'WEBP',quality=92,method=6)
    b64=base64.b64encode(out.getvalue()).decode('ascii')
    s=s[:m.start(1)]+b64+s[m.end(1):]
    p.write_text(s,encoding='utf-8')
    print(f'V4 atlas improved: {p} -> {im.width}x{im.height}, {len(out.getvalue())} bytes')

# Новая версия только для этой исправленной визуальной сборки.
p=Path('android/app/build.gradle')
s=p.read_text(encoding='utf-8')
s=re.sub(r'versionCode\s+\d+','versionCode 41',s,count=1)
s=re.sub(r"versionName\s+'[^']+'","versionName '4.3.0'",s,count=1)
p.write_text(s,encoding='utf-8')

ma=Path('android/app/src/main/java/com/chronicles/abyss/MainActivity.java').read_text(encoding='utf-8')
if any(x in ma for x in ['dispatchTouchFallback','setOnTouchListener','MotionEvent','ANDROID-NATIVE-TOUCH-FALLBACK-V60']):
    raise SystemExit('MainActivity native duplicate touch fallback still present')
for p in [Path('NEW_DARK_RPG/art-atlas-v4.js'),Path('android/app/src/main/assets/art-atlas-v4.js')]:
    s=p.read_text(encoding='utf-8')
    if "setProperty('background-size','400% 600%','important')" not in s:
        raise SystemExit(f'{p}: V4 important tile sizing missing')
    if "setProperty('background-position'" not in s:
        raise SystemExit(f'{p}: V4 exact position missing')
    if 'art-v4-scene:before' not in s:
        raise SystemExit(f'{p}: V4 legacy overlay suppression missing')

print('V4 HIGH-RES + EXACT CREATURE CROP + SCROLL-SAFE TOUCH: PASS')
