from pathlib import Path

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]

# Переводим существующую Бездну из конечной модели в постоянное продолжение после 7-го этажа.
for path in FILES:
    s=path.read_text(encoding='utf-8')
    original=s

    # После 7-го этажа кнопка всегда открывает следующий этаж, а не завершает игру.
    old="if(abyssRoom>=ROOMS_PER_FLOOR){if(abyssFloor<MAX_FLOOR){abyssFloor++;abyssRoom=0;save();updateAbyss();logEvent('ЭТАЖ','Открыт этаж '+abyssFloor+'.');if(el('out'))el('out').innerHTML='<span class=\"green\">Этаж '+abyssFloor+' открыт.</span>';return}"
    new="if(abyssRoom>=ROOMS_PER_FLOOR){abyssFloor++;abyssRoom=0;save();updateAbyss();logEvent('ЭТАЖ',abyssFloor<=MAX_FLOOR?'Открыт этаж '+abyssFloor+'.':'Открыта новая глубина Бездны: '+abyssFloor+'.');if(el('out'))el('out').innerHTML='<span class=\"green\">'+(abyssFloor<=MAX_FLOOR?'Этаж '+abyssFloor+' открыт.':'Глубина '+abyssFloor+' открыта.')+'</span>';return}"
    if old not in s:
        raise SystemExit(f'{path}: finite floor transition not found')
    s=s.replace(old,new,1)

    # После завершения 7-го этажа больше не возвращаемся в город автоматически.
    old="abyssBossDefeated=true;save();logEvent('БЕЗДНА','Вершина Бездны достигнута.');if(el('out'))el('out').innerHTML='<span class=\"gold\">Ты достиг вершины Бездны.</span>';screenHistory=['menu','main'];history.replaceState({screen:'main'},'','#main');setScreen('main',false);return"
    new="abyssBossDefeated=true;save();logEvent('БЕЗДНА','Предела Бездны нет. Начинается следующая глубина.');if(el('out'))el('out').innerHTML='<span class=\"gold\">🌑 Глубина продолжается. Открыт этаж '+abyssFloor+'.</span>';return"
    if old not in s:
        raise SystemExit(f'{path}: finite Abyss ending not found')
    s=s.replace(old,new,1)

    # Убираем сброс глубины после смерти. Персонаж возвращается в город, но достигнутая глубина сохраняется.
    old="logEvent('СМЕРТЬ','Герой пал на этаже '+abyssFloor+', комната '+Math.min(ROOMS_PER_FLOOR,abyssRoom+1)+'. Забег завершён.');resetAbyss();hero.hp=hero.maxHp;hero.energy=hero.maxEnergy;save();"
    new="logEvent('СМЕРТЬ','Герой пал на глубине '+abyssFloor+', комнате '+Math.min(ROOMS_PER_FLOOR,abyssRoom+1)+'. Глубина сохранена.');abyssRoom=0;abyssBossDefeated=false;hero.hp=hero.maxHp;hero.energy=hero.maxEnergy;save();"
    if old not in s:
        raise SystemExit(f'{path}: death reset block not found')
    s=s.replace(old,new,1)

    # Текст индикатора больше не показывает 1/7 как конечный предел.
    old="if(el('abyssFloor'))el('abyssFloor').textContent=abyssFloor+'/'+MAX_FLOOR;"
    new="if(el('abyssFloor'))el('abyssFloor').textContent=abyssFloor+(abyssFloor>=8?' · Глубины':'/'+MAX_FLOOR);"
    if old not in s:
        raise SystemExit(f'{path}: abyss floor display not found')
    s=s.replace(old,new,1)

    # На последующих глубинах кнопка не превращается в «Завершить Бездну».
    old="el('exploreBtn').textContent=abyssRoom>=ROOMS_PER_FLOOR?(abyssFloor<MAX_FLOOR?'Следующий этаж':'Завершить Бездну'):'Войти в комнату'"
    new="el('exploreBtn').textContent=abyssRoom>=ROOMS_PER_FLOOR?'Следующая глубина':'Войти в комнату'"
    if old not in s:
        raise SystemExit(f'{path}: explore button text not found')
    s=s.replace(old,new,1)

    # Нормализуем старые сохранения: сохранённая глубина >=8 должна продолжаться, а не закрываться.
    marker="const INFINITE_PERSISTENCE_FIX_V2='"
    if marker not in s:
        s=s.replace('</script>',"const INFINITE_PERSISTENCE_FIX_V2='persistent-infinite-abyss';\n</script>",1)

    if s==original:
        raise SystemExit(f'{path}: no changes made')
    path.write_text(s,encoding='utf-8')
    print(f'Updated {path}')
