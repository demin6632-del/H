from pathlib import Path

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]

# Финальная версия: после 7-го этажа исследование Бездны продолжается бесконечно.
for path in FILES:
    s=path.read_text(encoding='utf-8')
    original=s

    # После завершения пяти комнат всегда открываем следующий этаж/глубину.
    old="if(abyssRoom>=ROOMS_PER_FLOOR){if(abyssFloor<MAX_FLOOR){abyssFloor++;abyssRoom=0;save();updateAbyss();logEvent('ЭТАЖ','Открыт этаж '+abyssFloor+'.');if(el('out'))el('out').innerHTML='<span class=\"green\">Этаж '+abyssFloor+' открыт.</span>';return}"
    new="if(abyssRoom>=ROOMS_PER_FLOOR){abyssFloor++;abyssRoom=0;save();updateAbyss();logEvent('ЭТАЖ',abyssFloor<=MAX_FLOOR?'Открыт этаж '+abyssFloor+'.':'Открыта новая глубина Бездны: '+abyssFloor+'.');if(el('out'))el('out').innerHTML='<span class=\"green\">'+(abyssFloor<=MAX_FLOOR?'Этаж '+abyssFloor+' открыт.':'Глубина '+abyssFloor+' открыта.')+'</span>';return}"
    if old not in s: raise SystemExit(f'{path}: finite floor transition not found')
    s=s.replace(old,new,1)

    # Удаляем старое завершение Бездны, которое находилось внутри перехода последнего этажа.
    old="abyssBossDefeated=true;save();logEvent('БЕЗДНА','Вершина Бездны достигнута.');if(el('out'))el('out').innerHTML='<span class=\"gold\">Ты достиг вершины Бездны.</span>';screenHistory=['menu','main'];history.replaceState({screen:'main'},'','#main');setScreen('main',false);return"
    if old not in s: raise SystemExit(f'{path}: finite Abyss ending not found')
    s=s.replace(old,'',1)

    # Смерть больше не сбрасывает глубину. После смерти герой возвращается в город с сохранённой глубиной.
    old="logEvent('СМЕРТЬ','Герой пал на этаже '+abyssFloor+', комната '+Math.min(ROOMS_PER_FLOOR,abyssRoom+1)+'. Забег завершён.');resetAbyss();hero.hp=hero.maxHp;hero.energy=hero.maxEnergy;save();"
    new="logEvent('СМЕРТЬ','Герой пал на глубине '+abyssFloor+', комнате '+Math.min(ROOMS_PER_FLOOR,abyssRoom+1)+'. Глубина сохранена.');abyssRoom=0;abyssBossDefeated=false;hero.hp=hero.maxHp;hero.energy=hero.maxEnergy;save();"
    if old not in s: raise SystemExit(f'{path}: death reset block not found')
    s=s.replace(old,new,1)

    # После 7-го этажа индикатор показывает бесконечные Глубины.
    old="if(el('abyssFloor'))el('abyssFloor').textContent=abyssFloor+'/'+MAX_FLOOR;"
    new="if(el('abyssFloor'))el('abyssFloor').textContent=abyssFloor+(abyssFloor>=8?' · Глубины':'/'+MAX_FLOOR);"
    if old not in s: raise SystemExit(f'{path}: abyss floor display not found')
    s=s.replace(old,new,1)

    # Кнопка после пятой комнаты всегда ведёт дальше.
    old="el('exploreBtn').textContent=abyssRoom>=ROOMS_PER_FLOOR?(abyssFloor<MAX_FLOOR?'Следующий этаж':'Завершить Бездну'):'Войти в комнату'"
    new="el('exploreBtn').textContent=abyssRoom>=ROOMS_PER_FLOOR?'Следующая глубина':'Войти в комнату'"
    if old not in s: raise SystemExit(f'{path}: explore button text not found')
    s=s.replace(old,new,1)

    marker="const INFINITE_PERSISTENCE_FIX_V2='"
    if marker not in s:
        s=s.replace('</script>',"const INFINITE_PERSISTENCE_FIX_V2='persistent-infinite-abyss';\n</script>",1)

    if s==original: raise SystemExit(f'{path}: no changes made')
    path.write_text(s,encoding='utf-8')
    print(f'Updated {path}')
