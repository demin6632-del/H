from pathlib import Path

# V4 experimental overlay is intentionally disabled.
# The Android button issue is fixed at its root in fix_android_touch_v41.py.
for name in ['NEW_DARK_RPG/index.html','android/app/src/main/assets/index.html']:
    p=Path(name)
    if p.exists():
        s=p.read_text(encoding='utf-8')
        # Не добавляем новый обработчик, чтобы не дублировать штатные click/touch события.
        p.write_text(s,encoding='utf-8')
print('ANDROID-TOUCH-FIX-V4-DISABLED')
