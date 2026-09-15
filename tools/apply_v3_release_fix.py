from pathlib import Path
import ast,base64,zlib
src=Path('tools/apply_v3_release.py').read_text(encoding='utf-8')
chunk4=Path('tools/v3_chunk4.txt').read_text(encoding='utf-8').strip()
tree=ast.parse(src)
vals={}
for node in tree.body:
    if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in {'CHUNK1','CHUNK2','CHUNK3'}:
        vals[node.targets[0].id]=ast.literal_eval(node.value)
if set(vals)!={'CHUNK1','CHUNK2','CHUNK3'}: raise SystemExit('v3 payload chunks 1-3 missing')
html=zlib.decompress(base64.b64decode(vals['CHUNK1']+vals['CHUNK2']+vals['CHUNK3']+chunk4)).decode('utf-8')
for p in [Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]: p.write_text(html,encoding='utf-8')
print('Applied canonical v3:',len(html),'bytes')
