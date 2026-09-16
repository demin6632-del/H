from pathlib import Path

HTML_FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
ABYSS_OLD='<div class="info-card" id="abyssRoomInfo" style="margin-top:7px;line-height:1.55">Комната 1/5<br><span class="muted">Новая комната ещё не исследована.</span></div><button id="exploreBtn" onclick="explore()">Войти в комнату</button>'
ABYSS_NEW='<div class="info-card" id="abyssRoomInfo" style="margin-top:7px;line-height:1.55">Комната 1/5<br><span class="muted">Новая комната ещё не исследована.</span></div><div class="info-card" id="depthSelectPanel" style="margin-top:7px"><div class="info-row"><span>Открытая глубина</span><b id="bestDepthValue">1</b></div><select id="depthSelect" style="width:100%;min-height:40px;margin:5px 0;background:#080808;color:#eee;border:1px solid #6b1717;border-radius:4px;padding:7px"></select><button onclick="selectAbyssDepth()">Перейти на глубину</button></div><button id="exploreBtn" onclick="explore()">Войти в комнату</button><button id="abyssKeyBtn" onclick="openAbyssKeyCache()" style="display:none">🔑 Открыть запечатанный тайник</button>'
CARD_REPL={'<div class="hero-equip-card empty"><div class="gear-icon">🪖</div><b>Голова</b><small>+1 Защиты</small><button disabled>Надеть</button></div>':'<div class="hero-equip-card empty" id="heroHeadCard"></div>','<div class="hero-equip-card empty"><div class="gear-icon">💍</div><b>Кольцо</b><small>—</small><button disabled>Надеть</button></div>':'<div class="hero-equip-card empty" id="heroRingCard"></div>','<div class="hero-equip-card empty"><div class="gear-icon">👢</div><b>Обувь</b><small>—</small><button disabled>Надеть</button></div>':'<div class="hero-equip-card empty" id="heroBootsCard"></div>','<div class="hero-equip-card empty"><div class="gear-icon">🧥</div><b>Плащ</b><small>+1 Защиты</small><button disabled>Надеть</button></div>':'<div class="hero-equip-card empty" id="heroCloakCard"></div>','<div class="hero-equip-card empty"><div class="gear-icon">🔮</div><b>Амулет</b><small>—</small><button disabled>Надеть</button></div>':'<div class="hero-equip-card empty" id="heroAmuletCard"></div>','<div class="hero-equip-card empty"><div class="gear-icon">🛡️</div><b>Щит</b><small>—</small><button disabled>Надеть</button></div>':'<div class="hero-equip-card empty" id="heroShieldCard"></div>'}
for path in HTML_FILES:
    s=path.read_text(encoding='utf-8')
    if 'RELEASE-V3.8' in s: continue
    if ABYSS_OLD not in s: raise SystemExit(f'{path}: abyss UI anchor missing')
    s=s.replace(ABYSS_OLD,ABYSS_NEW,1)
    for a,b in CARD_REPL.items(): s=s.replace(a,b,1)
    js=Path('tools/release_v38_override.js').read_text(encoding='utf-8')
    s=s.replace('</script></div>','\n'+js+'\n</script></div>',1)
    path.write_text(s,encoding='utf-8')
print('RELEASE_V38_PATCH_OK')
