from pathlib import Path
import subprocess

# V56 — окончательная точка применения Android touch-патча.
# Этот файл вызывается существующим build-apk.yml, поэтому отдельного ручного шага не требуется.
patch = Path('tools/fix_android_touch_v56.py')
if not patch.exists():
    raise SystemExit('tools/fix_android_touch_v56.py is missing')
subprocess.run(['python', str(patch)], check=True)
print('ANDROID TOUCH V56 APPLIED')
