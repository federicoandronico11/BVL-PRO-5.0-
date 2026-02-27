"""
mbt_rivals.py — MBT RIVALS: Sistema Carte, Collezione, Negozio, Battaglia v2.0
Fix: Errori CSS carte, Collezione da Negozio + Atleti reali, Squadra attiva migliorata.
"""
import streamlit as st
import json
import random
import time
import base64
import os
from pathlib import Path
from datetime import datetime

# ─── FILE PERSISTENZA ────────────────────────────────────────────────────────
RIVALS_FILE = "mbt_rivals_data.json"
CARDS_DB_FILE = "mbt_cards_db.json"
ASSETS_ICONS_DIR = "assets/icons"


# ─── CSS ANIMATIONS & STYLES ─────────────────────────────────────────────────

RIVALS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Orbitron:wght@400;700;900&family=Exo+2:ital,wght@0,300;0,700;0,900;1,700&display=swap');

:root {
  --rivals-bg: #080810;
  --rivals-card: #10101e;
  --rivals-border: #1e1e3a;
  --rivals-gold: #ffd700;
  --rivals-purple: #9b59b6;
  --rivals-blue: #1e3a8a;
  --rivals-red: #dc2626;
  --rivals-green: #16a34a;
  --rivals-cyan: #00f5ff;
}

