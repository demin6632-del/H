// Chronicles of the Abyss V5 — combat status effects
export const STATUS = Object.freeze({
  poison:"poison", burn:"burn", bleed:"bleed", stun:"stun", slow:"slow", regen:"regen", fortify:"fortify", berserk:"berserk"
});

export function addStatus(actor, id, turns = 1, power = 1) {
  if (!actor.statuses) actor.statuses = {};
  actor.statuses[id] = { turns:Math.max(1, Math.trunc(turns)), power:Math.max(1, Math.trunc(power)) };
  return actor;
}

export function hasStatus(actor, id) {
  return !!actor.statuses?.[id];
}

export function tickStatuses(actor) {
  if (!actor.statuses) actor.statuses = {};
  const effects = [];
  for (const [id, effect] of Object.entries(actor.statuses)) {
    if (id === STATUS.poison || id === STATUS.burn || id === STATUS.bleed) {
      const damage = Math.max(1, effect.power);
      actor.hp = Math.max(0, actor.hp - damage);
      effects.push({ id, type:"damage", value:damage });
    } else if (id === STATUS.regen) {
      const heal = Math.max(1, effect.power);
      actor.hp = Math.min(actor.maxHp, actor.hp + heal);
      effects.push({ id, type:"heal", value:heal });
    }
    effect.turns -= 1;
    if (effect.turns <= 0) delete actor.statuses[id];
  }
  return effects;
}

export function modifyDamage(actor, damage) {
  let value = Math.max(0, Math.trunc(damage));
  if (hasStatus(actor, STATUS.fortify)) value = Math.max(1, Math.floor(value * 0.7));
  if (hasStatus(actor, STATUS.berserk)) value = Math.max(1, Math.floor(value * 1.15));
  return value;
}
