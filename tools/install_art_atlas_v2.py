from pathlib import Path

runtime=Path('NEW_DARK_RPG/art-atlas-v3.js').read_text(encoding='utf-8')
css='''<style id="art-atlas-v3-css">.atlas-creature{display:block;width:170px;height:170px;background-repeat:no-repeat;background-size:400% 600%;border:1px solid #671515;box-shadow:0 0 25px rgba(220,0,0,.32);border-radius:4px}.scene{background-size:cover!important;background-position:center!important}.scene .art-atlas-label{position:absolute;left:10px;bottom:8px;z-index:4;background:rgba(0,0,0,.55);padding:3px 6px;border-radius:3px;font:12px Georgia;color:#eee;text-shadow:0 2px 5px #000}</style>'''
Path('android/app/src/main/assets/art-atlas-v3.js').write_text(runtime,encoding='utf-8')
for name in ['NEW_DARK_RPG/index.html','android/app/src/main/assets/index.html']:
    p=Path(name); s=p.read_text(encoding='utf-8')
    # Удаляем только старое подключение атласа, если оно уже было установлено предыдущим запуском.
    s=s.replace('<script src="art-atlas-v2.js"></script>','').replace('<script src="art-atlas-v3.js"></script>','')
    s=s.replace('id="art-atlas-v2-css"','id="art-atlas-v3-css"')
    s=s.replace('</body>',css+'\n<script src="art-atlas-v3.js"></script>\n</body>')
    p.write_text(s,encoding='utf-8')
print('ART-ATLAS-V3 installed after game scripts')
