// Chronicles of the Abyss V5 — death and run lifecycle
import { createInitialState } from "./state.js";
import { clearRun } from "./run-persistence.js";

export function finishDeath(game) {
  const state=game.state;
  state.meta.deaths=(state.meta.deaths||0)+1;
  state.meta.bestDepth=Math.max(state.meta.bestDepth||1,state.abyss.depth||1);
  state.abyss.active=false;
  state.abyss.room=0;
  state.abyss.pending=null;
  state.abyss.morale=100;
  state.abyss.risk=0;
  state.abyss.awareness=50;
  state.abyss.tempo=50;
  state.abyss.returnRewards=null;
  game.combat=null;
  clearRun();
  return {dead:true,depth:state.abyss.depth,deaths:state.meta.deaths};
}

export function newGame(game) {
  game.state=createInitialState();
  game.combat=null;
  clearRun();
  return game;
}
