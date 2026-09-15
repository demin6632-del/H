from pathlib import Path
import base64,zlib
parts=[Path(f'tools/v3_chunk{i}.txt').read_text(encoding='utf-8').strip() for i in range(1,5)]
raw=base64.b64decode(''.join(parts))
html=zlib.decompress(raw).decode('utf-8')
for p in [Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]: p.write_text(html,encoding='utf-8')
print('Applied exact canonical v3 game:',len(html),'bytes')
