// Chronicles of the Abyss V5 — boss phases and combat resolution
export function bossPhase(combat) {
  const meta=combat.enemyMeta;
  if (!meta?.boss) return null;
  const ratio=combat.enemy.hp / Math.max(1,combat.enemy.maxHp);
  const phase=ratio<=0.33?3:ratio<=0.66?2:1;
  if (phase!==combat.bossPhase) {
    combat.bossPhase=phase;
    if (phase===2) {
      combat.enemy.power+=Math.ceil(combat.enemy.power*0.15);
      combat.log.push("Босс входит во вторую фазу.");
    }
    if (phase===3) {
      combat.enemy.power+=Math.ceil(combat.enemy.power*0.2);
      combat.enemy.speed+=2;
      combat.log.push("Босс раскрывает последнюю фазу.");
    }
  }
  return phase;
}

export function resolveCombat(game) {
  const combat=game.combat;
  if (!combat) return {ok:false,reason:"no_combat"};
  bossPhase(combat);
  if (combat.phase==="victory") {
    game.combat=null;
    return {ok:true,victory:true,enemyId:combat.enemyId,criticals:combat.criticals};
  }
  if (combat.phase==="defeat") {
    game.combat=null;
    return {ok:true,victory:false,enemyId:combat.enemyId};
  }
  return {ok:true,victory:null};
}