@keyframes goldShine {
  0%{background-position:200% center}
  100%{background-position:-200% center}
}
@keyframes pulseGlow {
  0%,100%{box-shadow:0 0 10px currentColor}
  50%{box-shadow:0 0 30px currentColor,0 0 60px currentColor}
}
@keyframes shimmer {
  0%{left:-100%}100%{left:200%}
}
@keyframes holographic {
  0%{background-position:0% 50%}
  50%{background-position:100% 50%}
  100%{background-position:0% 50%}
}
@keyframes iconGodPulse {
  0%,100%{box-shadow:0 0 20px #ff2200,0 0 40px #880000,inset 0 0 20px rgba(255,0,0,0.3)}
  50%{box-shadow:0 0 40px #ff4400,0 0 80px #ff0000,inset 0 0 40px rgba(255,80,0,0.5)}
}
@keyframes lightningFlash {
  0%,90%,100%{opacity:0}
  92%,96%{opacity:1}
  94%,98%{opacity:.3}
}
@keyframes nebulaSwirl {
  0%{transform:rotate(0deg) scale(1)}
  50%{transform:rotate(180deg) scale(1.1)}
  100%{transform:rotate(360deg) scale(1)}
}
@keyframes cardFlip {
  0%{transform:rotateY(0deg) scale(0.8);opacity:0}
  40%{transform:rotateY(90deg) scale(1.1)}
  100%{transform:rotateY(0deg) scale(1);opacity:1}
}
@keyframes goldPulse {
  0%,100%{box-shadow:0 0 15px rgba(255,215,0,0.5)}
  50%{box-shadow:0 0 35px rgba(255,215,0,0.9),0 0 60px rgba(255,215,0,0.4)}
}

/* ─── Card Base ─── */
.mbt-card-wrap {
  position:relative;
  display:inline-block;
  cursor:pointer;
  transition:transform 0.3s;
  vertical-align:top;
}
.mbt-card-wrap:hover {
  transform:translateY(-6px) scale(1.03);
  z-index:10;
}
.mbt-card {
  border-radius:12px;
  position:relative;
  overflow:hidden;
  font-family:'Orbitron','Rajdhani',sans-serif;
  user-select:none;
  display:block;
}

/* Bronzo */
.mbt-card.bronzo {
  background:linear-gradient(160deg,#3d2b1f 0%,#6b4226 50%,#3d2b1f 100%);
  border:2px solid #cd7f32;
  box-shadow:0 4px 15px rgba(205,127,50,0.3);
}
/* Argento */
.mbt-card.argento {
  background:linear-gradient(160deg,#2a2a2a 0%,#555 50%,#2a2a2a 100%);
  border:2px solid #c0c0c0;
  box-shadow:0 4px 20px rgba(192,192,192,0.4);
}
/* Oro */
.mbt-card.oro {
  background:linear-gradient(160deg,#2a1f00 0%,#5a4200 50%,#2a1f00 100%);
  border:2px solid #ffd700;
  box-shadow:0 6px 25px rgba(255,215,0,0.5);
}
.mbt-card.oro::after {
  content:'';position:absolute;top:0;left:-100%;width:60%;height:100%;
  background:linear-gradient(90deg,transparent,rgba(255,215,0,0.3),transparent);
  animation:shimmer 2.5s infinite;pointer-events:none;
}
/* Eroe */
.mbt-card.eroe {
  background:linear-gradient(160deg,#1a0033 0%,#4a0080 50%,#1a0033 100%);
  border:2px solid #9b59b6;
  box-shadow:0 6px 30px rgba(155,89,182,0.6);
}
/* Leggenda */
.mbt-card.leggenda {
  background:linear-gradient(160deg,#1a1a1a 0%,#3a3a3a 50%,#1a1a1a 100%);
  border:2px solid #ffffff;
  box-shadow:0 8px 40px rgba(255,255,255,0.4);
}
/* TOTY */
.mbt-card.toty {
  background:linear-gradient(160deg,#000820 0%,#001855 50%,#000820 100%);
  border:3px solid #4169e1;
  box-shadow:0 8px 40px rgba(65,105,225,0.7);
}
/* ICON BASE */
.mbt-card.icon-base {
  background:linear-gradient(160deg,#1a0f00 0%,#3d2800 50%,#1a0f00 100%);
  border:3px solid #ffd700;
  box-shadow:0 10px 50px rgba(255,215,0,0.8);
}
/* ICON EPICA */
.mbt-card.icon-epica {
  background:linear-gradient(160deg,#1a0030 0%,#4a0090 50%,#1a0030 100%);
  border:3px solid #cc44ff;
  box-shadow:0 10px 60px rgba(180,0,255,0.9);
}
/* ICON LEGGENDARIA */
.mbt-card.icon-leggendaria {
  background:linear-gradient(160deg,#111 0%,#2a2a2a 50%,#111 100%);
  border:3px solid #ffffff;
  box-shadow:0 12px 70px rgba(255,255,255,0.9);
}
/* ICON TOTY */
.mbt-card.icon-toty {
  background:linear-gradient(160deg,#000820 0%,#001060 50%,#000820 100%);
  border:4px solid #4169e1;
  box-shadow:0 15px 80px rgba(65,105,225,1);
}
/* ICON GOD */
.mbt-card.icon-god {
  background:linear-gradient(160deg,#0a0000 0%,#2a0000 30%,#000000 70%,#0a0000 100%);
  border:4px solid #ff2200;
  box-shadow:0 0 20px #ff2200,0 0 40px #880000;
  animation:iconGodPulse 1.5s infinite;
}

/* ─── Card Inner Elements ─── */
.mbt-card-header {
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  padding:6px 8px 2px;
  position:relative;
  z-index:2;
}
.mbt-card-ovr {
  font-family:'Orbitron',sans-serif;
  font-weight:900;
  line-height:1;
}
.mbt-card-tier-label {
  font-size:0.42rem;
  letter-spacing:1.5px;
  font-weight:700;
  opacity:0.85;
  text-transform:uppercase;
  text-align:right;
  max-width:60px;
  line-height:1.2;
}
.mbt-card-photo {
  width:100%;
  height:85px;
  object-fit:cover;
  object-position:top center;
  display:block;
  position:relative;
  z-index:1;
}
.mbt-card-photo-placeholder {
  width:100%;
  height:85px;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:2rem;
  background:rgba(0,0,0,0.35);
  position:relative;
  z-index:1;
}
.mbt-card-name {
  font-family:'Orbitron',sans-serif;
  font-size:0.55rem;
  font-weight:700;
  text-align:center;
  letter-spacing:0.8px;
  padding:3px 6px 1px;
  text-transform:uppercase;
  position:relative;
  z-index:2;
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}
.mbt-card-role {
  font-size:0.42rem;
  text-align:center;
  opacity:0.75;
  letter-spacing:1px;
  text-transform:uppercase;
  margin-bottom:3px;
  padding:0 4px;
  position:relative;
  z-index:2;
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}
.mbt-card-divider {
  height:1px;
  background:rgba(255,255,255,0.1);
  margin:0 8px 3px;
}
.mbt-card-stats {
  display:grid;
  grid-template-columns:1fr 1fr 1fr;
  gap:2px;
  padding:2px 6px 6px;
  position:relative;
  z-index:2;
}
.mbt-stat {
  text-align:center;
}
.mbt-stat-val {
  font-family:'Orbitron',sans-serif;
  font-size:0.68rem;
  font-weight:900;
  line-height:1;
}
.mbt-stat-lbl {
  font-size:0.34rem;
  letter-spacing:0.8px;
  text-transform:uppercase;
  opacity:0.65;
  margin-top:1px;
}

/* Large card sizes */
.mbt-card.size-large .mbt-card-photo,
.mbt-card.size-large .mbt-card-photo-placeholder {
  height:120px;
}
.mbt-card.size-large .mbt-card-name { font-size:0.7rem; }
.mbt-card.size-large .mbt-card-ovr { font-size:1.6rem !important; }
.mbt-card.size-large .mbt-stat-val { font-size:0.85rem; }

/* Small card sizes */
.mbt-card.size-small .mbt-card-photo,
.mbt-card.size-small .mbt-card-photo-placeholder {
  height:70px;
}
.mbt-card.size-small .mbt-card-name { font-size:0.48rem; }
.mbt-card.size-small .mbt-card-ovr { font-size:1rem !important; }

/* ─── Collezione / Team ─── */
.card-slot-wrapper {
  position:relative;
  display:inline-block;
  width:100%;
}
.card-active-badge {
  position:absolute;
  top:-6px;right:-6px;
  background:#16a34a;
  color:#fff;
  border-radius:50%;
  width:20px;height:20px;
  display:flex;align-items:center;justify-content:center;
  font-size:0.6rem;font-weight:900;
  z-index:20;border:2px solid #080810;
}
.card-source-badge {
  position:absolute;
  bottom:4px;left:4px;
  background:rgba(0,0,0,0.75);
  color:#ffd700;
  border-radius:4px;
  padding:1px 4px;
  font-size:0.38rem;
  letter-spacing:1px;
  z-index:20;
  text-transform:uppercase;
}

/* ─── Pack ─── */
.pack-card-visual {
  border-radius:14px;
  width:100%;
  padding:24px 16px;
  text-align:center;
  position:relative;
  overflow:hidden;
  cursor:pointer;
  transition:transform 0.3s, box-shadow 0.3s;
}
.pack-card-visual:hover {
  transform:translateY(-6px) scale(1.02);
}
.pack-base-bg {
  background:linear-gradient(160deg,#2a1f0f 0%,#5a3a0f 50%,#2a1f0f 100%);
  border:2px solid #cd7f32;
  box-shadow:0 8px 30px rgba(205,127,50,0.5);
}
.pack-epico-bg {
  background:linear-gradient(160deg,#1a0035 0%,#4a0080 50%,#1a0035 100%);
  border:2px solid #9b59b6;
  box-shadow:0 8px 40px rgba(155,89,182,0.7);
}
.pack-leggenda-bg {
  background:linear-gradient(160deg,#0a0000 0%,#2a0000 50%,#0a0000 100%);
  border:3px solid #ff6600;
  box-shadow:0 10px 60px rgba(255,102,0,0.8);
}

/* ─── HP Bars ─── */
.hp-bar-container {
  height:16px;background:#1a1a2a;border-radius:8px;overflow:hidden;
  border:1px solid #1e1e3a;
}
.hp-bar-fill {
  height:100%;border-radius:8px;transition:width 0.5s ease;
  background:linear-gradient(90deg,#16a34a,#4ade80);
}
.hp-bar-fill.danger {
  background:linear-gradient(90deg,#dc2626,#ef4444);
}

/* ─── Arena Badges ─── */
.arena-badge {
  border-radius:10px;padding:14px;text-align:center;
  transition:transform 0.2s;
}
.arena-badge:hover { transform:translateY(-3px); }
.arena-base     { background:linear-gradient(135deg,#2a1f0f,#5a3a0f);border:2px solid #cd7f32; }
.arena-epica    { background:linear-gradient(135deg,#1a003a,#4a0080);border:2px solid #9b59b6; }
.arena-leggendaria { background:linear-gradient(135deg,#0a0a0a,#2a2a2a);border:2px solid #fff; }
.arena-toty     { background:linear-gradient(135deg,#000820,#001855);border:2px solid #4169e1; }
.arena-icona    { background:linear-gradient(135deg,#1a0f00,#3d2800);border:3px solid #ffd700; }
.arena-icona-epica { background:linear-gradient(135deg,#1a0030,#4a0090);border:3px solid #cc44ff; }
.arena-icona-leggendaria { background:linear-gradient(135deg,#111,#2a2a2a);border:3px solid #fff; }
.arena-toty-plus { background:linear-gradient(135deg,#000820,#001060);border:4px solid #4169e1; }
.arena-god      { background:linear-gradient(135deg,#0a0000,#2a0000);border:4px solid #ff2200; }
.arena-omega    { background:linear-gradient(135deg,#000,#0a001a);border:4px solid #cc00ff;
  box-shadow:0 0 40px rgba(180,0,255,0.5); }

/* ─── Battle log ─── */
.battle-log {
  background:#05050f;border:1px solid #1e1e3a;border-radius:8px;
  padding:10px;max-height:180px;overflow-y:auto;
  font-family:'Exo 2',sans-serif;font-size:0.72rem;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:#0a0a14; }
::-webkit-scrollbar-thumb { background:#2a2a4a;border-radius:2px; }
</style>
"""


# ─── DATA HELPERS ─────────────────────────────────────────────────────────────

def load_rivals_data():
    if Path(RIVALS_FILE).exists():
        with open(RIVALS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return empty_rivals_state()

def save_rivals_data(data):
    with open(RIVALS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_cards_db():
    if Path(CARDS_DB_FILE).exists():
        with open(CARDS_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"cards": [], "next_id": 1}

def save_cards_db(db):
    with open(CARDS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def empty_rivals_state():
    return {
        "player_level": 1,
        "player_xp": 0,
        "mbt_coins": 100_000_000,
        "trofei_rivals": 0,
        "collection": [],           # lista di instance_id o card_id possedute
        "collection_cards": [],     # lista completa delle carte possedute (oggetti)
        "active_team": [],          # max 5 instance_id
        "active_team_cards": [],    # carte complete del team attivo
        "arena_unlocked": 1,
        "battle_wins": 0,
        "battle_losses": 0,
        "special_moves_learned": [],
        "superpowers": {},
        "achievements": [],
    }


# ─── CONSTANTS ────────────────────────────────────────────────────────────────

ROLES = [
    "SPIKER", "IRONBLOCKER", "DIFENSORE", "ACER",
    "SPECIALISTA", "TRAINER - Fisioterapista",
    "TRAINER - Mental Coach", "TRAINER - Scoutman"
]
ROLE_ICONS = {
    "SPIKER": "⚡", "IRONBLOCKER": "🛡️", "DIFENSORE": "🤿",
    "ACER": "🎯", "SPECIALISTA": "🔮",
    "TRAINER - Fisioterapista": "💊", "TRAINER - Mental Coach": "🧠",
    "TRAINER - Scoutman": "🔭"
}

CARD_TIERS = {
    "Bronzo Comune":    {"ovr_range":(40,44), "css":"bronzo",           "color":"#cd7f32", "rarity":0},
    "Bronzo Raro":      {"ovr_range":(45,49), "css":"bronzo",           "color":"#e8902a", "rarity":1},
    "Argento Comune":   {"ovr_range":(50,54), "css":"argento",          "color":"#c0c0c0", "rarity":2},
    "Argento Raro":     {"ovr_range":(55,59), "css":"argento",          "color":"#d8d8d8", "rarity":3},
    "Oro Comune":       {"ovr_range":(60,64), "css":"oro",              "color":"#ffd700", "rarity":4},
    "Oro Raro":         {"ovr_range":(65,69), "css":"oro",              "color":"#ffec4a", "rarity":5},
    "Eroe":             {"ovr_range":(70,74), "css":"eroe",             "color":"#9b59b6", "rarity":6},
    "IF (In Form)":     {"ovr_range":(75,79), "css":"eroe",             "color":"#b07dd0", "rarity":7},
    "Leggenda":         {"ovr_range":(80,84), "css":"leggenda",         "color":"#ffffff", "rarity":8},
    "TOTY":             {"ovr_range":(85,89), "css":"toty",             "color":"#4169e1", "rarity":9},
    "TOTY Evoluto":     {"ovr_range":(90,94), "css":"toty",             "color":"#6a8fff", "rarity":10},
    "GOAT":             {"ovr_range":(95,99), "css":"eroe",             "color":"#ff4400", "rarity":11},
    "ICON BASE":        {"ovr_range":(100,104),"css":"icon-base",       "color":"#ffd700", "rarity":12},
    "ICON EPICA":       {"ovr_range":(105,109),"css":"icon-epica",      "color":"#cc44ff", "rarity":13},
    "ICON LEGGENDARIA": {"ovr_range":(110,114),"css":"icon-leggendaria","color":"#ffffff", "rarity":14},
    "ICON TOTY":        {"ovr_range":(115,119),"css":"icon-toty",       "color":"#4169e1", "rarity":15},
    "ICON GOD":         {"ovr_range":(120,125),"css":"icon-god",        "color":"#ff2200", "rarity":16},
}

def get_tier_by_ovr(ovr):
    for tier_name, td in CARD_TIERS.items():
        lo, hi = td["ovr_range"]
        if lo <= ovr <= hi:
            return tier_name
    if ovr >= 120: return "ICON GOD"
    if ovr >= 115: return "ICON TOTY"
    if ovr >= 110: return "ICON LEGGENDARIA"
    if ovr >= 105: return "ICON EPICA"
    if ovr >= 100: return "ICON BASE"
    return "GOAT" if ovr >= 95 else "TOTY Evoluto"


PACKS = {
    "Base": {
        "price": 200,
        "emoji": "🟫",
        "css": "pack-base-bg",
        "label_color": "#cd7f32",
        "description": "6 carte | Comuni e Rare",
        "weights": {
            "Bronzo Comune":0.30,"Bronzo Raro":0.25,"Argento Comune":0.20,
            "Argento Raro":0.12,"Oro Comune":0.07,"Oro Raro":0.04,
            "Eroe":0.015,"IF (In Form)":0.005
        }
    },
    "Epico": {
        "price": 500,
        "emoji": "💜",
        "css": "pack-epico-bg",
        "label_color": "#9b59b6",
        "description": "6 carte | Da Oro a Leggenda",
        "weights": {
            "Oro Comune":0.25,"Oro Raro":0.22,"Eroe":0.18,
            "IF (In Form)":0.15,"Leggenda":0.08,"TOTY":0.04,
            "TOTY Evoluto":0.02,"GOAT":0.01,
            "ICON BASE":0.008,"ICON EPICA":0.002
        }
    },
    "Leggenda": {
        "price": 1200,
        "emoji": "🔥",
        "css": "pack-leggenda-bg",
        "label_color": "#ff6600",
        "description": "6 carte | Alta probabilità di Speciali",
        "weights": {
            "Leggenda":0.25,"TOTY":0.20,"TOTY Evoluto":0.18,
            "GOAT":0.12,"ICON BASE":0.10,"ICON EPICA":0.07,
            "ICON LEGGENDARIA":0.04,"ICON TOTY":0.02,"ICON GOD":0.01,
            "IF (In Form)":0.01
        }
    },
}

ARENE = [
    {"min_level":1,  "max_level":2,  "name":"Arena Base",           "css":"arena-base",             "color":"#cd7f32","icon":"🏟️"},
    {"min_level":3,  "max_level":4,  "name":"Arena Epica",          "css":"arena-epica",            "color":"#9b59b6","icon":"⚡"},
    {"min_level":5,  "max_level":6,  "name":"Arena Leggendaria",    "css":"arena-leggendaria",      "color":"#ffffff","icon":"👑"},
    {"min_level":7,  "max_level":8,  "name":"Arena TOTY",           "css":"arena-toty",             "color":"#4169e1","icon":"🌟"},
    {"min_level":9,  "max_level":10, "name":"Arena ICONA",          "css":"arena-icona",            "color":"#ffd700","icon":"🏆"},
    {"min_level":11, "max_level":12, "name":"Arena ICONA EPICA",    "css":"arena-icona-epica",      "color":"#cc44ff","icon":"💫"},
    {"min_level":13, "max_level":14, "name":"Arena ICONA LEGGEND.", "css":"arena-icona-leggendaria","color":"#ffffff","icon":"✨"},
    {"min_level":15, "max_level":16, "name":"Arena TOTY SUPREMA",   "css":"arena-toty-plus",        "color":"#4169e1","icon":"🔮"},
    {"min_level":17, "max_level":18, "name":"Arena GOD MODE",       "css":"arena-god",              "color":"#ff2200","icon":"🔥"},
    {"min_level":19, "max_level":20, "name":"Arena OMEGA",          "css":"arena-omega",            "color":"#ff00cc","icon":"⚜️"},
]

XP_PER_LEVEL = [0,100,250,450,700,1000,1350,1750,2200,2700,
                3250,3850,4500,5200,5950,6750,7600,8500,9450,10450]

SPECIAL_MOVES = [
    {"id":"nocchino_ghiaccio","name":"Nocchino di Ghiaccio","role":"SPIKER","cost_coins":300,"dmg":35,"desc":"Attacco che non fallisce mai"},
    {"id":"fortezza_titanio","name":"Fortezza di Titanio","role":"IRONBLOCKER","cost_coins":280,"dmg":0,"desc":"Annulla il prossimo attacco"},
    {"id":"muro_corna","name":"Muro Corna","role":"IRONBLOCKER","cost_coins":320,"dmg":20,"desc":"Danno e difesa simultanei"},
    {"id":"sky_dive","name":"Sky Dive","role":"DIFENSORE","cost_coins":250,"dmg":0,"desc":"Recupera 20 HP"},
    {"id":"sabbia_mobile","name":"Sabbia Mobile","role":"DIFENSORE","cost_coins":270,"dmg":0,"desc":"Recupera 30 HP"},
    {"id":"jump_float","name":"Jump Float Infuocato","role":"ACER","cost_coins":350,"dmg":40,"desc":"Danni critici doppi se primo turno"},
    {"id":"skyball","name":"SKYBALL","role":"ACER","cost_coins":400,"dmg":45,"desc":"Danno critico al morale avversario"},
    {"id":"seconda_intenzione","name":"Seconda Intenzione","role":"SPECIALISTA","cost_coins":380,"dmg":30,"desc":"Attacca nel turno difesa"},
    {"id":"clutch_rise","name":"Clutch Rise","role":None,"cost_coins":500,"dmg":50,"desc":"Danno x2 quando HP < 30%"},
    {"id":"final_spike","name":"FINAL SPIKE","role":None,"cost_coins":800,"dmg":80,"desc":"MOSSA FINALE — danno devastante"},
]

SUPERPOWERS = [
    {"id":"iron_will","name":"Iron Will","desc":"Riduce danni subiti del 10% per livello","max_level":5,"cost_per_level":200},
    {"id":"kill_shot","name":"Kill Shot","desc":"Aumenta ATK del 8% per livello","max_level":5,"cost_per_level":200},
    {"id":"stamina_boost","name":"Stamina Boost","desc":"Stamina si ricarica 15% più veloce per livello","max_level":5,"cost_per_level":150},
    {"id":"clutch_god","name":"Clutch God","desc":"HP critico (<30%): danno +20% per livello","max_level":3,"cost_per_level":350},
    {"id":"vision","name":"Vision","desc":"Vedi sempre la prossima mossa CPU per livello 3+","max_level":3,"cost_per_level":300},
]


# ─── CARD RENDERING ───────────────────────────────────────────────────────────

def render_card_html(card_data, size="normal", badge_text=None):
    """
    Genera HTML pulito per una carta MBT.
    size = 'small' | 'normal' | 'large'
    badge_text = testo opzionale sul badge in alto a destra (es. 'SQUADRA', 'PACK')
    """
    ovr = int(card_data.get("overall", 40))
    tier_name = get_tier_by_ovr(ovr)
    tier_info = CARD_TIERS.get(tier_name, CARD_TIERS["Bronzo Comune"])
    css_class = tier_info["css"]
    color = tier_info["color"]
    nome = card_data.get("nome", "Unknown")
    role = card_data.get("ruolo", "SPIKER")
    role_icon = ROLE_ICONS.get(role, "⚡")
    photo_path = card_data.get("foto_path", "")

    # Statistiche con fallback sicuro
    atk = int(card_data.get("attacco", 40))
    dif = int(card_data.get("difesa", 40))
    bat = int(card_data.get("battuta", 40))

    # Dimensioni
    size_map = {"small": "110px", "normal": "140px", "large": "175px"}
    width = size_map.get(size, "140px")

    ovr_size_map = {"small": "1.1rem", "normal": "1.35rem", "large": "1.7rem"}
    ovr_font = ovr_size_map.get(size, "1.35rem")

    size_class = f"size-{size}" if size in ("small", "large") else ""

    # Foto con gestione errori robusta
    if photo_path and os.path.exists(str(photo_path)):
        try:
            with open(photo_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            ext = str(photo_path).split(".")[-1].lower()
            mime = "image/png" if ext == "png" else "image/jpeg"
            foto_html = f'<img class="mbt-card-photo" src="data:{mime};base64,{b64}" alt="{nome}">'
        except Exception:
            foto_html = f'<div class="mbt-card-photo-placeholder">{role_icon}</div>'
    else:
        foto_html = f'<div class="mbt-card-photo-placeholder">{role_icon}</div>'

    # Tier label abbreviata
    tier_short = tier_name.replace("ICON ", "").replace(" Comune","").replace(" Raro","").replace(" Evoluto","").replace(" LEGGENDARIA","LEG")
    tier_short = tier_short[:8]

    # Badge opzionale
    badge_html = ""
    if badge_text:
        badge_html = f'<div class="card-source-badge">{badge_text}</div>'

    # Shimmer per carte oro+
    shimmer_html = ""
    if css_class in ("oro", "icon-base", "icon-epica", "icon-leggendaria", "icon-toty"):
        shimmer_html = f'<div style="position:absolute;top:0;left:-100%;width:50%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08),transparent);animation:shimmer 2.5s 1s infinite;pointer-events:none;z-index:3"></div>'

    html = f"""<div class="mbt-card-wrap" style="width:{width}">
  <div class="mbt-card {css_class} {size_class}" style="width:{width}">
    <div class="mbt-card-header">
      <div class="mbt-card-ovr" style="color:{color};font-size:{ovr_font}">{ovr}</div>
      <div class="mbt-card-tier-label" style="color:{color}">{tier_short}</div>
    </div>
    {foto_html}
    <div class="mbt-card-name" style="color:{color}">{nome.upper()}</div>
    <div class="mbt-card-role" style="color:{color}">{role_icon} {role}</div>
    <div class="mbt-card-divider"></div>
    <div class="mbt-card-stats">
      <div class="mbt-stat">
        <div class="mbt-stat-val" style="color:{color}">{atk}</div>
        <div class="mbt-stat-lbl" style="color:{color}">ATK</div>
      </div>
      <div class="mbt-stat">
        <div class="mbt-stat-val" style="color:{color}">{dif}</div>
        <div class="mbt-stat-lbl" style="color:{color}">DEF</div>
      </div>
      <div class="mbt-stat">
        <div class="mbt-stat-val" style="color:{color}">{bat}</div>
        <div class="mbt-stat-lbl" style="color:{color}">BAT</div>
      </div>
    </div>
    {shimmer_html}
    {badge_html}
  </div>
</div>"""
    return html


# ─── PACK OPENING ─────────────────────────────────────────────────────────────

def draw_cards_from_pack(pack_name, cards_db):
    """Pesca 6 carte da un pacchetto secondo le probabilità."""
    pack_info = PACKS[pack_name]
    weights = pack_info["weights"]
    tiers = list(weights.keys())
    probs = list(weights.values())
    total = sum(probs)
    probs = [p / total for p in probs]

    drawn = []
    all_cards = cards_db.get("cards", [])

    names_m = ["Marco","Luca","Andrea","Fabio","Simone","Giulio","Matteo","Riccardo","Davide","Paolo","Lorenzo","Alessandro"]
    surnames = ["Rossi","Bianchi","Ferrari","Conti","Esposito","Costa","Ricci","Serra","Gallo","Romano","Lombardi","De Luca"]

    for _ in range(6):
        chosen_tier = random.choices(tiers, weights=probs, k=1)[0]
        matching = [c for c in all_cards if get_tier_by_ovr(c.get("overall", 40)) == chosen_tier]
        if matching:
            card = matching[random.randint(0, len(matching)-1)].copy()
        else:
            tier_info = CARD_TIERS.get(chosen_tier, CARD_TIERS["Bronzo Comune"])
            lo, hi = tier_info["ovr_range"]
            ovr = random.randint(lo, hi)
            card = {
                "id": f"gen_{random.randint(100000,999999)}",
                "nome": random.choice(names_m),
                "cognome": random.choice(surnames),
                "overall": ovr,
                "ruolo": random.choice(list(ROLE_ICONS.keys())[:5]),
                "attacco": max(40, ovr - random.randint(0, 12)),
                "difesa": max(40, ovr - random.randint(0, 12)),
                "muro": max(40, ovr - random.randint(0, 18)),
                "ricezione": max(40, ovr - random.randint(0, 18)),
                "battuta": max(40, ovr - random.randint(0, 15)),
                "alzata": max(40, ovr - random.randint(0, 18)),
                "foto_path": "",
                "tier": chosen_tier,
                "generated": True,
            }
        # Ogni carta del pack ha un instance_id univoco
        card["instance_id"] = f"inst_{random.randint(10000000, 99999999)}"
        card["source"] = "pack"
        card["pack_name"] = pack_name
        drawn.append(card)

    return drawn


# ─── COLLECTION HELPERS ───────────────────────────────────────────────────────

def get_instance_id(card):
    """Restituisce l'ID univoco di un'istanza carta."""
    return card.get("instance_id") or card.get("id", "")

def add_card_to_collection(rivals_data, card):
    """Aggiunge una carta alla collezione del giocatore."""
    iid = get_instance_id(card)
    if iid and iid not in rivals_data.get("collection", []):
        rivals_data.setdefault("collection", []).append(iid)
        rivals_data.setdefault("collection_cards", []).append(card)
    return rivals_data

def is_in_active_team(rivals_data, card):
    iid = get_instance_id(card)
    return iid in rivals_data.get("active_team", [])

def add_to_active_team(rivals_data, card):
    iid = get_instance_id(card)
    if len(rivals_data.get("active_team", [])) < 5 and iid not in rivals_data.get("active_team", []):
        rivals_data.setdefault("active_team", []).append(iid)
        rivals_data.setdefault("active_team_cards", []).append(card)

def remove_from_active_team(rivals_data, card):
    iid = get_instance_id(card)
    if iid in rivals_data.get("active_team", []):
        rivals_data["active_team"].remove(iid)
        rivals_data["active_team_cards"] = [c for c in rivals_data.get("active_team_cards", []) if get_instance_id(c) != iid]

def get_active_team_cards(rivals_data):
    """Restituisce le carte del team attivo nell'ordine corretto."""
    team_ids = rivals_data.get("active_team", [])
    col_cards = rivals_data.get("collection_cards", [])
    result = []
    for tid in team_ids:
        card = next((c for c in col_cards if get_instance_id(c) == tid), None)
        if card:
            result.append(card)
    return result


# ─── SYNC OVR ─────────────────────────────────────────────────────────────────

def _sync_ovr_from_tournament(state, cards_db):
    try:
        from data_manager import calcola_overall_fifa
        for atleta in state.get("atleti", []):
            ovr = calcola_overall_fifa(atleta)
            for card in cards_db.get("cards", []):
                if card.get("atleta_id") == atleta.get("id"):
                    card["overall"] = ovr
                    s = atleta.get("stats", {})
                    card["attacco"] = s.get("attacco", card.get("attacco", 40))
                    card["difesa"] = s.get("difesa", card.get("difesa", 40))
                    card["muro"] = s.get("muro", card.get("muro", 40))
                    card["ricezione"] = s.get("ricezione", card.get("ricezione", 40))
                    card["battuta"] = s.get("battuta", card.get("battuta", 40))
                    card["alzata"] = s.get("alzata", card.get("alzata", 40))
    except Exception:
        pass


# ─── BATTLE ENGINE ────────────────────────────────────────────────────────────

def init_battle_state(player_cards, cpu_level=1):
    def make_fighter(card, is_cpu=False):
        ovr = card.get("overall", 40)
        base_hp = 80 + ovr * 2
        if is_cpu:
            base_hp = int(base_hp * (0.9 + cpu_level * 0.1))
        return {"card": card, "hp": base_hp, "max_hp": base_hp, "stamina": 100, "shield": 0}

    player_fighters = [make_fighter(c) for c in player_cards[:3]]
    cpu_ovr_base = 40 + cpu_level * 4
    cpu_names = ["Volkov","Storm","Ace","Blade","Vector","Nexus"]
    cpu_cards = []
    for i in range(3):
        ovr = min(99, cpu_ovr_base + random.randint(-5, 10))
        cpu_cards.append({
            "nome": random.choice(cpu_names),
            "overall": ovr,
            "ruolo": random.choice(list(ROLE_ICONS.keys())[:5]),
            "attacco": max(40, ovr - random.randint(0, 8)),
            "difesa": max(40, ovr - random.randint(0, 8)),
            "battuta": max(40, ovr - random.randint(0, 10)),
            "foto_path": "",
        })
    cpu_fighters = [make_fighter(c, is_cpu=True) for c in cpu_cards]

    return {
        "player_fighters": player_fighters,
        "cpu_fighters": cpu_fighters,
        "player_active_idx": 0,
        "cpu_active_idx": 0,
        "turn": 0,
        "phase": "battle",
        "log": [],
        "stamina_charges": 0,
        "start_time": time.time(),
        "time_limit": 300,
    }

def calculate_damage(attacker_card, defender_card, move_type="attack", superpowers=None):
    atk = attacker_card.get("attacco", 40)
    def_ = defender_card.get("difesa", 40)
    base = max(5, (atk - def_ * 0.6) * 0.4 + random.randint(3, 12))
    if move_type == "special": base *= 1.8
    elif move_type == "super": base *= 2.5
    if superpowers:
        base *= (1 + superpowers.get("kill_shot", 0) * 0.08)
    return max(5, int(base))

def cpu_choose_action(cpu_fighter, player_fighter, turn):
    hp_ratio = cpu_fighter["hp"] / max(cpu_fighter["max_hp"], 1)
    if hp_ratio < 0.3 and cpu_fighter["stamina"] >= 40:
        return "special"
    if cpu_fighter["stamina"] >= 50 and random.random() < 0.25:
        return "special"
    return random.choice(["attack", "attack", "attack", "defend"])

def process_battle_action(battle_state, action, rivals_data):
    p_idx = battle_state["player_active_idx"]
    c_idx = battle_state["cpu_active_idx"]
    p_fighter = battle_state["player_fighters"][p_idx]
    c_fighter = battle_state["cpu_fighters"][c_idx]
    log = battle_state["log"]
    superpowers = rivals_data.get("superpowers", {})
    player_name = p_fighter["card"].get("nome", "Tu")
    cpu_name = c_fighter["card"].get("nome", "CPU")

    if action == "attack":
        dmg = calculate_damage(p_fighter["card"], c_fighter["card"], "attack", superpowers)
        c_fighter["hp"] = max(0, c_fighter["hp"] - dmg)
        p_fighter["stamina"] = min(100, p_fighter["stamina"] + 10)
        battle_state["stamina_charges"] += 1
        log.append(f"⚡ {player_name} attacca → -{dmg} HP (CPU: {c_fighter['hp']})")
    elif action == "special":
        if p_fighter["stamina"] >= 40:
            dmg = calculate_damage(p_fighter["card"], c_fighter["card"], "special", superpowers)
            c_fighter["hp"] = max(0, c_fighter["hp"] - dmg)
            p_fighter["stamina"] -= 40
            log.append(f"🔥 SUPER ATTACCO {player_name} → -{dmg} HP!")
        else:
            log.append("⚠️ Stamina insufficiente per il Super Attacco!")
    elif action == "defend":
        p_fighter["shield"] = 30
        p_fighter["stamina"] = min(100, p_fighter["stamina"] + 20)
        log.append(f"🛡️ {player_name} si difende — scudo +30!")
    elif action == "final":
        if battle_state["stamina_charges"] >= 10:
            dmg = calculate_damage(p_fighter["card"], c_fighter["card"], "super", superpowers)
            c_fighter["hp"] = max(0, c_fighter["hp"] - dmg)
            battle_state["stamina_charges"] = 0
            log.append(f"💥 MOSSA FINALE! -{dmg} HP DEVASTANTI!")
        else:
            log.append(f"⚠️ Serve carica 10/10 — attuale: {battle_state['stamina_charges']}")

    if c_fighter["hp"] <= 0:
        next_cpu = c_idx + 1
        if next_cpu < len(battle_state["cpu_fighters"]):
            battle_state["cpu_active_idx"] = next_cpu
            log.append(f"💀 {cpu_name} eliminato! Prossimo avversario!")
        else:
            battle_state["phase"] = "win"
            log.append("🏆 HAI VINTO LA PARTITA!")
            battle_state["log"] = log[-20:]
            return

    if battle_state["phase"] == "battle":
        cpu_action = cpu_choose_action(c_fighter, p_fighter, battle_state["turn"])
        if cpu_action in ("attack", "special"):
            move = "special" if cpu_action == "special" else "attack"
            cpu_dmg = calculate_damage(c_fighter["card"], p_fighter["card"], move)
            if p_fighter["shield"] > 0:
                cpu_dmg = max(0, cpu_dmg - p_fighter["shield"])
                p_fighter["shield"] = 0
                log.append(f"🛡️ Scudo attivato! {cpu_name} → -{cpu_dmg} HP (dopo difesa)")
            else:
                label = "SUPER" if move == "special" else "attacca"
                log.append(f"🤖 {cpu_name} {label} → -{cpu_dmg} HP!")
            p_fighter["hp"] = max(0, p_fighter["hp"] - cpu_dmg)
            if cpu_action == "special":
                c_fighter["stamina"] = max(0, c_fighter["stamina"] - 40)
        else:
            c_fighter["shield"] = 25
            log.append(f"🤖 {cpu_name} si difende.")

    if p_fighter["hp"] <= 0:
        next_p = p_idx + 1
        if next_p < len(battle_state["player_fighters"]):
            battle_state["player_active_idx"] = next_p
            log.append(f"💔 {player_name} KO! Prossima carta!")
        else:
            battle_state["phase"] = "lose"
            log.append("💀 HAI PERSO! Tutte le carte KO.")

    battle_state["turn"] += 1
    if len(log) > 20:
        battle_state["log"] = log[-20:]


# ─── MAIN ENTRY POINT ─────────────────────────────────────────────────────────

def render_mbt_rivals(state):
    st.markdown(RIVALS_CSS, unsafe_allow_html=True)

    if "rivals_data" not in st.session_state:
        st.session_state.rivals_data = load_rivals_data()
    if "cards_db" not in st.session_state:
        st.session_state.cards_db = load_cards_db()

    rivals_data = st.session_state.rivals_data
    cards_db = st.session_state.cards_db

    _sync_ovr_from_tournament(state, cards_db)

    level = rivals_data["player_level"]
    xp = rivals_data["player_xp"]
    coins = rivals_data["mbt_coins"]
    xp_needed = XP_PER_LEVEL[min(level, 19)] if level < 20 else 99999
    xp_pct = min(100, int(xp / max(xp_needed, 1) * 100))
    current_arena = next((a for a in ARENE if a["min_level"] <= level <= a["max_level"]), ARENE[0])
    wins = rivals_data["battle_wins"]
    losses = rivals_data["battle_losses"]
    col_size = len(rivals_data.get("collection_cards", []))

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#07070f,#0e0e1c,#07070f);
        border:2px solid #1e1e3a;border-radius:14px;padding:14px 22px;margin-bottom:18px">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
        <div>
          <div style="font-family:'Orbitron',sans-serif;font-size:1.5rem;font-weight:900;
            background:linear-gradient(90deg,#ffd700,#ffec4a,#ffd700);
            background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
            animation:goldShine 3s linear infinite">⚡ MBT RIVALS</div>
          <div style="font-size:0.65rem;color:#555;letter-spacing:3px">CARD BATTLE SYSTEM</div>
        </div>
        <div style="display:flex;gap:18px;flex-wrap:wrap;align-items:center">
          <div style="text-align:center">
            <div style="font-family:'Orbitron',sans-serif;font-size:1.1rem;font-weight:900;color:#ffd700">LV.{level}</div>
            <div style="width:75px;height:5px;background:#1a1a2a;border-radius:3px;margin:3px auto;overflow:hidden">
              <div style="width:{xp_pct}%;height:100%;background:linear-gradient(90deg,#ffd700,#ffec4a);border-radius:3px"></div>
            </div>
            <div style="font-size:0.5rem;color:#666">{xp}/{xp_needed} XP</div>
          </div>
          <div style="text-align:center">
            <div style="font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:900;color:#ffd700">🪙 {coins:,}</div>
            <div style="font-size:0.5rem;color:#666;letter-spacing:2px">COINS</div>
          </div>
          <div style="text-align:center">
            <div style="font-family:'Orbitron',sans-serif;font-size:1rem;color:{current_arena['color']}">{current_arena['icon']} {current_arena['name']}</div>
            <div style="font-size:0.5rem;color:#666">{wins}V / {losses}S</div>
          </div>
          <div style="text-align:center">
            <div style="font-family:'Orbitron',sans-serif;font-size:1rem;color:#9b59b6">🃏 {col_size}</div>
            <div style="font-size:0.5rem;color:#666">CARTE</div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["⚔️ Battaglia", "🃏 Collezione", "🛒 Negozio", "🏟️ Arene", "💪 Poteri", "⚙️ Admin"])

    with tabs[0]: _render_battle_tab(rivals_data, cards_db, state)
    with tabs[1]: _render_collection_tab(rivals_data, cards_db, state)
    with tabs[2]: _render_shop_tab(rivals_data, cards_db)
    with tabs[3]: _render_arenas_tab(rivals_data)
    with tabs[4]: _render_powers_tab(rivals_data)
    with tabs[5]: _render_admin_tab(state, cards_db, rivals_data)

    save_rivals_data(rivals_data)
    save_cards_db(cards_db)


# ─── BATTLE TAB ───────────────────────────────────────────────────────────────

def _render_battle_tab(rivals_data, cards_db, state):
    st.markdown("## ⚔️ Battaglia vs CPU")

    battle_state = st.session_state.get("battle_state")

    if battle_state is None:
        team_cards = get_active_team_cards(rivals_data)

        st.markdown("### 🏆 Squadra Attiva")
        if not team_cards:
            st.warning("⚠️ Nessuna carta nel team attivo! Vai nella scheda **Collezione** e aggiungi fino a 5 carte.")
            return

        cols = st.columns(min(5, len(team_cards)))
        for i, card in enumerate(team_cards[:5]):
            with cols[i]:
                st.markdown(render_card_html(card, size="small"), unsafe_allow_html=True)
                ovr = card.get("overall", 40)
                tier = get_tier_by_ovr(ovr)
                st.caption(f"OVR {ovr}")

        st.markdown("---")
        level = rivals_data["player_level"]
        current_arena = next((a for a in ARENE if a["min_level"] <= level <= a["max_level"]), ARENE[0])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="arena-badge {current_arena['css']}">
              <div style="font-size:1.8rem">{current_arena['icon']}</div>
              <div style="font-family:'Orbitron',sans-serif;font-weight:700;
                color:{current_arena['color']};font-size:0.8rem">{current_arena['name']}</div>
              <div style="font-size:0.6rem;color:#888">LV.{level}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="background:#10101e;border:1px solid #1e1e3a;border-radius:10px;
              padding:14px;text-align:center">
              <div style="font-size:1.6rem">🤖</div>
              <div style="font-family:'Orbitron',sans-serif;color:#dc2626;font-weight:700;font-size:0.85rem">
                CPU LV.{level}</div>
              <div style="font-size:0.6rem;color:#666">Difficoltà adattiva</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            coins_r = 50 + level * 10
            xp_r = 30 + level * 5
            trofei_r = 2 + level
            st.markdown(f"""
            <div style="background:#10101e;border:1px solid #16a34a;border-radius:10px;
              padding:14px;text-align:center">
              <div style="font-size:0.75rem;color:#4ade80;font-weight:700;font-family:'Orbitron',sans-serif">RICOMPENSE</div>
              <div style="font-size:0.7rem;color:#ffd700;margin-top:4px">🪙 +{coins_r}</div>
              <div style="font-size:0.7rem;color:#60a5fa">⭐ +{xp_r} XP</div>
              <div style="font-size:0.7rem;color:#9b59b6">🏆 +{trofei_r} Trofei</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")
        if st.button("⚔️ INIZIA BATTAGLIA!", use_container_width=True, type="primary"):
            st.session_state.battle_state = init_battle_state(team_cards[:3], cpu_level=level)
            st.rerun()
    else:
        _render_active_battle(battle_state, rivals_data, cards_db)


def _render_active_battle(battle_state, rivals_data, cards_db):
    phase = battle_state["phase"]

    if phase == "win":
        level = rivals_data["player_level"]
        xp_gain = 30 + level * 5
        coins_gain = 50 + level * 10
        trofei_gain = 2 + level
        rivals_data["player_xp"] += xp_gain
        rivals_data["mbt_coins"] += coins_gain
        rivals_data["trofei_rivals"] += trofei_gain
        rivals_data["battle_wins"] += 1
        _check_level_up(rivals_data)
        st.markdown(f"""
        <div style="text-align:center;padding:28px;
          background:linear-gradient(135deg,#001a00,#003300);
          border:3px solid #16a34a;border-radius:16px;margin-bottom:16px">
          <div style="font-size:3rem">🏆</div>
          <div style="font-family:'Orbitron',sans-serif;font-size:1.8rem;font-weight:900;color:#4ade80">VITTORIA!</div>
          <div style="color:#ffd700;margin-top:8px;font-size:0.8rem">
            +{xp_gain} XP &nbsp;|&nbsp; +{coins_gain} Coins &nbsp;|&nbsp; +{trofei_gain} Trofei
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 Nuova Partita", use_container_width=True, type="primary"):
            st.session_state.battle_state = None
            st.rerun()
        return

    if phase == "lose":
        rivals_data["battle_losses"] += 1
        rivals_data["player_xp"] += 10
        rivals_data["mbt_coins"] += 20
        _check_level_up(rivals_data)
        st.markdown("""
        <div style="text-align:center;padding:28px;
          background:linear-gradient(135deg,#1a0000,#330000);
          border:3px solid #dc2626;border-radius:16px;margin-bottom:16px">
          <div style="font-size:3rem">💀</div>
          <div style="font-family:'Orbitron',sans-serif;font-size:1.8rem;font-weight:900;color:#ef4444">SCONFITTA</div>
          <div style="color:#888;margin-top:8px;font-size:0.75rem">+10 XP | +20 Coins per aver combattuto</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 Riprova", use_container_width=True):
            st.session_state.battle_state = None
            st.rerun()
        return

    # Battaglia attiva
    p_idx = battle_state["player_active_idx"]
    c_idx = battle_state["cpu_active_idx"]
    p_fighter = battle_state["player_fighters"][p_idx]
    c_fighter = battle_state["cpu_fighters"][c_idx]

    elapsed = time.time() - battle_state["start_time"]
    remaining = max(0, battle_state["time_limit"] - elapsed)
    if remaining <= 0:
        battle_state["phase"] = "lose"
        st.rerun()

    min_r = int(remaining // 60)
    sec_r = int(remaining % 60)

    col_p, col_mid, col_c = st.columns([5, 2, 5])

    with col_p:
        st.markdown(f"**⚡ {p_fighter['card'].get('nome','Tu')}**")
        hp_pct = max(0, int(p_fighter['hp'] / max(p_fighter['max_hp'],1) * 100))
        hp_class = "danger" if hp_pct < 30 else ""
        st.markdown(f"""
        <div class="hp-bar-container">
          <div class="hp-bar-fill {hp_class}" style="width:{hp_pct}%"></div>
        </div>
        <div style="font-size:0.65rem;color:#888;margin-top:2px">
          ❤️ {p_fighter['hp']}/{p_fighter['max_hp']}
        </div>
        <div style="height:6px;background:#1a1a2a;border-radius:3px;overflow:hidden;margin-top:6px">
          <div style="width:{p_fighter['stamina']}%;height:100%;
            background:linear-gradient(90deg,#ffd700,#ffec4a);border-radius:3px;transition:width 0.3s">
          </div>
        </div>
        <div style="font-size:0.58rem;color:#888;margin-top:1px">⚡ Stamina: {int(p_fighter['stamina'])}%</div>
        """, unsafe_allow_html=True)
        st.markdown(render_card_html(p_fighter["card"], size="small"), unsafe_allow_html=True)

    with col_mid:
        st.markdown(f"""
        <div style="text-align:center;padding:16px 0">
          <div style="font-family:'Orbitron',sans-serif;font-size:1.4rem;font-weight:900;color:#dc2626">VS</div>
          <div style="font-size:0.7rem;color:#888;margin-top:10px">⏱️ {min_r:02d}:{sec_r:02d}</div>
          <div style="font-size:0.62rem;color:#ffd700;margin-top:4px">Turno {battle_state['turn']}</div>
          <div style="font-size:0.58rem;color:#888;margin-top:6px">
            Carica:<br>
            <span style="color:#ff6600;font-weight:700">{battle_state['stamina_charges']}/10</span>
          </div>
        </div>""", unsafe_allow_html=True)

    with col_c:
        st.markdown(f"**🤖 {c_fighter['card'].get('nome','CPU')}**")
        chp_pct = max(0, int(c_fighter['hp'] / max(c_fighter['max_hp'],1) * 100))
        st.markdown(f"""
        <div class="hp-bar-container">
          <div style="width:{chp_pct}%;height:100%;
            background:linear-gradient(90deg,#dc2626,#ef4444);border-radius:8px;transition:width 0.5s">
          </div>
        </div>
        <div style="font-size:0.65rem;color:#888;margin-top:2px">
          ❤️ {c_fighter['hp']}/{c_fighter['max_hp']}
        </div>""", unsafe_allow_html=True)
        st.markdown(render_card_html(c_fighter["card"], size="small"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎮 Scegli la tua mossa:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("⚡ ATTACCO", key="battle_attack", use_container_width=True):
            process_battle_action(battle_state, "attack", rivals_data)
            st.rerun()
    with col2:
        can_special = p_fighter["stamina"] >= 40
        if st.button(f"🔥 SUPER {'✓' if can_special else '✗'}", key="battle_special",
                     use_container_width=True, disabled=not can_special):
            process_battle_action(battle_state, "special", rivals_data)
            st.rerun()
    with col3:
        if st.button("🛡️ DIFENDI", key="battle_defend", use_container_width=True):
            process_battle_action(battle_state, "defend", rivals_data)
            st.rerun()
    with col4:
        can_final = battle_state["stamina_charges"] >= 10
        if st.button(f"💥 FINALE {'✓' if can_final else str(battle_state['stamina_charges'])+'/10'}",
                     key="battle_final", use_container_width=True, disabled=not can_final):
            process_battle_action(battle_state, "final", rivals_data)
            st.rerun()

    if battle_state["log"]:
        with st.expander("📋 Log Battaglia", expanded=True):
            log_html = '<div class="battle-log">'
            for entry in reversed(battle_state["log"][-8:]):
                log_html += f'<div style="padding:2px 0;border-bottom:1px solid #14142a;color:#ccc">{entry}</div>'
            log_html += '</div>'
            st.markdown(log_html, unsafe_allow_html=True)

    if st.button("🏳️ Abbandona", key="battle_quit"):
        rivals_data["battle_losses"] += 1
        st.session_state.battle_state = None
        st.rerun()


def _check_level_up(rivals_data):
    level = rivals_data["player_level"]
    if level >= 20:
        return
    xp = rivals_data["player_xp"]
    xp_needed = XP_PER_LEVEL[level]
    if xp >= xp_needed:
        rivals_data["player_level"] += 1
        rivals_data["trofei_rivals"] += 10
        rivals_data["arena_unlocked"] = rivals_data["player_level"]


# ─── COLLECTION TAB ───────────────────────────────────────────────────────────

def _render_collection_tab(rivals_data, cards_db, state):
    st.markdown("## 🃏 La Mia Collezione")

    col_cards = rivals_data.get("collection_cards", [])
    active_team = rivals_data.get("active_team", [])

    # ── SEZIONE TEAM ATTIVO ──
    team_cards = get_active_team_cards(rivals_data)
    n_team = len(team_cards)

    st.markdown(f"### 👥 Team Attivo ({n_team}/5)")

    if n_team == 0:
        st.info("Nessuna carta nel team! Aggiungi carte dalla tua collezione qui sotto.")
    else:
        team_cols = st.columns(5)
        for i in range(5):
            with team_cols[i]:
                if i < n_team:
                    card = team_cards[i]
                    st.markdown(render_card_html(card, size="small"), unsafe_allow_html=True)
                    ovr = card.get("overall", 40)
                    if st.button("❌", key=f"rm_team_col_{get_instance_id(card)[:10]}", use_container_width=True, help="Rimuovi dal team"):
                        remove_from_active_team(rivals_data, card)
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div style="width:100%;height:165px;border:2px dashed #1e1e3a;
                      border-radius:12px;display:flex;align-items:center;justify-content:center;
                      color:#333;font-size:1.5rem">＋</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── TAB: Collezione / Atleti reali ──
    source_tabs = st.tabs(["🃏 Le Mie Carte", "⭐ Atleti Reali"])

    with source_tabs[0]:
        _render_my_cards_grid(rivals_data, col_cards, active_team)

    with source_tabs[1]:
        _render_real_athletes_collection(rivals_data, cards_db, state)


def _render_my_cards_grid(rivals_data, col_cards, active_team):
    """Griglia carte possedute con aggiunta al team."""
    if not col_cards:
        st.warning("📦 Non hai ancora carte! Acquista pacchetti nel **Negozio** o aggiungi atleti reali.")
        return

    # Filtri
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        tier_filter = st.selectbox("🔍 Filtra Rarità", ["Tutte"] + list(CARD_TIERS.keys()), key="coll_filter_tier")
    with col_f2:
        sort_opt = st.selectbox("↕️ Ordina per", ["OVR (alto→basso)", "Rarità", "Nome"], key="coll_sort")

    filtered = col_cards.copy()
    if tier_filter != "Tutte":
        filtered = [c for c in filtered if get_tier_by_ovr(c.get("overall", 40)) == tier_filter]

    if sort_opt == "OVR (alto→basso)":
        filtered.sort(key=lambda c: c.get("overall", 0), reverse=True)
    elif sort_opt == "Rarità":
        filtered.sort(key=lambda c: CARD_TIERS.get(get_tier_by_ovr(c.get("overall", 40)), {}).get("rarity", 0), reverse=True)
    elif sort_opt == "Nome":
        filtered.sort(key=lambda c: c.get("nome", ""))

    st.caption(f"📊 {len(col_cards)} carte totali | {len(filtered)} mostrate")

    cols_per_row = 5
    for i in range(0, len(filtered), cols_per_row):
        chunk = filtered[i:i + cols_per_row]
        row_cols = st.columns(cols_per_row)
        for j, card in enumerate(chunk):
            with row_cols[j]:
                iid = get_instance_id(card)
                in_team = iid in rivals_data.get("active_team", [])
                source = card.get("source", "")
                src_label = "PACK" if source == "pack" else ("ATLETA" if source == "athlete" else "ADMIN")

                st.markdown(render_card_html(card, size="small", badge_text=src_label), unsafe_allow_html=True)
                st.caption(f"OVR {card.get('overall',40)} · {get_tier_by_ovr(card.get('overall',40))[:8]}")

                if in_team:
                    if st.button("✅ In squadra", key=f"rm_{iid[:10]}", use_container_width=True):
                        remove_from_active_team(rivals_data, card)
                        st.rerun()
                else:
                    disabled = len(rivals_data.get("active_team", [])) >= 5
                    btn_label = "➕ Squadra" if not disabled else "🔒 Max 5"
                    if st.button(btn_label, key=f"add_{iid[:10]}", use_container_width=True, disabled=disabled):
                        add_to_active_team(rivals_data, card)
                        st.rerun()


def _render_real_athletes_collection(rivals_data, cards_db, state):
    """Aggiunge carte dagli atleti reali del torneo."""
    atleti = state.get("atleti", [])
    if not atleti:
        st.info("Nessun atleta nel torneo. Aggiungili prima nella sezione Atleti.")
        return

    st.markdown("Aggiungi gli atleti reali del torneo come carte alla tua collezione.")

    try:
        from data_manager import calcola_overall_fifa
        has_ovr = True
    except Exception:
        has_ovr = False

    col_ids = [get_instance_id(c) for c in rivals_data.get("collection_cards", [])]

    cols_per_row = 4
    for i in range(0, len(atleti), cols_per_row):
        chunk = atleti[i:i + cols_per_row]
        row_cols = st.columns(cols_per_row)
        for j, atleta in enumerate(chunk):
            with row_cols[j]:
                ovr = calcola_overall_fifa(atleta) if has_ovr else 60
                s = atleta.get("stats", {})
                card = {
                    "id": f"athlete_{atleta.get('id','?')}",
                    "instance_id": f"ath_{atleta.get('id','?')}",
                    "nome": atleta.get("nome", "?"),
                    "cognome": atleta.get("cognome", ""),
                    "overall": ovr,
                    "ruolo": atleta.get("ruolo", "SPIKER"),
                    "attacco": s.get("attacco", 50),
                    "difesa": s.get("difesa", 50),
                    "muro": s.get("muro", 50),
                    "ricezione": s.get("ricezione", 50),
                    "battuta": s.get("battuta", 50),
                    "alzata": s.get("alzata", 50),
                    "foto_path": atleta.get("foto_path", ""),
                    "source": "athlete",
                    "atleta_id": atleta.get("id"),
                }
                ath_iid = get_instance_id(card)
                already_owned = ath_iid in col_ids

                st.markdown(render_card_html(card, size="small", badge_text="ATLETA"), unsafe_allow_html=True)
                st.caption(f"OVR {ovr} · {get_tier_by_ovr(ovr)[:10]}")

                if already_owned:
                    in_team = ath_iid in rivals_data.get("active_team", [])
                    if in_team:
                        if st.button("✅ In squadra", key=f"ath_rm_{ath_iid[:12]}", use_container_width=True):
                            remove_from_active_team(rivals_data, card)
                            st.rerun()
                    else:
                        disabled = len(rivals_data.get("active_team", [])) >= 5
                        if st.button("➕ Squadra" if not disabled else "🔒 Max 5",
                                     key=f"ath_team_{ath_iid[:12]}", use_container_width=True, disabled=disabled):
                            add_to_active_team(rivals_data, card)
                            st.rerun()
                else:
                    if st.button("📥 Aggiungi collezione", key=f"ath_add_{ath_iid[:12]}", use_container_width=True, type="primary"):
                        add_card_to_collection(rivals_data, card)
                        st.rerun()


# ─── SHOP TAB ─────────────────────────────────────────────────────────────────

def _render_shop_tab(rivals_data, cards_db):
    st.markdown("## 🛒 Negozio Pacchetti")

    coins = rivals_data.get("mbt_coins", 0)
    st.markdown(f"""
    <div style="text-align:right;margin-bottom:16px">
      <span style="font-family:'Orbitron',sans-serif;font-size:1.1rem;color:#ffd700;font-weight:700">
        🪙 {coins:,} MBT Coins
      </span>
    </div>""", unsafe_allow_html=True)

    pack_names = ["Base", "Epico", "Leggenda"]
    pack_descs = {
        "Base": "Bronzo, Argento e raramente Oro. Perfetto per iniziare.",
        "Epico": "Da Oro a Leggenda. Alta chance di Eroi e TOTY!",
        "Leggenda": "Solo carte di alto livello. Garantisce Leggenda+",
    }

    pack_cols = st.columns(3)
    for i, pack_name in enumerate(pack_names):
        pack_info = PACKS[pack_name]
        with pack_cols[i]:
            can_afford = coins >= pack_info["price"]
            border_color = pack_info["label_color"]

            st.markdown(f"""
            <div class="pack-card-visual {pack_info['css']}" style="margin-bottom:10px">
              <div style="font-size:2.5rem">{pack_info['emoji']}</div>
              <div style="font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:900;
                color:{border_color};letter-spacing:3px;margin-top:6px">{pack_name.upper()}</div>
              <div style="font-size:0.6rem;color:#888;margin:8px 0;min-height:32px">{pack_descs[pack_name]}</div>
              <div style="font-size:0.65rem;color:#666;margin-bottom:4px">6 carte per pacchetto</div>
              <div style="font-family:'Orbitron',sans-serif;font-size:1.1rem;font-weight:700;color:#ffd700">
                🪙 {pack_info['price']:,}
              </div>
            </div>""", unsafe_allow_html=True)

            btn_txt = f"🛒 Apri pacchetto {pack_name}" if can_afford else "🔒 Coins insufficienti"
            if st.button(btn_txt, key=f"buy_pack_{pack_name}", use_container_width=True,
                         disabled=not can_afford, type="primary" if can_afford else "secondary"):
                rivals_data["mbt_coins"] -= pack_info["price"]
                drawn = draw_cards_from_pack(pack_name, cards_db)
                st.session_state["drawn_cards"] = drawn
                st.session_state["opening_pack"] = pack_name
                st.rerun()

    # ── VISUALIZZA CARTE PESCATE ──
    drawn = st.session_state.get("drawn_cards")
    if drawn:
        pack_name_opened = st.session_state.get("opening_pack", "Base")
        st.markdown("---")

        max_rarity = max(
            CARD_TIERS.get(get_tier_by_ovr(c.get("overall", 40)), {}).get("rarity", 0)
            for c in drawn
        )
        if max_rarity >= 12:
            st.markdown(f"""
            <div style="text-align:center;background:rgba(255,215,0,0.08);
              border:2px solid #ffd700;border-radius:10px;padding:10px;margin-bottom:14px;
              animation:goldPulse 1s infinite">
              <span style="font-family:'Orbitron',sans-serif;font-size:1rem;color:#ffd700">
                ⚡ CARTA ICONA TROVATA! ⚡
              </span>
            </div>""", unsafe_allow_html=True)
        elif max_rarity >= 8:
            st.markdown("""
            <div style="text-align:center;background:rgba(255,255,255,0.04);
              border:2px solid #fff;border-radius:10px;padding:8px;margin-bottom:14px">
              <span style="font-family:'Orbitron',sans-serif;font-size:0.9rem;color:#fff">
                ✨ CARTA LEGGENDARIA O SUPERIORE! ✨
              </span>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"### 🎁 Pacchetto **{pack_name_opened}** — 6 carte trovate:")
        card_cols = st.columns(6)
        for i, card in enumerate(drawn):
            with card_cols[i]:
                tier = get_tier_by_ovr(card.get("overall", 40))
                tc = CARD_TIERS.get(tier, {}).get("color", "#888")
                rarity = CARD_TIERS.get(tier, {}).get("rarity", 0)
                st.markdown(f"""
                <div style="animation:cardFlip 0.6s {i*0.12:.2f}s ease-out both;opacity:0">
                  {render_card_html(card, size="small", badge_text=pack_name_opened.upper()[:4])}
                </div>
                <div style="text-align:center;font-size:0.5rem;color:{tc};
                  margin-top:3px;font-weight:{'700' if rarity>=8 else '400'}">
                  {'⚡ ' if rarity>=12 else ('✦ ' if rarity>=8 else '')}{tier}
                </div>""", unsafe_allow_html=True)

        st.markdown("")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ Aggiungi TUTTE alla Collezione", use_container_width=True, type="primary"):
                for card in drawn:
                    add_card_to_collection(rivals_data, card)
                st.session_state["drawn_cards"] = None
                st.session_state["opening_pack"] = None
                st.success(f"✅ {len(drawn)} carte aggiunte alla collezione!")
                st.rerun()
        with col_b:
            if st.button("🗑️ Scarta (non aggiungere)", use_container_width=True):
                st.session_state["drawn_cards"] = None
                st.session_state["opening_pack"] = None
                st.rerun()

    # ── MOSSE SPECIALI ──
    st.markdown("---")
    st.markdown("### ⚡ Mosse Speciali")
    learned = rivals_data.get("special_moves_learned", [])
    move_cols = st.columns(3)
    for i, move in enumerate(SPECIAL_MOVES[:9]):
        with move_cols[i % 3]:
            already = move["id"] in learned
            can_aff = coins >= move["cost_coins"]
            role_tag = f"[{move['role']}]" if move.get("role") else "[Universale]"
            border = "#ffd700" if already else "#1e1e3a"
            st.markdown(f"""
            <div style="background:#0e0e1c;border:1px solid {border};
              border-radius:8px;padding:10px;margin-bottom:8px;min-height:95px">
              <div style="font-family:'Orbitron',sans-serif;font-size:0.68rem;font-weight:700;
                color:{'#ffd700' if already else '#ccc'}">{move['name']}</div>
              <div style="font-size:0.52rem;color:#555;margin:3px 0">{role_tag}</div>
              <div style="font-size:0.58rem;color:#777">{move['desc']}</div>
              <div style="font-size:0.58rem;color:{'#4ade80' if already else '#ffd700'};margin-top:4px">
                {'✅ Appresa' if already else f'🪙 {move["cost_coins"]:,}'}
              </div>
            </div>""", unsafe_allow_html=True)
            if not already:
                if st.button("Apprendi", key=f"learn_{move['id']}", disabled=not can_aff, use_container_width=True):
                    rivals_data["special_moves_learned"].append(move["id"])
                    rivals_data["mbt_coins"] -= move["cost_coins"]
                    st.rerun()


# ─── ARENAS TAB ───────────────────────────────────────────────────────────────

def _render_arenas_tab(rivals_data):
    st.markdown("## 🏟️ Sistema Arene")
    st.caption("Avanza di livello per sbloccare arene sempre più epiche!")
    level = rivals_data["player_level"]

    for arena in ARENE:
        is_unlocked = level >= arena["min_level"]
        is_current = arena["min_level"] <= level <= arena["max_level"]
        col1, col2 = st.columns([1, 4])
        with col1:
            opacity = "1" if is_unlocked else "0.35"
            gscale = "" if is_unlocked else "filter:grayscale(80%);"
            st.markdown(f"""
            <div class="arena-badge {arena['css']}" style="opacity:{opacity};{gscale}">
              <div style="font-size:1.8rem">{arena['icon'] if is_unlocked else '🔒'}</div>
              <div style="font-family:'Orbitron',sans-serif;font-size:0.6rem;font-weight:700;
                color:{arena['color'] if is_unlocked else '#444'}">LV.{arena['min_level']}-{arena['max_level']}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            status = " 🔴 ATTUALE" if is_current else (" ✅" if is_unlocked else " 🔒")
            color = arena["color"] if is_unlocked else "#444"
            st.markdown(f"""
            <div style="padding:10px 0">
              <div style="font-family:'Orbitron',sans-serif;font-weight:700;
                color:{color};font-size:0.85rem">{arena['name']}{status}</div>
              <div style="font-size:0.65rem;color:#555">Livelli {arena['min_level']} – {arena['max_level']}</div>
              {'<div style="font-size:0.62rem;color:#ffd700;margin-top:3px">⚡ Combatti qui per ricompense speciali!</div>' if is_current else ''}
            </div>""", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#14142a;margin:4px 0'>", unsafe_allow_html=True)


# ─── POWERS TAB ───────────────────────────────────────────────────────────────

def _render_powers_tab(rivals_data):
    st.markdown("## 💪 Super Poteri")
    coins = rivals_data.get("mbt_coins", 0)
    superpowers = rivals_data.setdefault("superpowers", {})

    for power in SUPERPOWERS:
        current_level = superpowers.get(power["id"], 0)
        max_level = power["max_level"]
        cost = power["cost_per_level"]
        bars = "█" * current_level + "░" * (max_level - current_level)

        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"""
            <div style="background:#0e0e1c;border:1px solid #1e1e3a;border-radius:8px;padding:12px;margin-bottom:6px">
              <div style="font-family:'Orbitron',sans-serif;font-size:0.78rem;font-weight:700;color:#ffd700">
                {power['name']}
                <span style="font-size:0.6rem;color:#666;font-weight:400"> LV.{current_level}/{max_level}</span>
              </div>
              <div style="font-size:0.62rem;color:#888;margin:4px 0">{power['desc']}</div>
              <div style="font-size:0.9rem;color:#ffd700;letter-spacing:3px">{bars}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            if current_level < max_level:
                st.markdown(f"<div style='padding-top:12px;font-size:0.7rem;color:#ffd700'>🪙 {cost}</div>", unsafe_allow_html=True)
        with col3:
            if current_level < max_level:
                if st.button("⬆️", key=f"up_{power['id']}", disabled=coins < cost,
                             help=f"Potenzia {power['name']} — costa {cost} coins", use_container_width=True):
                    superpowers[power["id"]] = current_level + 1
                    rivals_data["mbt_coins"] -= cost
                    st.rerun()
            else:
                st.markdown('<div style="color:#ffd700;text-align:center;padding:14px 0;font-size:0.75rem">✅ MAX</div>', unsafe_allow_html=True)


# ─── ADMIN TAB ────────────────────────────────────────────────────────────────

def _render_admin_tab(state, cards_db, rivals_data):
    st.markdown("## ⚙️ Pannello Admin — Cards Creator")
    admin_tabs = st.tabs(["➕ Crea Carta", "📋 Gestisci Carte", "🎁 Coins & XP"])

    with admin_tabs[0]: _render_card_creator(state, cards_db, rivals_data)
    with admin_tabs[1]: _render_card_manager(cards_db)
    with admin_tabs[2]: _render_coins_manager(rivals_data)


def _render_card_creator(state, cards_db, rivals_data):
    st.markdown("### ✏️ Crea Nuova Carta")

    col_form, col_preview = st.columns([2, 1])

    with col_form:
        nome = st.text_input("Nome", key="cc_nome")
        cognome = st.text_input("Cognome", key="cc_cognome")
        ruolo = st.selectbox("Ruolo", ROLES, key="cc_ruolo")
        st.markdown("---")
        overall = st.slider("Overall (OVR)", 40, 125, 75, key="cc_ovr")
        tier_preview = get_tier_by_ovr(overall)
        tier_color = CARD_TIERS.get(tier_preview, {}).get("color", "#ffd700")
        st.markdown(f'<div style="font-family:Orbitron,sans-serif;font-size:0.75rem;color:{tier_color};margin-bottom:6px">Tier: {tier_preview}</div>', unsafe_allow_html=True)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            atk = st.slider("⚡ Attacco", 40, 99, min(overall, 99), key="cc_atk")
            dif = st.slider("🛡️ Difesa", 40, 99, min(overall, 99), key="cc_dif")
            ric = st.slider("🤲 Ricezione", 40, 99, min(overall, 99), key="cc_ric")
        with col_s2:
            bat = st.slider("🏐 Battuta", 40, 99, min(overall, 99), key="cc_bat")
            mur = st.slider("🧱 Muro", 40, 99, min(overall, 99), key="cc_mur")
            alz = st.slider("🎯 Alzata", 40, 99, min(overall, 99), key="cc_alz")

        st.markdown("---")
        foto_file = st.file_uploader("📷 Foto Atleta", type=["png","jpg","jpeg"], key="cc_foto")
        foto_path = ""
        if foto_file:
            os.makedirs(ASSETS_ICONS_DIR, exist_ok=True)
            safe_name = (nome or "card").replace(" ", "_")
            foto_path = os.path.join(ASSETS_ICONS_DIR, f"{safe_name}_{random.randint(1000,9999)}.jpg")
            with open(foto_path, "wb") as f:
                f.write(foto_file.read())
            st.success(f"✅ Foto salvata")

        atleti_nomi = ["-- Nessuno --"] + [a["nome"] for a in state.get("atleti", [])]
        selected_atleta_nome = st.selectbox("🔗 Collega Atleta Torneo", atleti_nomi, key="cc_atleta_link")
        atleta_id_linked = None
        if selected_atleta_nome != "-- Nessuno --":
            linked = next((a for a in state.get("atleti", []) if a["nome"] == selected_atleta_nome), None)
            if linked:
                atleta_id_linked = linked["id"]
                try:
                    from data_manager import calcola_overall_fifa
                    real_ovr = calcola_overall_fifa(linked)
                    st.info(f"📊 OVR reale: **{real_ovr}**")
                except Exception:
                    pass

    with col_preview:
        st.markdown("#### 👁️ Anteprima")
        preview_card = {
            "nome": nome or "NOME",
            "overall": overall,
            "ruolo": ruolo,
            "attacco": st.session_state.get("cc_atk", overall),
            "difesa": st.session_state.get("cc_dif", overall),
            "battuta": st.session_state.get("cc_bat", overall),
            "muro": st.session_state.get("cc_mur", overall),
            "ricezione": st.session_state.get("cc_ric", overall),
            "alzata": st.session_state.get("cc_alz", overall),
            "foto_path": foto_path,
        }
        st.markdown(f"""
        <div style="display:flex;justify-content:center;padding:16px;
          background:radial-gradient(ellipse at center,rgba(255,215,0,0.04) 0%,transparent 70%);
          border-radius:12px;border:1px dashed #2a2a3a">
          {render_card_html(preview_card, size="large")}
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_save1, col_save2 = st.columns(2)
    with col_save1:
        if st.button("💾 Salva nel Database", use_container_width=True, type="primary"):
            if not nome:
                st.error("Inserisci il nome!")
            else:
                new_id = f"card_{cards_db['next_id']}_{random.randint(1000,9999)}"
                cards_db["next_id"] += 1
                new_card = {
                    "id": new_id,
                    "instance_id": f"admin_{new_id}",
                    "nome": nome,
                    "cognome": cognome,
                    "overall": overall,
                    "ruolo": ruolo,
                    "attacco": st.session_state.get("cc_atk", overall),
                    "difesa": st.session_state.get("cc_dif", overall),
                    "muro": st.session_state.get("cc_mur", overall),
                    "ricezione": st.session_state.get("cc_ric", overall),
                    "battuta": st.session_state.get("cc_bat", overall),
                    "alzata": st.session_state.get("cc_alz", overall),
                    "foto_path": foto_path,
                    "tier": tier_preview,
                    "atleta_id": atleta_id_linked,
                    "source": "admin",
                    "created_at": datetime.now().isoformat(),
                }
                cards_db["cards"].append(new_card)
                save_cards_db(cards_db)
                st.session_state.cards_db = cards_db
                st.success(f"✅ **{nome} {cognome}** (OVR {overall} · {tier_preview}) salvata!")
                st.rerun()
    with col_save2:
        if st.button("💾 Salva e Aggiungi a Collezione", use_container_width=True):
            if not nome:
                st.error("Inserisci il nome!")
            else:
                new_id = f"card_{cards_db['next_id']}_{random.randint(1000,9999)}"
                cards_db["next_id"] += 1
                new_card = {
                    "id": new_id,
                    "instance_id": f"admin_{new_id}",
                    "nome": nome, "cognome": cognome, "overall": overall, "ruolo": ruolo,
                    "attacco": st.session_state.get("cc_atk", overall),
                    "difesa": st.session_state.get("cc_dif", overall),
                    "muro": st.session_state.get("cc_mur", overall),
                    "ricezione": st.session_state.get("cc_ric", overall),
                    "battuta": st.session_state.get("cc_bat", overall),
                    "alzata": st.session_state.get("cc_alz", overall),
                    "foto_path": foto_path, "tier": tier_preview,
                    "atleta_id": atleta_id_linked, "source": "admin",
                    "created_at": datetime.now().isoformat(),
                }
                cards_db["cards"].append(new_card)
                save_cards_db(cards_db)
                st.session_state.cards_db = cards_db
                add_card_to_collection(rivals_data, new_card)
                st.success(f"✅ Carta creata e aggiunta alla collezione!")
                st.rerun()


def _render_card_manager(cards_db):
    st.markdown("### 📋 Carte nel Database")
    all_cards = cards_db.get("cards", [])

    if not all_cards:
        st.info("Nessuna carta nel database.")
        return

    filter_tier = st.selectbox("Filtra Tier", ["Tutte"] + list(CARD_TIERS.keys()), key="mgr_filter")
    filtered = all_cards if filter_tier == "Tutte" else \
        [c for c in all_cards if get_tier_by_ovr(c.get("overall", 40)) == filter_tier]

    st.caption(f"{len(all_cards)} carte totali | {len(filtered)} mostrate")

    for i, card in enumerate(filtered):
        tier = get_tier_by_ovr(card.get("overall", 40))
        tc = CARD_TIERS.get(tier, {}).get("color", "#888")
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            st.markdown(render_card_html(card, size="small", badge_text="DB"), unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="padding:6px 0">
              <div style="font-family:'Orbitron',sans-serif;font-weight:700;color:{tc};font-size:0.82rem">
                {card.get('nome','')} {card.get('cognome','')}
              </div>
              <div style="font-size:0.65rem;color:#777">OVR {card.get('overall',40)} · {tier} · {card.get('ruolo','')}</div>
              <div style="font-size:0.55rem;color:#444">ID: {card.get('id','')[:20]}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            if st.button("🗑️", key=f"del_{i}_{card.get('id','')[:8]}", help="Elimina"):
                cards_db["cards"] = [c for c in all_cards if c.get("id") != card.get("id")]
                save_cards_db(cards_db)
                st.session_state.cards_db = cards_db
                st.rerun()
        st.markdown("<hr style='border-color:#12122a;margin:3px 0'>", unsafe_allow_html=True)


def _render_coins_manager(rivals_data):
    st.markdown("### 🎁 Gestione Coins & XP")

    col1, col2 = st.columns(2)
    with col1:
        add_coins = st.number_input("Aggiungi MBT Coins", 0, 999999, 500, step=100, key="admin_add_coins")
        if st.button("➕ Aggiungi Coins", key="admin_btn_coins", use_container_width=True):
            rivals_data["mbt_coins"] += add_coins
            st.success(f"✅ +{add_coins:,} coins! Totale: {rivals_data['mbt_coins']:,}")
    with col2:
        add_xp = st.number_input("Aggiungi XP", 0, 99999, 100, step=50, key="admin_add_xp")
        if st.button("➕ Aggiungi XP", key="admin_btn_xp", use_container_width=True):
            rivals_data["player_xp"] += add_xp
            _check_level_up(rivals_data)
            st.success(f"✅ +{add_xp} XP! Livello: {rivals_data['player_level']}")

    st.markdown("---")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Coins", f"🪙 {rivals_data['mbt_coins']:,}")
    col_b.metric("Livello", f"LV.{rivals_data['player_level']}")
    col_c.metric("Vittorie", f"⚔️ {rivals_data['battle_wins']}")
    col_d.metric("Carte", f"🃏 {len(rivals_data.get('collection_cards',[]))}")

    st.markdown("---")
    if st.button("🔄 Reset Completo Rivals", key="admin_reset_rivals"):
        st.session_state.rivals_data = empty_rivals_state()
        save_rivals_data(st.session_state.rivals_data)
        st.success("✅ Dati Rivals resettati.")
        st.rerun()
