"""
mbt_rivals.py — MBT RIVALS v3.0
Card Battle System - versione completa e definitiva.
Migliorie rispetto all'originale:
- Forme geometriche SVG clip-path progressive per rarità (più rara = più particolare)
- OVR calcolato matematicamente da TUTTE le 6 statistiche (max 125)
- Nome piccolo sopra al COGNOME grande (separati)
- Badge source (DB/PACK/ATLETA) visivo CSS — zero HTML grezzo visibile
- Animazioni pack opening con cardFlipIn staggerato
- Arene animate con linee wave
- Stats slider 0-125 in Admin
- Password admin mantenuta
- Tutti i tab originali completi (collezione raggruppata per tier, descrizioni ruoli, etc.)
"""
import streamlit as st
import json
import random
import time
import base64
import os
import math
from pathlib import Path
from datetime import datetime

# ─── FILE PATHS ───────────────────────────────────────────────────────────────
RIVALS_FILE       = "mbt_rivals_data.json"
CARDS_DB_FILE     = "mbt_cards_db.json"
ASSETS_ICONS_DIR  = "assets/icons"


# ══════════════════════════════════════════════════════════════════════════════
# COSTANTI
# ══════════════════════════════════════════════════════════════════════════════

XP_PER_LEVEL = [
    0, 100, 250, 450, 700, 1000, 1350, 1750, 2200, 2700,
    3250, 3850, 4500, 5200, 5950, 6750, 7600, 8500, 9450, 10450
]

ROLES = [
    "SPIKER", "IRONBLOCKER", "DIFENSORE", "ACER",
    "SPECIALISTA", "TRAINER - Fisioterapista",
    "TRAINER - Mental Coach", "TRAINER - Scoutman"
]

ROLE_ICONS = {
    "SPIKER": "⚡", "IRONBLOCKER": "🛡️", "DIFENSORE": "🤿",
    "ACER": "🎯", "SPECIALISTA": "🔮",
    "TRAINER - Fisioterapista": "💊",
    "TRAINER - Mental Coach": "🧠",
    "TRAINER - Scoutman": "🔭"
}

ROLE_DESCRIPTIONS = {
    "SPIKER":                   "Super Attacco: Nocchino di Ghiaccio – attacco che non fallisce mai",
    "IRONBLOCKER":              "Fortezza di Titanio (Annulla danni) o Muro Corna (danno+difesa)",
    "DIFENSORE":                "Dig Classico / Sky Dive / Sabbia Mobile (recupera HP)",
    "ACER":                     "Jump Float Infuocato – danni critici doppi se vince il turno battuta",
    "SPECIALISTA":              "Seconda Intenzione – attacca nel turno difesa",
    "TRAINER - Fisioterapista": "Riduce consumo Stamina del 20%",
    "TRAINER - Mental Coach":   "Aumenta danni Super quando HP < 30%",
    "TRAINER - Scoutman":       "Vedi in anticipo la prima carta CPU",
}

CARD_TIERS = {
    "Bronzo Comune":    {"ovr_range": (40, 44),  "color": "#cd7f32", "rarity": 0},
    "Bronzo Raro":      {"ovr_range": (45, 49),  "color": "#e8902a", "rarity": 1},
    "Argento Comune":   {"ovr_range": (50, 54),  "color": "#c0c0c0", "rarity": 2},
    "Argento Raro":     {"ovr_range": (55, 59),  "color": "#d8d8d8", "rarity": 3},
    "Oro Comune":       {"ovr_range": (60, 64),  "color": "#ffd700", "rarity": 4},
    "Oro Raro":         {"ovr_range": (65, 69),  "color": "#ffec4a", "rarity": 5},
    "Eroe":             {"ovr_range": (70, 74),  "color": "#a855f7", "rarity": 6},
    "IF (In Form)":     {"ovr_range": (75, 79),  "color": "#c084fc", "rarity": 7},
    "Leggenda":         {"ovr_range": (80, 84),  "color": "#ffffff", "rarity": 8},
    "TOTY":             {"ovr_range": (85, 89),  "color": "#60a5fa", "rarity": 9},
    "TOTY Evoluto":     {"ovr_range": (90, 94),  "color": "#818cf8", "rarity": 10},
    "GOAT":             {"ovr_range": (95, 99),  "color": "#f97316", "rarity": 11},
    "ICON BASE":        {"ovr_range": (100, 104),"color": "#ffd700", "rarity": 12},
    "ICON EPICA":       {"ovr_range": (105, 109),"color": "#e040fb", "rarity": 13},
    "ICON LEGGENDARIA": {"ovr_range": (110, 114),"color": "#ffffff", "rarity": 14},
    "ICON TOTY":        {"ovr_range": (115, 119),"color": "#38bdf8", "rarity": 15},
    "ICON GOD":         {"ovr_range": (120, 125),"color": "#ff2200", "rarity": 16},
}

def get_tier_by_ovr(ovr):
    ovr = int(ovr)
    for name, td in CARD_TIERS.items():
        lo, hi = td["ovr_range"]
        if lo <= ovr <= hi:
            return name
    if ovr >= 120: return "ICON GOD"
    if ovr >= 115: return "ICON TOTY"
    if ovr >= 110: return "ICON LEGGENDARIA"
    if ovr >= 105: return "ICON EPICA"
    if ovr >= 100: return "ICON BASE"
    return "GOAT" if ovr >= 95 else "TOTY Evoluto"

def calcola_ovr_da_stats(atk, dif, ric, bat, mur, alz):
    """OVR matematico pesato, range 40-125."""
    pesi = {"atk": 1.4, "dif": 1.2, "bat": 1.1, "ric": 1.0, "mur": 0.9, "alz": 0.8}
    tot  = sum(pesi.values())
    raw  = (atk * pesi["atk"] + dif * pesi["dif"] + bat * pesi["bat"] +
            ric * pesi["ric"] + mur * pesi["mur"] + alz * pesi["alz"]) / tot
    return max(40, min(125, round(raw)))


PACKS = {
    "Base": {
        "price": 200, "css_class": "pack-base", "label_color": "#cd7f32",
        "emoji": "🟫",
        "description": "Perfetto per iniziare. Carte Bronzo, Argento e raramente Oro.",
        "weights": {
            "Bronzo Comune": 0.30, "Bronzo Raro": 0.25, "Argento Comune": 0.20,
            "Argento Raro": 0.12, "Oro Comune": 0.07, "Oro Raro": 0.04,
            "Eroe": 0.015, "IF (In Form)": 0.005
        }
    },
    "Epico": {
        "price": 500, "css_class": "pack-epico", "label_color": "#a855f7",
        "emoji": "💜",
        "description": "Alta probabilità di Oro ed Eroi. Chance di Leggenda e TOTY!",
        "weights": {
            "Oro Comune": 0.25, "Oro Raro": 0.22, "Eroe": 0.18,
            "IF (In Form)": 0.15, "Leggenda": 0.08, "TOTY": 0.04,
            "TOTY Evoluto": 0.02, "GOAT": 0.01,
            "ICON BASE": 0.008, "ICON EPICA": 0.002
        }
    },
    "Leggenda": {
        "price": 1200, "css_class": "pack-leggenda", "label_color": "#f97316",
        "emoji": "🔥",
        "description": "Solo carte di alto livello. Garantisce almeno una Leggenda!",
        "weights": {
            "Leggenda": 0.25, "TOTY": 0.20, "TOTY Evoluto": 0.18,
            "GOAT": 0.12, "ICON BASE": 0.10, "ICON EPICA": 0.07,
            "ICON LEGGENDARIA": 0.04, "ICON TOTY": 0.02, "ICON GOD": 0.01,
            "IF (In Form)": 0.01
        }
    },
}

ARENE = [
    {"min_level": 1,  "max_level": 2,  "name": "Arena Base",            "color": "#cd7f32", "icon": "🏟", "css": "arena-base"},
    {"min_level": 3,  "max_level": 4,  "name": "Arena Epica",           "color": "#a855f7", "icon": "⚡",  "css": "arena-epica"},
    {"min_level": 5,  "max_level": 6,  "name": "Arena Leggendaria",     "color": "#e2e8f0", "icon": "👑",  "css": "arena-legg"},
    {"min_level": 7,  "max_level": 8,  "name": "Arena TOTY",            "color": "#60a5fa", "icon": "🌟",  "css": "arena-toty"},
    {"min_level": 9,  "max_level": 10, "name": "Arena ICONA",           "color": "#ffd700", "icon": "🏆",  "css": "arena-icona"},
    {"min_level": 11, "max_level": 12, "name": "Arena ICONA EPICA",     "color": "#e040fb", "icon": "💫",  "css": "arena-icon-e"},
    {"min_level": 13, "max_level": 14, "name": "Arena ICONA LEGGEND.",  "color": "#f0f0f0", "icon": "✨",  "css": "arena-icon-l"},
    {"min_level": 15, "max_level": 16, "name": "Arena TOTY SUPREMA",    "color": "#38bdf8", "icon": "🔮",  "css": "arena-toty-s"},
    {"min_level": 17, "max_level": 18, "name": "Arena GOD MODE",        "color": "#ff3300", "icon": "🔥",  "css": "arena-god"},
    {"min_level": 19, "max_level": 20, "name": "Arena OMEGA",           "color": "#ff00ff", "icon": "⚜",  "css": "arena-omega"},
]

SPECIAL_MOVES = [
    {"id": "nocchino_ghiaccio",  "name": "Nocchino di Ghiaccio",   "role": "SPIKER",       "cost_coins": 300, "dmg": 35, "desc": "Attacco che non fallisce mai"},
    {"id": "fortezza_titanio",   "name": "Fortezza di Titanio",    "role": "IRONBLOCKER",  "cost_coins": 280, "dmg": 0,  "desc": "Annulla il prossimo attacco"},
    {"id": "muro_corna",         "name": "Muro Corna",             "role": "IRONBLOCKER",  "cost_coins": 320, "dmg": 20, "desc": "Danno e difesa simultanei"},
    {"id": "sky_dive",           "name": "Sky Dive",               "role": "DIFENSORE",    "cost_coins": 250, "dmg": 0,  "desc": "Recupera 20 HP"},
    {"id": "sabbia_mobile",      "name": "Sabbia Mobile",          "role": "DIFENSORE",    "cost_coins": 270, "dmg": 0,  "desc": "Recupera 30 HP"},
    {"id": "jump_float",         "name": "Jump Float Infuocato",   "role": "ACER",         "cost_coins": 350, "dmg": 40, "desc": "Danni critici doppi se primo turno"},
    {"id": "skyball",            "name": "SKYBALL",                "role": "ACER",         "cost_coins": 400, "dmg": 45, "desc": "Danno critico al morale avversario"},
    {"id": "seconda_intenzione", "name": "Seconda Intenzione",    "role": "SPECIALISTA",  "cost_coins": 380, "dmg": 30, "desc": "Attacca nel turno difesa"},
    {"id": "clutch_rise",        "name": "Clutch Rise",            "role": None,           "cost_coins": 500, "dmg": 50, "desc": "Danno x2 quando HP < 30%"},
    {"id": "final_spike",        "name": "FINAL SPIKE",            "role": None,           "cost_coins": 800, "dmg": 80, "desc": "MOSSA FINALE — danno devastante"},
]

SUPERPOWERS = [
    {"id": "iron_will",     "name": "Iron Will",     "desc": "Riduce danni subiti del 10% per livello", "max_level": 5, "cost_per_level": 200},
    {"id": "kill_shot",     "name": "Kill Shot",     "desc": "Aumenta ATK del 8% per livello",           "max_level": 5, "cost_per_level": 200},
    {"id": "stamina_boost", "name": "Stamina Boost", "desc": "Stamina si ricarica 15% più veloce/liv",   "max_level": 5, "cost_per_level": 150},
    {"id": "clutch_god",    "name": "Clutch God",    "desc": "HP critico (<30%): danno +20% per livello","max_level": 3, "cost_per_level": 350},
    {"id": "vision",        "name": "Vision",        "desc": "Vedi sempre la prossima mossa CPU (lv3+)", "max_level": 3, "cost_per_level": 300},
]


# ══════════════════════════════════════════════════════════════════════════════
# CSS COMPLETO
# ══════════════════════════════════════════════════════════════════════════════

RIVALS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&family=Exo+2:wght@300;700;900&display=swap');

:root {
  --rivals-bg: #080810;
  --rivals-card: #10101e;
  --rivals-border: #1e1e3a;
  --rivals-gold: #ffd700;
  --rivals-purple: #a855f7;
  --font-rivals: 'Orbitron', 'Rajdhani', sans-serif;
  --font-body: 'Exo 2', sans-serif;
}

/* ── Keyframes ──────────────────────────────────────────────────────── */
@keyframes goldShine      {0%{background-position:200% center}100%{background-position:-200% center}}
@keyframes shimmer        {0%{left:-100%}100%{left:200%}}
@keyframes shimmerSlide   {0%{transform:translateX(-150%)}100%{transform:translateX(250%)}}
@keyframes pulseGlow      {0%,100%{box-shadow:0 0 10px currentColor}50%{box-shadow:0 0 30px currentColor,0 0 60px currentColor}}
@keyframes floatUp        {0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes holographic    {0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes iconGodPulse   {0%,100%{box-shadow:0 0 20px #ff2200,0 0 40px #880000,inset 0 0 20px rgba(255,0,0,0.3)}50%{box-shadow:0 0 40px #ff4400,0 0 80px #ff0000,inset 0 0 40px rgba(255,80,0,0.5)}}
@keyframes lightningFlash {0%,90%,100%{opacity:0}92%,96%{opacity:1}94%,98%{opacity:.3}}
@keyframes fireFlicker    {0%,100%{transform:scaleY(1) translateX(0)}25%{transform:scaleY(1.1) translateX(-2px)}75%{transform:scaleY(0.95) translateX(2px)}}
@keyframes smokeRise      {0%{transform:translateY(0) scale(1);opacity:.6}100%{transform:translateY(-30px) scale(2);opacity:0}}
@keyframes goldDust       {0%{transform:translate(0,0) rotate(0deg);opacity:1}100%{transform:translate(var(--dx,20px),var(--dy,-30px)) rotate(720deg);opacity:0}}
@keyframes nebulaSwirl    {0%{transform:rotate(0deg) scale(1)}50%{transform:rotate(180deg) scale(1.1)}100%{transform:rotate(360deg) scale(1)}}
@keyframes explosion      {0%{transform:scale(0) rotate(0deg);opacity:1}60%{transform:scale(1.5) rotate(180deg);opacity:.8}100%{transform:scale(3) rotate(360deg);opacity:0}}
@keyframes cardFlip       {0%{transform:rotateY(0deg) scale(.8);opacity:0}40%{transform:rotateY(90deg) scale(1.1)}100%{transform:rotateY(0deg) scale(1);opacity:1}}
@keyframes cardFlipIn     {0%{transform:perspective(800px) rotateY(-90deg) scale(.8);opacity:0}60%{transform:perspective(800px) rotateY(8deg) scale(1.05)}100%{transform:perspective(800px) rotateY(0deg) scale(1);opacity:1}}
@keyframes packReveal     {0%{transform:rotateY(0deg);opacity:1}50%{transform:rotateY(90deg);opacity:.5}100%{transform:rotateY(0deg);opacity:1}}
@keyframes screenShake    {0%,100%{transform:translate(0,0)}10%{transform:translate(-8px,4px)}20%{transform:translate(8px,-4px)}30%{transform:translate(-6px,6px)}40%{transform:translate(6px,-2px)}50%{transform:translate(-4px,4px)}60%{transform:translate(4px,-4px)}}
@keyframes hpBar          {0%{width:var(--hp-from)}100%{width:var(--hp-to)}}
@keyframes battleHit      {0%{transform:translateX(0);filter:brightness(1)}20%{transform:translateX(-15px);filter:brightness(3) saturate(0)}40%{transform:translateX(10px);filter:brightness(1)}60%{transform:translateX(-5px)}100%{transform:translateX(0)}}
@keyframes godPulse       {0%,100%{box-shadow:0 0 20px #ff3300,0 0 50px #880000}50%{box-shadow:0 0 50px #ff5500,0 0 120px #ff0000,0 0 200px #440000}}
@keyframes holoPulse      {0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
@keyframes beamRotate     {0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
@keyframes particleDrift  {0%{transform:translate(0,0) scale(1);opacity:1}100%{transform:translate(var(--px,20px),var(--py,-30px)) scale(0);opacity:0}}
@keyframes energyOrb      {0%,100%{transform:translate(-50%,-50%) scale(1);opacity:.7}50%{transform:translate(-50%,-50%) scale(1.4);opacity:1}}
@keyframes waveFlow       {0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes screenTremor   {0%,100%{transform:translate(0,0) rotate(0)}10%{transform:translate(-10px,5px) rotate(-1deg)}20%{transform:translate(10px,-5px) rotate(1deg)}30%{transform:translate(-8px,8px) rotate(-.5deg)}40%{transform:translate(8px,-3px) rotate(.5deg)}50%{transform:translate(-4px,4px)}60%{transform:translate(4px,-4px)}}

/* ── Card wrapper ───────────────────────────────────────────────────── */
.mbt-card-wrap {
  position: relative; display: inline-block; cursor: pointer;
  transition: transform .3s cubic-bezier(.34,1.56,.64,1), filter .3s;
}
.mbt-card-wrap:hover {
  transform: translateY(-10px) scale(1.06) rotate(.4deg); z-index: 20; filter: brightness(1.15);
}
.mbt-card-wrap:active { transform: translateY(-3px) scale(.97); }
.mbt-card-wrap:hover .card-signature { opacity: 1 !important; }

/* ── Card base ──────────────────────────────────────────────────────── */
.mbt-card {
  position: relative; overflow: hidden;
  font-family: var(--font-rivals);
  display: flex; flex-direction: column;
  user-select: none;
}

/* ── Tier BG / Borders ──────────────────────────────────────────────── */
/* Bronzo */
.mbt-card.bronzo {
  background: linear-gradient(145deg, #3a2010, #7a4a28, #3a2010);
  border: 2px solid #cd7f32;
  box-shadow: 0 4px 15px rgba(205,127,50,.35);
}
/* Argento */
.mbt-card.argento {
  background: linear-gradient(145deg, #1a1a2a, #555, #1a1a2a);
  border: 2px solid #c0c0c0;
  box-shadow: 0 4px 20px rgba(192,192,192,.4);
}
/* Oro */
.mbt-card.oro {
  background: linear-gradient(145deg, #2a1e00, #5a4200, #2a1e00);
  border: 2px solid #ffd700;
  box-shadow: 0 6px 28px rgba(255,215,0,.5);
}
.mbt-card.oro::after {
  content: ''; position: absolute; top: 0; left: -100%; width: 60%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,215,0,.3), transparent);
  animation: shimmer 2.5s infinite;
}
/* Eroe */
.mbt-card.eroe {
  background: linear-gradient(145deg, #1a0040, #4a0090, #1a0040);
  border: 2px solid #a855f7;
  box-shadow: 0 8px 38px rgba(168,85,247,.7);
  animation: pulseGlow 2s infinite;
  color: var(--rivals-purple);
}
/* Leggenda */
.mbt-card.leggenda {
  background: linear-gradient(145deg, #0a0a14, #2a2a3a, #0a0a14);
  border: 2px solid #f0f0f0;
  box-shadow: 0 10px 50px rgba(240,240,240,.5), inset 0 0 20px rgba(255,255,255,.05);
}
/* TOTY */
.mbt-card.toty {
  background: linear-gradient(145deg, #000c24, #001660, #000c24);
  border: 3px solid #60a5fa;
  box-shadow: 0 10px 56px rgba(96,165,250,.8), 0 0 80px rgba(96,165,250,.3);
}
/* ICON BASE */
.mbt-card.icon-base {
  background: linear-gradient(145deg, #1a0f00, #3d2800, #1a0f00);
  border: 3px solid #ffd700;
  box-shadow: 0 0 30px #ffd700, 0 0 80px rgba(255,215,0,.5);
}
.mbt-card.icon-base::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(ellipse at 30% 20%, rgba(255,215,0,.15), transparent 70%);
  animation: nebulaSwirl 8s infinite linear;
}
/* ICON EPICA */
.mbt-card.icon-epica {
  background: linear-gradient(145deg, #1a0030, #4a0090, #1a0030);
  border: 3px solid #e040fb;
  box-shadow: 0 0 40px #e040fb, 0 0 100px rgba(224,64,251,.6);
}
.mbt-card.icon-epica::before {
  content: ''; position: absolute; inset: 0;
  background: conic-gradient(from 0deg, transparent 0deg, rgba(180,0,255,.2) 60deg, transparent 120deg);
  animation: nebulaSwirl 5s infinite linear;
}
/* ICON LEGGENDARIA */
.mbt-card.icon-leggendaria {
  background: linear-gradient(145deg, #0a0a10, #2a2a3a, #0a0a10);
  border: 3px solid #ffffff;
  box-shadow: 0 0 50px #fff, 0 0 120px rgba(255,255,255,.7), inset 0 0 40px rgba(255,255,255,.1);
}
.mbt-card.icon-leggendaria::before {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,.1) 50%, transparent 70%);
  background-size: 200% 200%;
  animation: holographic 3s infinite;
}
/* ICON TOTY */
.mbt-card.icon-toty {
  background: linear-gradient(145deg, #000c20, #001040, #000c20);
  border: 4px solid #38bdf8;
  box-shadow: 0 0 50px #38bdf8, 0 0 130px rgba(56,189,248,.7);
}
.mbt-card.icon-toty::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(circle at 50% 30%, rgba(56,189,248,.3), transparent 60%);
  animation: pulseGlow 2s infinite;
}
/* ICON GOD */
.mbt-card.icon-god {
  background: linear-gradient(145deg, #0a0000, #2a0000 30%, #000000 70%, #0a0000 100%);
  border: 4px solid #ff2200;
  box-shadow: 0 0 20px #ff2200, 0 0 40px #880000, 0 0 80px #440000;
  animation: iconGodPulse 1.5s infinite;
}
.mbt-card.icon-god::before {
  content: ''; position: absolute; inset: 0;
  background: repeating-linear-gradient(-45deg, transparent, transparent 10px, rgba(255,30,0,.05) 10px, rgba(255,30,0,.05) 11px);
  animation: lightningFlash 3s infinite;
}

/* ── Card photo / placeholder ───────────────────────────────────────── */
.mbt-card-photo             { width: 100%; height: 100px; object-fit: cover; object-position: top; display: block; position: relative; z-index: 1; }
.mbt-card-photo.sz-sm       { height: 70px; }
.mbt-card-photo.sz-lg       { height: 120px; }
.mbt-card-photo-placeholder { width: 100%; height: 100px; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; background: rgba(0,0,0,.3); position: relative; z-index: 1; }
.mbt-card-photo-placeholder.sz-sm { height: 70px; font-size: 1.8rem; }
.mbt-card-photo-placeholder.sz-lg { height: 120px; font-size: 3rem; }

/* ── OVR badge ──────────────────────────────────────────────────────── */
.mbt-card-ovr {
  position: absolute; top: 8px; left: 8px;
  font-family: var(--font-rivals); font-size: 1.4rem; font-weight: 900;
  line-height: 1; z-index: 15; text-shadow: 0 0 10px currentColor;
}
.mbt-card-ovr.sz-sm { font-size: 1rem; }
.mbt-card-ovr.sz-lg { font-size: 1.8rem; }

.mbt-card-tier-label {
  position: absolute; top: 8px; right: 8px;
  font-size: .45rem; letter-spacing: 1.5px; font-weight: 700; opacity: .8;
  text-transform: uppercase; z-index: 15; max-width: 50px; text-align: right;
  word-break: break-word;
}

/* ── Card text ──────────────────────────────────────────────────────── */
.mbt-card-nome-top {
  font-size: .36rem; letter-spacing: 1.5px; text-transform: uppercase; opacity: .7;
  text-align: center; padding: 3px 6px 0; position: relative; z-index: 2;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.mbt-card-cognome {
  font-family: var(--font-rivals); font-weight: 900; text-align: center;
  letter-spacing: .5px; text-transform: uppercase; padding: 1px 5px 2px;
  position: relative; z-index: 2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.mbt-card-cognome.sz-sm { font-size: .52rem; }
.mbt-card-cognome.sz-nm { font-size: .64rem; }
.mbt-card-cognome.sz-lg { font-size: .80rem; }
.mbt-card-role {
  font-size: .4rem; text-align: center; opacity: .75; letter-spacing: 1.5px;
  text-transform: uppercase; margin-bottom: 4px; position: relative; z-index: 2;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 4px;
}
.mbt-card-stats {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2px;
  padding: 4px 6px 6px; position: relative; z-index: 2;
}
.mbt-stat     { text-align: center; }
.mbt-stat-val { font-family: var(--font-rivals); font-size: .75rem; font-weight: 900; line-height: 1; }
.mbt-stat-lbl { font-size: .38rem; letter-spacing: 1px; text-transform: uppercase; opacity: .7; }

/* ── FX overlays ────────────────────────────────────────────────────── */
.shine-overlay {
  position: absolute; top: 0; left: 0; width: 40%; height: 100%;
  background: linear-gradient(105deg, transparent, rgba(255,255,255,.12), transparent);
  animation: shimmerSlide 2.5s 1.5s infinite; pointer-events: none; z-index: 8;
}
.holo-sheen {
  position: absolute; inset: 0; pointer-events: none; z-index: 7;
  background: linear-gradient(125deg, transparent 20%, rgba(255,255,255,.08) 30%, rgba(200,180,255,.12) 40%, rgba(100,200,255,.1) 50%, transparent 60%);
  background-size: 300% 300%; animation: holoPulse 4s ease infinite;
}
.beam-ring {
  position: absolute; inset: -3px; border-radius: inherit; pointer-events: none; z-index: 7;
  background: conic-gradient(from 0deg, transparent, rgba(96,165,250,.6), transparent, rgba(96,165,250,.6), transparent);
  animation: beamRotate 3s linear infinite;
}
.beam-ring.god {
  background: conic-gradient(from 0deg, transparent, rgba(255,34,0,.8), transparent, rgba(255,34,0,.8), transparent);
  animation-duration: 1.2s;
}
.eroe-bolt {
  position: absolute; right: 6px; top: 30%; font-size: .7rem;
  animation: lightningFlash 2s infinite; pointer-events: none; z-index: 10;
}
.nebula-orb {
  position: absolute; width: 60px; height: 60px; border-radius: 50%;
  pointer-events: none; z-index: 4;
  background: radial-gradient(circle, var(--orb-color, rgba(255,215,0,.3)), transparent 70%);
  top: 50%; left: 50%; transform: translate(-50%,-50%);
  animation: energyOrb 2.5s ease-in-out infinite;
}
.fire-bar {
  position: absolute; bottom: 0; left: 0; right: 0; height: 18px;
  pointer-events: none; z-index: 9;
  background: linear-gradient(0deg, rgba(255,34,0,.7), rgba(255,120,0,.3), transparent);
  animation: fireFlicker .6s ease-in-out infinite alternate;
}
.part-dot {
  position: absolute; width: 3px; height: 3px; border-radius: 50%;
  pointer-events: none; z-index: 11;
  animation: particleDrift 2s infinite both;
}
.god-cracks {
  position: absolute; inset: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 6; opacity: .7;
}
.card-signature {
  position: absolute; bottom: 70px; width: 100%; text-align: center;
  font-family: 'Brush Script MT', cursive; font-size: .8rem;
  opacity: 0; transition: opacity .3s; z-index: 15;
}

/* ── Pack visual ────────────────────────────────────────────────────── */
.pack-card {
  width: 100%; min-height: 200px; border-radius: 16px; cursor: pointer;
  transition: transform .4s, filter .3s; position: relative; overflow: hidden;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.pack-card:hover { transform: rotateY(10deg) scale(1.05); filter: brightness(1.1); }
.pack-base {
  background: linear-gradient(160deg, #2a1f0f, #5a3a0f, #2a1f0f);
  border: 3px solid #cd7f32; box-shadow: 0 8px 30px rgba(205,127,50,.5);
}
.pack-epico {
  background: linear-gradient(160deg, #1a0035, #4a0080, #1a0035);
  border: 3px solid #a855f7; box-shadow: 0 8px 40px rgba(168,85,247,.7);
}
.pack-leggenda {
  background: linear-gradient(160deg, #0a0000, #2a0000, #0a0000);
  border: 4px solid #f97316; box-shadow: 0 10px 60px rgba(249,115,22,.8), 0 0 120px rgba(249,115,22,.3);
}

/* ── Battle UI ──────────────────────────────────────────────────────── */
.hp-bar-container {
  height: 20px; background: #1a1a2a; border-radius: 10px; overflow: hidden;
  border: 1px solid var(--rivals-border);
}
.hp-bar-fill {
  height: 100%; border-radius: 10px; transition: width .5s ease;
  background: linear-gradient(90deg, #16a34a, #4ade80);
}
.hp-bar-fill.danger {
  background: linear-gradient(90deg, #dc2626, #ef4444);
  animation: pulseGlow 1s infinite;
}
.stamina-bar { height: 8px; background: #1a1a2a; border-radius: 4px; overflow: hidden; margin-top: 8px; }
.stamina-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #ffd700, #ffec4a); transition: width .3s; }
.battle-card-slot {
  border: 2px solid #1e1e3a; border-radius: 10px; padding: 10px;
  background: rgba(255,255,255,.02); min-height: 180px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: border-color .2s, background .2s;
}
.battle-card-slot.active { border-color: #ffd700; background: rgba(255,215,0,.05); }
.battle-card-slot:hover  { border-color: #60a5fa; background: rgba(96,165,250,.05); }
.battle-log {
  background: #05050f; border: 1px solid #1e1e3a; border-radius: 8px;
  padding: 10px; max-height: 200px; overflow-y: auto;
  font-family: var(--font-body); font-size: .75rem;
}
.battle-log div { padding: 2px 0; border-bottom: 1px solid #0e0e20; color: #bbc; }

/* ── Arena scenes ───────────────────────────────────────────────────── */
.arena-badge {
  border-radius: 10px; padding: 16px; text-align: center;
  cursor: pointer; transition: transform .2s, box-shadow .2s;
  position: relative; overflow: hidden;
}
.arena-badge:hover { transform: translateY(-4px); }
.arena-scene-full {
  border-radius: 16px; padding: 24px; text-align: center; position: relative;
  overflow: hidden; min-height: 140px; display: flex; flex-direction: column;
  align-items: center; justify-content: flex-end;
  cursor: pointer; transition: transform .25s, filter .25s;
}
.arena-scene-full:hover { transform: translateY(-5px); filter: brightness(1.1); }
.arena-glow { position: absolute; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.arena-line {
  position: absolute; height: 1px;
  background: linear-gradient(90deg, transparent, currentColor, transparent);
  opacity: .3; animation: waveFlow 4s ease infinite;
}
/* Arena variants */
.arena-base    { background: linear-gradient(135deg, #2a1f0f, #5a3a0f);    border: 2px solid #cd7f32; }
.arena-epica   { background: linear-gradient(135deg, #1a003a, #4a0080);    border: 2px solid #a855f7; }
.arena-legg    { background: linear-gradient(135deg, #0a0a0a, #2a2a2a);    border: 2px solid #fff; }
.arena-toty    { background: linear-gradient(135deg, #000820, #001855);    border: 2px solid #60a5fa; }
.arena-icona   { background: linear-gradient(135deg, #1a0f00, #3d2800);    border: 3px solid #ffd700; box-shadow: 0 0 30px rgba(255,215,0,.3); }
.arena-icon-e  { background: linear-gradient(135deg, #1a0030, #4a0090);    border: 3px solid #e040fb; box-shadow: 0 0 30px rgba(224,64,251,.3); }
.arena-icon-l  { background: linear-gradient(135deg, #111, #2a2a2a);       border: 3px solid #fff; box-shadow: 0 0 30px rgba(255,255,255,.3); }
.arena-toty-s  { background: linear-gradient(135deg, #000820, #001060);    border: 4px solid #38bdf8; box-shadow: 0 0 30px rgba(56,189,248,.5); }
.arena-god     { background: linear-gradient(135deg, #0a0000, #2a0000);    border: 4px solid #ff2200; box-shadow: 0 0 40px rgba(255,34,0,.6); animation: godPulse 2s infinite; }
.arena-omega   { background: #000; border: 4px solid transparent; box-shadow: 0 0 60px rgba(255,0,200,.8), 0 0 120px rgba(0,100,255,.6); }

/* ── Collection filter ──────────────────────────────────────────────── */
.collection-filter-btn {
  border: 1px solid; border-radius: 20px; padding: 4px 12px; cursor: pointer;
  font-size: .7rem; font-family: var(--font-rivals); transition: all .2s; background: transparent;
}
.collection-filter-btn.active  { background: var(--rivals-gold); border-color: var(--rivals-gold); color: #000; }
.collection-filter-btn:not(.active) { color: var(--rivals-gold); border-color: #555; }

/* ── Admin creator ──────────────────────────────────────────────────── */
.creator-preview-wrap {
  display: flex; justify-content: center; padding: 20px;
  background: radial-gradient(ellipse at center, rgba(255,215,0,.05), transparent 70%);
  border-radius: 12px; border: 1px dashed #333;
}

/* ── Rivals header title ────────────────────────────────────────────── */
.rivals-header-title {
  font-family: 'Orbitron', sans-serif; font-size: 1.6rem; font-weight: 900;
  background: linear-gradient(90deg, #ffd700, #ffec4a, #ffd700);
  background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  animation: goldShine 3s linear infinite;
}

/* ── Scrollbar ──────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #080810; }
::-webkit-scrollbar-thumb { background: #2a2a4a; border-radius: 2px; }
</style>
"""


# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════

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
        "player_level": 1, "player_xp": 0, "mbt_coins": 500,
        "trofei_rivals": 0,
        "collection": [],            # lista instance_id / id possedute
        "collection_cards": [],      # oggetti carta completi
        "active_team": [],           # max 5 instance_id
        "active_team_cards": [],     # oggetti carta del team
        "arena_unlocked": 1, "battle_wins": 0, "battle_losses": 0,
        "special_moves_learned": [], "superpowers": {}, "achievements": [],
    }

# ── Collezione helpers ──
def _iid(card): return card.get("instance_id") or card.get("id", "")

def _add_to_coll(rivals_data, card):
    iid = _iid(card)
    if iid and iid not in rivals_data.get("collection", []):
        rivals_data.setdefault("collection", []).append(iid)
        rivals_data.setdefault("collection_cards", []).append(card)

def _in_active_team(rivals_data, card):
    return _iid(card) in rivals_data.get("active_team", [])

def _add_to_active_team(rivals_data, card):
    iid = _iid(card)
    if len(rivals_data.get("active_team", [])) < 5 and iid not in rivals_data.get("active_team", []):
        rivals_data.setdefault("active_team", []).append(iid)
        rivals_data.setdefault("active_team_cards", []).append(card)

def _remove_from_active_team(rivals_data, card):
    iid = _iid(card)
    if iid in rivals_data.get("active_team", []):
        rivals_data["active_team"].remove(iid)
        rivals_data["active_team_cards"] = [
            c for c in rivals_data.get("active_team_cards", []) if _iid(c) != iid
        ]

def _get_active_team_cards(rivals_data):
    ids   = rivals_data.get("active_team", [])
    cards = rivals_data.get("collection_cards", [])
    return [c for tid in ids for c in cards if _iid(c) == tid]


# ══════════════════════════════════════════════════════════════════════════════
# CARD RENDERER — forme geometriche progressive, nome+cognome separati
# ══════════════════════════════════════════════════════════════════════════════

def _clip_path(rarity):
    """Forma geometrica progressivamente più complessa al crescere della rarità."""
    if rarity <= 1:
        return "polygon(0 0,100% 0,100% 92%,88% 100%,0 100%)"
    elif rarity <= 3:
        return "polygon(4% 0,96% 0,100% 4%,100% 96%,96% 100%,4% 100%,0 96%,0 4%)"
    elif rarity <= 5:
        return "polygon(8% 0,92% 0,100% 8%,100% 85%,92% 100%,8% 100%,0 85%,0 8%)"
    elif rarity <= 7:
        return "polygon(50% 0,96% 6%,100% 14%,100% 86%,96% 94%,50% 100%,4% 94%,0 86%,0 14%,4% 6%)"
    elif rarity <= 9:
        return "polygon(50% 0,100% 10%,100% 75%,50% 100%,0 75%,0 10%)"
    elif rarity <= 11:
        return "polygon(30% 0,70% 0,100% 30%,100% 70%,70% 100%,30% 100%,0 70%,0 30%)"
    elif rarity <= 13:
        return "polygon(50% 0,100% 30%,100% 70%,50% 100%,0 70%,0 30%)"
    elif rarity <= 15:
        return "polygon(50% 0,60% 38%,100% 38%,68% 62%,78% 100%,50% 78%,22% 100%,32% 62%,0 38%,40% 38%)"
    else:  # GOD — frammenti spezzati
        return "polygon(5% 0,40% 0,50% 8%,60% 0,95% 0,100% 5%,100% 40%,92% 50%,100% 60%,100% 95%,95% 100%,60% 100%,50% 92%,40% 100%,5% 100%,0 95%,0 60%,8% 50%,0 40%,0 5%)"


def render_card_html(card_data, size="normal", show_special_effects=True):
    """Genera HTML completo per una carta MBT. Nessun HTML grezzo visibile come testo."""
    ovr       = int(card_data.get("overall", 40))
    tier_name = get_tier_by_ovr(ovr)
    ti        = CARD_TIERS.get(tier_name, CARD_TIERS["Bronzo Comune"])
    color     = ti["color"]
    rarity    = ti["rarity"]
    # css_class per background/border
    css_rarity_map = {
        0: "bronzo", 1: "bronzo",
        2: "argento", 3: "argento",
        4: "oro", 5: "oro",
        6: "eroe", 7: "eroe",
        8: "leggenda", 9: "toty", 10: "toty", 11: "eroe",
        12: "icon-base", 13: "icon-epica", 14: "icon-leggendaria",
        15: "icon-toty", 16: "icon-god",
    }
    css_class = css_rarity_map.get(rarity, "bronzo")

    nome  = (card_data.get("nome") or "").strip()
    cogn  = (card_data.get("cognome") or "").strip() or nome
    role  = card_data.get("ruolo", "SPIKER")
    rico  = ROLE_ICONS.get(role, "⚡")
    foto_p = card_data.get("foto_path", "")

    atk = int(card_data.get("attacco", 40))
    dif = int(card_data.get("difesa",  40))
    bat = int(card_data.get("battuta", 40))

    width   = {"small": "110px", "normal": "140px", "large": "180px"}.get(size, "140px")
    ovr_sz  = {"small": " sz-sm", "large": " sz-lg"}.get(size, "")
    cogn_sz = {"small": " sz-sm", "large": " sz-lg"}.get(size, " sz-nm")
    ph_sz   = {"small": " sz-sm", "large": " sz-lg"}.get(size, "")
    clip    = _clip_path(rarity)

    tier_short = tier_name.replace("ICON ", "").replace(" Comune","").replace(" Raro","").replace(" Evoluto","")[:7]

    # Foto
    if foto_p and os.path.exists(str(foto_p)):
        try:
            with open(foto_p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            ext  = str(foto_p).split(".")[-1].lower()
            mime = "image/png" if ext == "png" else "image/jpeg"
            photo = '<img class="mbt-card-photo{ph_sz}" src="data:{mime};base64,{b64}" alt="">'.format(
                ph_sz=ph_sz, mime=mime, b64=b64)
        except Exception:
            photo = '<div class="mbt-card-photo-placeholder{ph_sz}">{rico}</div>'.format(ph_sz=ph_sz, rico=rico)
    else:
        photo = '<div class="mbt-card-photo-placeholder{ph_sz}">{rico}</div>'.format(ph_sz=ph_sz, rico=rico)

    # FX layers
    fx = ""
    if rarity >= 4:
        fx += '<div class="shine-overlay"></div>'
    if 8 <= rarity <= 11:
        fx += '<div class="holo-sheen"></div>'
    if rarity >= 9:
        gclass = " god" if rarity >= 16 else ""
        fx += '<div class="beam-ring{g}"></div>'.format(g=gclass)
    if rarity in (6, 7):
        fx += '<div class="eroe-bolt">&#9889;</div>'
    if rarity >= 12:
        orb_map = {12: "rgba(255,215,0,.35)", 13: "rgba(224,64,251,.4)",
                   14: "rgba(255,255,255,.3)", 15: "rgba(56,189,248,.4)", 16: "rgba(255,51,0,.5)"}
        oc = orb_map.get(rarity, "rgba(255,215,0,.3)")
        fx += '<div class="nebula-orb" style="--orb-color:{oc}"></div>'.format(oc=oc)
        if show_special_effects:
            for i in range(8):
                dx   = random.randint(-30, 30)
                dy   = random.randint(-50, -10)
                dl   = random.uniform(0, 2)
                dur  = random.uniform(1.5, 3)
                top  = random.randint(20, 80)
                left = random.randint(10, 90)
                fx += (
                    '<div class="part-dot" style="--px:{dx}px;--py:{dy}px;'
                    'background:{color};top:{top}%;left:{left}%;'
                    'animation-duration:{dur:.1f}s;animation-delay:{dl:.1f}s"></div>'
                ).format(dx=dx, dy=dy, color=color, top=top, left=left, dur=dur, dl=dl)
    if rarity >= 16:
        fx += '<div class="fire-bar"></div>'
        fx += (
            '<svg class="god-cracks" viewBox="0 0 140 220" fill="none">'
            '<polyline points="70,0 60,40 80,50 55,110" stroke="#ff5500" stroke-width="1.5" stroke-dasharray="6,3" opacity=".6"/>'
            '<polyline points="140,80 110,90 125,130 90,150" stroke="#ff3300" stroke-width="1" stroke-dasharray="5,4" opacity=".5"/>'
            '<polyline points="0,140 30,130 20,170 50,160" stroke="#ff4400" stroke-width="1" stroke-dasharray="4,3" opacity=".55"/>'
            '<circle cx="70" cy="50" r="2" fill="#ff5500" opacity=".8"/>'
            '<circle cx="110" cy="130" r="2" fill="#ff3300" opacity=".7"/>'
            '</svg>'
        )

    # Firma hover per ICON+
    sig = ""
    if rarity >= 12:
        sig = (
            '<div class="card-signature" style="color:{color};text-shadow:0 0 10px {color}">'
            '&#10022; {nome} &#10022;</div>'
        ).format(color=color, nome=nome)

    return (
        '<div class="mbt-card-wrap" style="width:{w}">'
        '<div class="mbt-card {css}" style="width:{w};clip-path:{clip}">'
        '<div class="mbt-card-ovr{ovr_sz}" style="color:{color}">{ovr}</div>'
        '<div class="mbt-card-tier-label" style="color:{color}">{tier_short}</div>'
        '{photo}'
        '<div class="mbt-card-nome-top" style="color:{color}">{nome}</div>'
        '<div class="mbt-card-cognome{cogn_sz}" style="color:{color}">{cogn}</div>'
        '<div class="mbt-card-role" style="color:{color}">{rico} {role}</div>'
        '<div style="height:1px;background:rgba(255,255,255,.12);margin:0 6px 3px"></div>'
        '<div class="mbt-card-stats">'
        '<div class="mbt-stat"><div class="mbt-stat-val" style="color:{color}">{atk}</div><div class="mbt-stat-lbl">ATK</div></div>'
        '<div class="mbt-stat"><div class="mbt-stat-val" style="color:{color}">{dif}</div><div class="mbt-stat-lbl">DEF</div></div>'
        '<div class="mbt-stat"><div class="mbt-stat-val" style="color:{color}">{bat}</div><div class="mbt-stat-lbl">BAT</div></div>'
        '</div>'
        '{fx}{sig}'
        '</div></div>'
    ).format(
        w=width, css=css_class, clip=clip, color=color, ovr_sz=ovr_sz, ovr=ovr,
        tier_short=tier_short, photo=photo, nome=nome, cogn_sz=cogn_sz,
        cogn=cogn.upper(), rico=rico, role=role, atk=atk, dif=dif, bat=bat,
        fx=fx, sig=sig
    )


# ══════════════════════════════════════════════════════════════════════════════
# PACK
# ══════════════════════════════════════════════════════════════════════════════

def draw_cards_from_pack(pack_name, cards_db):
    pack_info = PACKS[pack_name]
    weights   = pack_info["weights"]
    tiers     = list(weights.keys())
    probs     = [v / sum(weights.values()) for v in weights.values()]
    drawn     = []
    all_cards = cards_db.get("cards", [])

    for _ in range(6):
        chosen = random.choices(tiers, weights=probs, k=1)[0]
        matching = [c for c in all_cards if get_tier_by_ovr(c.get("overall", 40)) == chosen]
        if matching:
            card = random.choice(matching).copy()
        else:
            td  = CARD_TIERS.get(chosen, CARD_TIERS["Bronzo Comune"])
            lo, hi = td["ovr_range"]
            ovr = random.randint(lo, hi)
            card = {
                "id": "gen_{r}".format(r=random.randint(100000, 999999)),
                "nome":    random.choice(["Marco","Luca","Andrea","Fabio","Simone","Giulio","Matteo","Riccardo"]),
                "cognome": random.choice(["Rossi","Bianchi","Ferrari","Conti","Esposito","Costa","Ricci","Serra"]),
                "overall": ovr, "tier": chosen,
                "ruolo":    random.choice(list(ROLE_ICONS.keys())[:5]),
                "attacco":   max(40, ovr - random.randint(0, 15)),
                "difesa":    max(40, ovr - random.randint(0, 15)),
                "muro":      max(40, ovr - random.randint(0, 20)),
                "ricezione": max(40, ovr - random.randint(0, 20)),
                "battuta":   max(40, ovr - random.randint(0, 18)),
                "alzata":    max(40, ovr - random.randint(0, 20)),
                "foto_path": "", "generated": True,
            }
        card["instance_id"] = "inst_{r}".format(r=random.randint(1000000, 9999999))
        card["source"]      = "pack"
        card["pack_name"]   = pack_name
        drawn.append(card)
    return drawn


def render_pack_opening_animation(drawn_cards, pack_name):
    """Mostra le 6 carte con animazione staggerata cardFlipIn."""
    sorted_cards = sorted(
        drawn_cards,
        key=lambda c: CARD_TIERS.get(get_tier_by_ovr(c.get("overall", 40)), {}).get("rarity", 0)
    )

    st.markdown("### 🎁 Apertura Pacchetto **{p}** — Hai trovato:".format(p=pack_name))
    cols = st.columns(6)
    for i, card in enumerate(drawn_cards):
        tier   = get_tier_by_ovr(card.get("overall", 40))
        rarity = CARD_TIERS.get(tier, {}).get("rarity", 0)
        color  = CARD_TIERS.get(tier, {}).get("color", "#fff")
        delay  = "{d:.2f}s".format(d=i * 0.15)

        with cols[i]:
            if rarity >= 12:
                lbl = '<div style="text-align:center;font-size:.6rem;color:{c};margin-top:4px;font-weight:700;letter-spacing:2px">&#9889; {t} &#9889;</div>'.format(c=color, t=tier)
            elif rarity >= 8:
                lbl = '<div style="text-align:center;font-size:.55rem;color:{c};margin-top:4px">&#10022; {t} &#10022;</div>'.format(c=color, t=tier)
            else:
                lbl = '<div style="text-align:center;font-size:.5rem;color:#777;margin-top:4px">{t}</div>'.format(t=tier)

            st.markdown(
                '<div style="animation:cardFlipIn .7s {delay} cubic-bezier(.34,1.56,.64,1) both">'
                '{card_html}</div>{lbl}'.format(
                    delay=delay,
                    card_html=render_card_html(card, size="small"),
                    lbl=lbl),
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BATTLE ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def init_battle_state(player_cards, cpu_level=1):
    def make_fighter(card, is_cpu=False):
        ovr = card.get("overall", 40)
        hp  = 80 + ovr * 2
        if is_cpu:
            hp = int(hp * (0.9 + cpu_level * 0.1))
        return {"card": card, "hp": hp, "max_hp": hp, "stamina": 100, "shield": 0, "status": None}

    cpu_ovr_base = 40 + cpu_level * 4
    cpu_cards    = []
    for _ in range(3):
        ovr = min(99, cpu_ovr_base + random.randint(-5, 10))
        cpu_cards.append({
            "nome":    random.choice(["Volkov","Storm","Ace","Blade","Vector","Nexus","Cipher","Titan"]),
            "overall": ovr, "ruolo": random.choice(list(ROLE_ICONS.keys())[:5]),
            "attacco": max(40, ovr - random.randint(0, 10)),
            "difesa":  max(40, ovr - random.randint(0, 10)),
            "battuta": max(40, ovr - random.randint(0, 10)),
            "foto_path": "",
        })

    return {
        "player_fighters":   [make_fighter(c) for c in player_cards[:3]],
        "cpu_fighters":      [make_fighter(c, is_cpu=True) for c in cpu_cards],
        "player_active_idx": 0, "cpu_active_idx": 0,
        "turn": 0, "phase": "battle",
        "log": [], "stamina_charges": 0,
        "start_time": time.time(), "time_limit": 300,
    }


def calculate_damage(attacker_card, defender_card, move_type="attack", superpowers=None):
    atk  = attacker_card.get("attacco", 40)
    def_ = defender_card.get("difesa",  40)
    base = max(5, (atk - def_ * 0.6) * 0.4 + random.randint(3, 12))
    if move_type == "special": base *= 1.8
    elif move_type == "super": base *= 2.5
    if superpowers:
        base *= (1 + superpowers.get("kill_shot", 0) * 0.08)
    return max(5, int(base))


def cpu_choose_action(cpu_fighter, player_fighter, turn):
    hp_ratio = cpu_fighter["hp"] / max(cpu_fighter["max_hp"], 1)
    actions  = ["attack", "attack", "attack", "defend"]
    if hp_ratio < 0.3:
        actions = ["attack", "attack", "special", "defend"]
    if cpu_fighter["stamina"] >= 50 and random.random() < 0.3:
        return "special"
    return random.choice(actions)


def process_battle_action(battle_state, action, rivals_data):
    p_idx     = battle_state["player_active_idx"]
    c_idx     = battle_state["cpu_active_idx"]
    p_fighter = battle_state["player_fighters"][p_idx]
    c_fighter = battle_state["cpu_fighters"][c_idx]
    log       = battle_state["log"]
    sp        = rivals_data.get("superpowers", {})
    pn        = p_fighter["card"].get("nome", "Player")
    cn        = c_fighter["card"].get("nome", "CPU")

    if action == "attack":
        dmg = calculate_damage(p_fighter["card"], c_fighter["card"], "attack", sp)
        c_fighter["hp"] = max(0, c_fighter["hp"] - dmg)
        p_fighter["stamina"] = min(100, p_fighter["stamina"] + 10)
        battle_state["stamina_charges"] += 1
        log.append("⚡ {pn} attacca → {dmg} danni! (HP CPU: {hp})".format(pn=pn, dmg=dmg, hp=c_fighter["hp"]))

    elif action == "special":
        if p_fighter["stamina"] >= 40:
            dmg = calculate_damage(p_fighter["card"], c_fighter["card"], "special", sp)
            c_fighter["hp"] = max(0, c_fighter["hp"] - dmg)
            p_fighter["stamina"] -= 40
            log.append("🔥 {pn} SUPER ATTACCO → {dmg} danni! BOOM!".format(pn=pn, dmg=dmg))
        else:
            log.append("⚠️ Stamina insufficiente per Super Attacco!")

    elif action == "defend":
        p_fighter["shield"]  = 30
        p_fighter["stamina"] = min(100, p_fighter["stamina"] + 20)
        log.append("🛡️ {pn} si difende! Scudo attivato.".format(pn=pn))

    elif action == "final":
        if battle_state["stamina_charges"] >= 10:
            dmg = calculate_damage(p_fighter["card"], c_fighter["card"], "super", sp)
            c_fighter["hp"] = max(0, c_fighter["hp"] - dmg)
            battle_state["stamina_charges"] = 0
            log.append("💥 MOSSA FINALE! {pn} → {dmg} danni DEVASTANTI!".format(pn=pn, dmg=dmg))
        else:
            log.append("⚠️ Carica la Stamina per la Mossa Finale (10 attacchi)!")

    # Controlla HP CPU
    if c_fighter["hp"] <= 0:
        nxt = c_idx + 1
        if nxt < len(battle_state["cpu_fighters"]):
            battle_state["cpu_active_idx"] = nxt
            log.append("💀 {cn} eliminato! Prossimo avversario!".format(cn=cn))
        else:
            battle_state["phase"] = "win"
            log.append("🏆 HAI VINTO LA PARTITA!")
            battle_state["log"] = log[-20:]
            return

    # Turno CPU
    if battle_state["phase"] == "battle":
        cpu_action = cpu_choose_action(c_fighter, p_fighter, battle_state["turn"])
        if cpu_action == "attack":
            cpu_dmg = calculate_damage(c_fighter["card"], p_fighter["card"], "attack")
            if p_fighter["shield"] > 0:
                cpu_dmg = max(0, cpu_dmg - p_fighter["shield"])
                p_fighter["shield"] = 0
                log.append("🛡️ Scudo! {cn} attacca → {dmg} danni dopo difesa".format(cn=cn, dmg=cpu_dmg))
            else:
                log.append("🤖 {cn} attacca → {dmg} danni!".format(cn=cn, dmg=cpu_dmg))
            p_fighter["hp"] = max(0, p_fighter["hp"] - cpu_dmg)
        elif cpu_action == "special":
            cpu_dmg = calculate_damage(c_fighter["card"], p_fighter["card"], "special")
            log.append("💫 {cn} SUPER MOSSA → {dmg} danni!".format(cn=cn, dmg=cpu_dmg))
            p_fighter["hp"] = max(0, p_fighter["hp"] - cpu_dmg)
            c_fighter["stamina"] = max(0, c_fighter["stamina"] - 40)
        elif cpu_action == "defend":
            c_fighter["shield"] = 25
            log.append("🤖 {cn} si difende!".format(cn=cn))

    # Controlla HP player
    if p_fighter["hp"] <= 0:
        nxt = p_idx + 1
        if nxt < len(battle_state["player_fighters"]):
            battle_state["player_active_idx"] = nxt
            log.append("💔 {pn} KO! Prossima carta!".format(pn=pn))
        else:
            battle_state["phase"] = "lose"
            log.append("💀 HAI PERSO! Le tue carte sono cadute tutte!")

    battle_state["turn"] += 1
    if len(log) > 20:
        battle_state["log"] = log[-20:]


def _check_level_up(rivals_data):
    lv = rivals_data["player_level"]
    if lv >= 20:
        return
    xp_needed = XP_PER_LEVEL[lv]
    if rivals_data["player_xp"] >= xp_needed:
        rivals_data["player_level"] += 1
        rivals_data["trofei_rivals"] += 10
        rivals_data["arena_unlocked"] = rivals_data["player_level"]


# ══════════════════════════════════════════════════════════════════════════════
# SYNC OVR
# ══════════════════════════════════════════════════════════════════════════════

def _sync_ovr_from_tournament(state, cards_db):
    try:
        from data_manager import calcola_overall_fifa
        for atleta in state.get("atleti", []):
            ovr = calcola_overall_fifa(atleta)
            for card in cards_db.get("cards", []):
                if card.get("atleta_id") == atleta["id"]:
                    card["overall"] = ovr
                    s = atleta["stats"]
                    for k in ["attacco","difesa","muro","ricezione","battuta","alzata"]:
                        card[k] = s.get(k, card.get(k, 40))
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def render_mbt_rivals(state):
    st.markdown(RIVALS_CSS, unsafe_allow_html=True)

    rivals_data = st.session_state.get("rivals_data")
    if rivals_data is None:
        rivals_data = load_rivals_data()
        st.session_state.rivals_data = rivals_data

    cards_db = st.session_state.get("cards_db")
    if cards_db is None:
        cards_db = load_cards_db()
        st.session_state.cards_db = cards_db

    _sync_ovr_from_tournament(state, cards_db)

    level       = rivals_data["player_level"]
    xp          = rivals_data["player_xp"]
    coins       = rivals_data["mbt_coins"]
    xp_needed   = XP_PER_LEVEL[min(level, 19)] if level < 20 else 99999
    xp_pct      = min(100, int(xp / max(xp_needed, 1) * 100))
    curr_arena  = next((a for a in ARENE if a["min_level"] <= level <= a["max_level"]), ARENE[0])
    ncoll       = len(rivals_data.get("collection_cards", []))

    st.markdown("""
    <div style="background:linear-gradient(135deg,#080810,#10101e,#080810);
        border:2px solid #1e1e3a;border-radius:16px;padding:16px 24px;margin-bottom:20px">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
        <div>
          <div class="rivals-header-title">&#9889; MBT RIVALS</div>
          <div style="font-size:.75rem;color:#444;letter-spacing:3px;margin-top:2px">CARD BATTLE SYSTEM</div>
        </div>
        <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:center">
          <div style="text-align:center">
            <div style="font-family:'Orbitron',sans-serif;font-size:1.2rem;font-weight:900;color:#ffd700">LV.{lv}</div>
            <div style="width:80px;height:6px;background:#1a1a2a;border-radius:3px;margin:4px auto;overflow:hidden">
              <div style="width:{xp_pct}%;height:100%;background:linear-gradient(90deg,#ffd700,#ffec4a);border-radius:3px;transition:width .5s"></div>
            </div>
            <div style="font-size:.5rem;color:#555">{xp}/{xpn} XP</div>
          </div>
          <div style="text-align:center">
            <div style="font-family:'Orbitron',sans-serif;font-size:1.2rem;font-weight:900;color:#ffd700">&#127890; {coins}</div>
            <div style="font-size:.6rem;color:#555">MBT COINS</div>
          </div>
          <div style="text-align:center">
            <div style="font-family:'Orbitron',sans-serif;font-size:1.2rem;font-weight:900;color:{ac}">{ai}</div>
            <div style="font-size:.6rem;color:{ac}">{an}</div>
          </div>
          <div style="text-align:center">
            <div style="font-family:'Orbitron',sans-serif;font-size:1.2rem;font-weight:900;color:#4ade80">{bw}W</div>
            <div style="font-size:.6rem;color:#555">VITTORIE</div>
          </div>
          <div style="text-align:center">
            <div style="font-family:'Orbitron',sans-serif;font-size:1.1rem;color:#a855f7">&#127183; {nc}</div>
            <div style="font-size:.6rem;color:#555">CARTE</div>
          </div>
        </div>
      </div>
    </div>""".format(
        lv=level, xp_pct=xp_pct, xp=xp, xpn=xp_needed,
        coins="{:,}".format(coins), ac=curr_arena["color"],
        ai=curr_arena["icon"], an=curr_arena["name"],
        bw=rivals_data["battle_wins"], nc=ncoll),
        unsafe_allow_html=True)

    tabs = st.tabs(["⚔️ MBT RIVALS","🃏 Collezione","🛒 Negozio","🏟️ Arene","💪 Poteri","⚙️ Admin"])
    with tabs[0]: _render_battle_tab(rivals_data, cards_db, state)
    with tabs[1]: _render_collection_tab(rivals_data, cards_db, state)
    with tabs[2]: _render_shop_tab(rivals_data, cards_db)
    with tabs[3]: _render_arenas_tab(rivals_data)
    with tabs[4]: _render_powers_tab(rivals_data)
    with tabs[5]: _render_admin_tab(state, cards_db, rivals_data)

    save_rivals_data(rivals_data)
    save_cards_db(cards_db)


# ══════════════════════════════════════════════════════════════════════════════
# BATTLE TAB
# ══════════════════════════════════════════════════════════════════════════════

def _render_battle_tab(rivals_data, cards_db, state):
    st.markdown("## ⚔️ MBT RIVALS — Battaglia vs CPU")
    battle_state = st.session_state.get("battle_state")

    if battle_state is None:
        team_cards = _get_active_team_cards(rivals_data)
        st.markdown("### 🏆 La Tua Squadra Attiva")
        if not team_cards:
            st.warning("⚠️ Nessuna carta nella squadra attiva! Vai in **Collezione** → aggiungi fino a 5 carte al team.")
            return

        cols = st.columns(min(5, len(team_cards)))
        for i, card in enumerate(team_cards[:5]):
            with cols[i]:
                st.markdown(render_card_html(card, size="small"), unsafe_allow_html=True)

        st.markdown("---")
        level        = rivals_data["player_level"]
        curr_arena   = next((a for a in ARENE if a["min_level"] <= level <= a["max_level"]), ARENE[0])
        coins_reward = 50 + level * 10
        xp_reward    = 30 + level * 5
        trofei_reward= 2  + level

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                '<div class="arena-scene-full {css}">'
                '<div class="arena-glow">'
                '<div class="arena-line" style="top:35%;width:75%;left:12%;color:{col};animation-delay:.4s"></div>'
                '</div>'
                '<div style="position:relative;z-index:2;font-size:2rem">{icon}</div>'
                '<div style="position:relative;z-index:2;font-family:Orbitron,sans-serif;color:{col};font-size:.9rem;font-weight:700">{name}</div>'
                '</div>'.format(css=curr_arena["css"], col=curr_arena["color"],
                               icon=curr_arena["icon"], name=curr_arena["name"]),
                unsafe_allow_html=True)
        with col2:
            st.markdown(
                '<div style="background:#10101e;border:1px solid #1e1e3a;border-radius:10px;padding:16px;text-align:center;min-height:110px;display:flex;flex-direction:column;align-items:center;justify-content:center">'
                '<div style="font-size:1.5rem">&#129302;</div>'
                '<div style="font-family:Orbitron,sans-serif;color:#dc2626;font-weight:700">CPU LV.{lv}</div>'
                '<div style="font-size:.65rem;color:#555">Difficoltà proporzionale</div>'
                '</div>'.format(lv=level),
                unsafe_allow_html=True)
        with col3:
            st.markdown(
                '<div style="background:#10101e;border:1px solid #16a34a;border-radius:10px;padding:16px;text-align:center;min-height:110px;display:flex;flex-direction:column;align-items:center;justify-content:center">'
                '<div style="font-size:.7rem;color:#4ade80;font-family:Orbitron,sans-serif;font-weight:700;margin-bottom:6px">RICOMPENSE</div>'
                '<div style="font-size:.7rem;color:#ffd700">&#127890; +{cr} Coins</div>'
                '<div style="font-size:.7rem;color:#60a5fa">&#11088; +{xr} XP</div>'
                '<div style="font-size:.7rem;color:#a855f7">&#127942; +{tr} Trofei</div>'
                '</div>'.format(cr=coins_reward, xr=xp_reward, tr=trofei_reward),
                unsafe_allow_html=True)

        st.markdown("")
        if st.button("⚔️ INIZIA BATTAGLIA!", use_container_width=True, type="primary"):
            st.session_state.battle_state = init_battle_state(team_cards[:3], cpu_level=level)
            st.rerun()
    else:
        _render_active_battle(battle_state, rivals_data, cards_db)


def _render_active_battle(battle_state, rivals_data, cards_db):
    phase = battle_state["phase"]

    if phase == "win":
        level       = rivals_data["player_level"]
        xp_gain     = 30 + level * 5
        coins_gain  = 50 + level * 10
        trofei_gain = 2  + level
        rivals_data["player_xp"]      += xp_gain
        rivals_data["mbt_coins"]      += coins_gain
        rivals_data["trofei_rivals"]  += trofei_gain
        rivals_data["battle_wins"]    += 1
        _check_level_up(rivals_data)
        st.markdown(
            '<div style="text-align:center;padding:30px;background:linear-gradient(135deg,#001a00,#003300);'
            'border:3px solid #16a34a;border-radius:16px;animation:pulseGlow 1s infinite">'
            '<div style="font-size:3rem">&#127942;</div>'
            '<div style="font-family:Orbitron,sans-serif;font-size:2rem;font-weight:900;color:#4ade80">VITTORIA!</div>'
            '</div>',
            unsafe_allow_html=True)
        st.success("🎉 +{xg} XP | +{cg} Coins | +{tg} Trofei".format(xg=xp_gain, cg=coins_gain, tg=trofei_gain))
        if st.button("🔄 Nuova Partita", use_container_width=True, type="primary"):
            st.session_state.battle_state = None; st.rerun()
        return

    if phase == "lose":
        rivals_data["battle_losses"] += 1
        rivals_data["player_xp"]    += 10
        rivals_data["mbt_coins"]    += 20
        _check_level_up(rivals_data)
        st.markdown(
            '<div style="text-align:center;padding:30px;background:linear-gradient(135deg,#1a0000,#330000);'
            'border:3px solid #dc2626;border-radius:16px">'
            '<div style="font-size:3rem">&#128128;</div>'
            '<div style="font-family:Orbitron,sans-serif;font-size:2rem;font-weight:900;color:#ef4444">SCONFITTA</div>'
            '</div>',
            unsafe_allow_html=True)
        st.info("+10 XP per aver combattuto | +20 Coins")
        if st.button("🔄 Riprova", use_container_width=True):
            st.session_state.battle_state = None; st.rerun()
        return

    p_idx    = battle_state["player_active_idx"]
    c_idx    = battle_state["cpu_active_idx"]
    p_fighter= battle_state["player_fighters"][p_idx]
    c_fighter= battle_state["cpu_fighters"][c_idx]

    elapsed   = time.time() - battle_state["start_time"]
    remaining = max(0, battle_state["time_limit"] - elapsed)
    min_r     = int(remaining // 60)
    sec_r     = int(remaining % 60)
    if remaining <= 0:
        battle_state["phase"] = "lose"; st.rerun()

    col_p, col_mid, col_c = st.columns([2, 1, 2])

    with col_p:
        st.markdown("**⚡ {n}**".format(n=p_fighter["card"].get("nome","Player")))
        hp_pct = max(0, int(p_fighter["hp"] / max(p_fighter["max_hp"],1) * 100))
        hp_cls = "danger" if hp_pct < 30 else ""
        st.markdown(
            '<div class="hp-bar-container"><div class="hp-bar-fill {c}" style="width:{p}%"></div></div>'
            '<div style="font-size:.7rem;color:#777;margin-top:2px">HP: {hp}/{mhp}</div>'
            '<div class="stamina-bar"><div class="stamina-fill" style="width:{sta}%"></div></div>'
            '<div style="font-size:.6rem;color:#777;margin-top:1px">STAMINA: {sta}%</div>'.format(
                c=hp_cls, p=hp_pct, hp=p_fighter["hp"], mhp=p_fighter["max_hp"],
                sta=int(p_fighter["stamina"])),
            unsafe_allow_html=True)
        st.markdown(render_card_html(p_fighter["card"], size="small", show_special_effects=False), unsafe_allow_html=True)

    with col_mid:
        st.markdown(
            '<div style="text-align:center;padding:20px 0">'
            '<div style="font-family:Orbitron,sans-serif;font-size:1.5rem;font-weight:900;color:#dc2626">VS</div>'
            '<div style="font-size:.7rem;color:#555;margin-top:8px">&#9201;&#65039; {mr:02d}:{sr:02d}</div>'
            '<div style="font-size:.65rem;color:#ffd700;margin-top:4px">Turno {turn}</div>'
            '<div style="font-size:.6rem;color:#555;margin-top:8px">Carica: {sc}/10</div>'
            '</div>'.format(mr=min_r, sr=sec_r, turn=battle_state["turn"], sc=battle_state["stamina_charges"]),
            unsafe_allow_html=True)

    with col_c:
        st.markdown("**🤖 {n}**".format(n=c_fighter["card"].get("nome","CPU")))
        chp_pct = max(0, int(c_fighter["hp"] / max(c_fighter["max_hp"],1) * 100))
        st.markdown(
            '<div class="hp-bar-container">'
            '<div style="width:{p}%;height:100%;background:linear-gradient(90deg,#dc2626,#ef4444);border-radius:10px;transition:width .5s"></div>'
            '</div>'
            '<div style="font-size:.7rem;color:#777;margin-top:2px">HP: {hp}/{mhp}</div>'.format(
                p=chp_pct, hp=c_fighter["hp"], mhp=c_fighter["max_hp"]),
            unsafe_allow_html=True)
        st.markdown(render_card_html(c_fighter["card"], size="small", show_special_effects=False), unsafe_allow_html=True)

    st.markdown("#### 🎮 Scegli la tua mossa:")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("⚡ ATTACCO", key="battle_attack", use_container_width=True):
            process_battle_action(battle_state, "attack", rivals_data); st.rerun()
    with c2:
        ok = p_fighter["stamina"] >= 40
        if st.button("🔥 SUPER {s}".format(s="✓" if ok else "✗"), key="battle_special",
                     use_container_width=True, disabled=not ok):
            process_battle_action(battle_state, "special", rivals_data); st.rerun()
    with c3:
        if st.button("🛡️ DIFENDI", key="battle_defend", use_container_width=True):
            process_battle_action(battle_state, "defend", rivals_data); st.rerun()
    with c4:
        okf = battle_state["stamina_charges"] >= 10
        if st.button("💥 FINALE {s}".format(s="✓" if okf else "{sc}/10".format(sc=battle_state["stamina_charges"])),
                     key="battle_final", use_container_width=True, disabled=not okf):
            process_battle_action(battle_state, "final", rivals_data); st.rerun()

    if battle_state["log"]:
        with st.expander("📋 Log Battaglia", expanded=True):
            html = '<div class="battle-log">'
            for entry in reversed(battle_state["log"][-8:]):
                html += "<div>{e}</div>".format(e=entry)
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)

    if st.button("🏳️ Abbandona partita", key="battle_quit"):
        rivals_data["battle_losses"] += 1
        st.session_state.battle_state = None; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# COLLECTION TAB
# ══════════════════════════════════════════════════════════════════════════════

def _render_collection_tab(rivals_data, cards_db, state):
    st.markdown("## 🃏 La Mia Collezione")

    team_cards = _get_active_team_cards(rivals_data)
    n_team     = len(team_cards)

    # ── Squadra Attiva ──
    st.markdown("### 👥 Squadra Attiva ({n}/5)".format(n=n_team))
    tcols = st.columns(5)
    for i in range(5):
        with tcols[i]:
            if i < n_team:
                st.markdown(render_card_html(team_cards[i], size="small"), unsafe_allow_html=True)
                if st.button("❌ Rimuovi", key="rm_team_{k}".format(k=_iid(team_cards[i])[:10]), use_container_width=True):
                    _remove_from_active_team(rivals_data, team_cards[i]); st.rerun()
            else:
                st.markdown(
                    '<div style="min-height:160px;border:2px dashed #1e1e3a;border-radius:12px;'
                    'display:flex;align-items:center;justify-content:center;color:#2a2a4a;font-size:1.5rem">&#65291;</div>',
                    unsafe_allow_html=True)

    st.markdown("---")

    src_tabs = st.tabs(["🃏 Mie Carte", "⭐ Atleti Reali"])

    with src_tabs[0]:
        _collection_mycards(rivals_data, n_team)

    with src_tabs[1]:
        _collection_athletes(rivals_data, cards_db, state, n_team)


def _collection_mycards(rivals_data, n_team):
    all_cards_coll = rivals_data.get("collection_cards", [])

    # Retrocompatibilità: vecchia collezione usava solo IDs e cards_db
    if not all_cards_coll:
        st.warning("📦 Nessuna carta! Vai nel **Negozio** per acquistare pacchetti.")
        return

    tier_filter = st.selectbox("🔍 Filtra per Rarità", ["Tutte"] + list(CARD_TIERS.keys()), key="cf_tier")
    sort_opt    = st.selectbox("Ordina per", ["OVR ↓", "Rarità", "Nome"], key="cf_sort")

    filtered = all_cards_coll if tier_filter == "Tutte" else [
        c for c in all_cards_coll if get_tier_by_ovr(c.get("overall", 40)) == tier_filter
    ]
    if sort_opt == "OVR ↓":   filtered = sorted(filtered, key=lambda c: c.get("overall",0), reverse=True)
    elif sort_opt == "Rarità": filtered = sorted(filtered, key=lambda c: CARD_TIERS.get(get_tier_by_ovr(c.get("overall",40)),{}).get("rarity",0), reverse=True)
    else:                      filtered = sorted(filtered, key=lambda c: (c.get("cognome") or c.get("nome","")).lower())

    st.caption("📊 Totale: {t} carte | Mostrate: {f}".format(t=len(all_cards_coll), f=len(filtered)))

    # Raggruppa per tier (come originale)
    rarity_groups = {}
    for card in filtered:
        tier = get_tier_by_ovr(card.get("overall", 40))
        rarity_groups.setdefault(tier, []).append(card)

    active_ids = rivals_data.get("active_team", [])

    for tier_name in reversed(list(CARD_TIERS.keys())):
        if tier_name not in rarity_groups:
            continue
        tier_cards = rarity_groups[tier_name]
        ti         = CARD_TIERS[tier_name]

        with st.expander("{t} ({n} carte)".format(t=tier_name, n=len(tier_cards)), expanded=ti["rarity"] >= 12):
            for i in range(0, len(tier_cards), 5):
                chunk    = tier_cards[i:i+5]
                row_cols = st.columns(5)
                for j, card in enumerate(chunk):
                    with row_cols[j]:
                        iid      = _iid(card)
                        in_team  = iid in active_ids
                        st.markdown(render_card_html(card, size="small"), unsafe_allow_html=True)
                        st.caption("OVR {ovr} | {role}".format(ovr=card.get("overall",40), role=card.get("ruolo","")[:10]))
                        if in_team:
                            if st.button("✅ IN SQUADRA", key="rm2_{k}".format(k=iid[:10]), use_container_width=True):
                                _remove_from_active_team(rivals_data, card); st.rerun()
                        else:
                            dis = n_team >= 5
                            if st.button("➕ Aggiungi" if not dis else "🔒 Squadra piena",
                                         key="add2_{k}".format(k=iid[:10]), disabled=dis, use_container_width=True):
                                _add_to_active_team(rivals_data, card); st.rerun()


def _collection_athletes(rivals_data, cards_db, state, n_team):
    atleti = state.get("atleti", [])
    if not atleti:
        st.info("Nessun atleta nel torneo.")
        return
    try:
        from data_manager import calcola_overall_fifa
        has_ovr = True
    except Exception:
        has_ovr = False

    coll_ids   = [_iid(c) for c in rivals_data.get("collection_cards", [])]
    active_ids = rivals_data.get("active_team", [])

    st.markdown("Importa atleti reali come carte nella tua collezione:")
    for i in range(0, len(atleti), 4):
        chunk    = atleti[i:i+4]
        row_cols = st.columns(4)
        for j, a in enumerate(chunk):
            with row_cols[j]:
                ovr = calcola_overall_fifa(a) if has_ovr else 60
                s   = a.get("stats", {})
                card = {
                    "id":           "ath_{id}".format(id=a.get("id","?")),
                    "instance_id":  "ath_{id}".format(id=a.get("id","?")),
                    "nome":          a.get("nome","?"),
                    "cognome":       a.get("cognome",""),
                    "overall":       ovr,
                    "ruolo":         a.get("ruolo","SPIKER"),
                    "attacco":       s.get("attacco",50),
                    "difesa":        s.get("difesa",50),
                    "muro":          s.get("muro",50),
                    "ricezione":     s.get("ricezione",50),
                    "battuta":       s.get("battuta",50),
                    "alzata":        s.get("alzata",50),
                    "foto_path":     a.get("foto_path",""),
                    "source":        "athlete",
                    "atleta_id":     a.get("id"),
                }
                aiid    = _iid(card)
                owned   = aiid in coll_ids
                in_team = aiid in active_ids

                st.markdown(render_card_html(card, size="small"), unsafe_allow_html=True)
                st.caption("OVR {ovr}".format(ovr=ovr))

                if owned:
                    if in_team:
                        if st.button("✅ IN SQUADRA", key="arm_{k}".format(k=aiid[:12]), use_container_width=True):
                            _remove_from_active_team(rivals_data, card); st.rerun()
                    else:
                        dis = n_team >= 5
                        if st.button("➕ Team" if not dis else "🔒", key="aat_{k}".format(k=aiid[:12]),
                                     disabled=dis, use_container_width=True):
                            _add_to_active_team(rivals_data, card); st.rerun()
                else:
                    if st.button("📥 Aggiungi collezione", key="aadd_{k}".format(k=aiid[:12]),
                                 use_container_width=True, type="primary"):
                        _add_to_coll(rivals_data, card); st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SHOP TAB
# ══════════════════════════════════════════════════════════════════════════════

def _render_shop_tab(rivals_data, cards_db):
    st.markdown("## 🛒 Negozio Pacchetti")
    coins = rivals_data.get("mbt_coins", 0)

    st.markdown(
        '<div style="text-align:right;margin-bottom:20px">'
        '<span style="font-family:Orbitron,sans-serif;font-size:1.2rem;color:#ffd700;font-weight:700">'
        '&#127890; {coins} MBT Coins</span></div>'.format(coins="{:,}".format(coins)),
        unsafe_allow_html=True)

    pack_cols  = st.columns(3)
    pack_names = ["Base", "Epico", "Leggenda"]
    pack_descs = {
        "Base":     "Perfetto per iniziare. Carte Bronzo, Argento e raramente Oro.",
        "Epico":    "Alta probabilità di Oro ed Eroi. Chance di Leggenda e TOTY!",
        "Leggenda": "Solo carte di alto livello. Garantisce almeno una Leggenda!",
    }

    for i, pack_name in enumerate(pack_names):
        pi          = PACKS[pack_name]
        color       = pi["label_color"]
        can_afford  = coins >= pi["price"]

        with pack_cols[i]:
            st.markdown(
                '<div class="pack-card {css}" style="margin-bottom:8px">'
                '<div style="font-size:3rem;z-index:2">{emoji}</div>'
                '<div style="font-family:Orbitron,sans-serif;font-size:1.1rem;font-weight:900;color:{col};z-index:2;letter-spacing:3px;text-transform:uppercase">{name}</div>'
                '<div style="font-size:.65rem;color:#888;z-index:2;text-align:center;padding:0 10px;margin-top:4px">{desc}</div>'
                '<div style="font-family:Orbitron,sans-serif;font-size:1rem;font-weight:700;color:#ffd700;z-index:2;margin-top:8px">&#127890; {price}</div>'
                '</div>'.format(
                    css=pi["css_class"], emoji=pi["emoji"], col=color,
                    name=pack_name, desc=pack_descs[pack_name],
                    price="{:,}".format(pi["price"])),
                unsafe_allow_html=True)

            if st.button(
                "{lbl} {n}".format(lbl="🛒 Acquista" if can_afford else "🔒 Non abbastanza coins", n=pack_name),
                key="buy_pack_{n}".format(n=pack_name),
                use_container_width=True,
                disabled=not can_afford,
                type="primary" if can_afford else "secondary"
            ):
                rivals_data["mbt_coins"] -= pi["price"]
                drawn = draw_cards_from_pack(pack_name, cards_db)
                st.session_state["drawn_cards"]  = drawn
                st.session_state["opening_pack"] = pack_name
                st.rerun()

    # ── Apertura Pack ──
    drawn = st.session_state.get("drawn_cards")
    if drawn:
        pack_opened = st.session_state.get("opening_pack", "Base")
        max_rarity  = max(CARD_TIERS.get(get_tier_by_ovr(c.get("overall",40)),{}).get("rarity",0) for c in drawn)
        st.markdown("---")

        if max_rarity >= 16:
            st.markdown(
                '<div style="text-align:center;background:rgba(255,34,0,.12);border:2px solid #ff2200;'
                'border-radius:12px;padding:10px;margin-bottom:12px;animation:iconGodPulse 1s infinite">'
                '<span style="font-family:Orbitron,sans-serif;font-size:1rem;color:#ff2200;font-weight:900">'
                '&#128293;&#128293; CARTA ICON GOD! &#128293;&#128293;</span></div>',
                unsafe_allow_html=True)
        elif max_rarity >= 12:
            st.markdown(
                '<div style="text-align:center;background:rgba(255,215,0,.1);border:2px solid #ffd700;'
                'border-radius:10px;padding:10px;margin-bottom:12px">'
                '<span style="font-family:Orbitron,sans-serif;font-size:1rem;color:#ffd700;'
                'animation:goldShine 1s infinite">&#9889;&#128165; CARTA ICONA! &#128165;&#9889;</span></div>',
                unsafe_allow_html=True)
        elif max_rarity >= 8:
            st.markdown(
                '<div style="text-align:center;background:rgba(255,255,255,.05);border:2px solid #fff;'
                'border-radius:10px;padding:8px;margin-bottom:12px">'
                '<span style="font-family:Orbitron,sans-serif;font-size:.9rem;color:#fff">'
                '&#10024; CARTA LEGGENDARIA O SUPERIORE! &#10024;</span></div>',
                unsafe_allow_html=True)

        render_pack_opening_animation(drawn, pack_opened)
        st.markdown("")

        ca, cb = st.columns(2)
        with ca:
            if st.button("✅ Aggiungi TUTTE alla Collezione", use_container_width=True, type="primary"):
                for card in drawn:
                    _add_to_coll(rivals_data, card)
                st.session_state["drawn_cards"]  = None
                st.session_state["opening_pack"] = None
                st.success("✅ {n} carte aggiunte alla collezione!".format(n=len(drawn)))
                st.rerun()
        with cb:
            if st.button("🗑️ Scarta", use_container_width=True):
                st.session_state["drawn_cards"]  = None
                st.session_state["opening_pack"] = None
                st.rerun()

    # ── Mosse Speciali ──
    st.markdown("---")
    st.markdown("### ⚡ Mosse Speciali")
    st.caption("Insegna mosse speciali alle tue carte spendendo MBT Coins")
    learned    = rivals_data.get("special_moves_learned", [])
    move_cols  = st.columns(3)
    for i, move in enumerate(SPECIAL_MOVES[:9]):
        with move_cols[i % 3]:
            already    = move["id"] in learned
            can_afford = coins >= move["cost_coins"]
            role_tag   = "[{r}]".format(r=move["role"]) if move.get("role") else "[Universale]"
            border     = "#ffd700" if already else "#1e1e3a"
            st.markdown(
                '<div style="background:#10101e;border:1px solid {border};border-radius:8px;padding:10px;margin-bottom:8px;min-height:100px">'
                '<div style="font-family:Orbitron,sans-serif;font-size:.7rem;font-weight:700;color:{nc}">{name}</div>'
                '<div style="font-size:.55rem;color:#555;margin:4px 0">{rt}</div>'
                '<div style="font-size:.6rem;color:#777">{desc}</div>'
                '<div style="font-size:.6rem;color:{sc};margin-top:4px">{status}</div>'
                '</div>'.format(
                    border=border, nc="#ffd700" if already else "#ccc",
                    name=move["name"], rt=role_tag, desc=move["desc"],
                    sc="#4ade80" if already else "#ffd700",
                    status="✅ Appresa" if already else "&#127890; {:,} Coins".format(move["cost_coins"])),
                unsafe_allow_html=True)
            if not already:
                if st.button("Apprendi", key="learn_{id}".format(id=move["id"]),
                             disabled=not can_afford, use_container_width=True):
                    rivals_data["special_moves_learned"].append(move["id"])
                    rivals_data["mbt_coins"] -= move["cost_coins"]
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ARENAS TAB
# ══════════════════════════════════════════════════════════════════════════════

def _render_arenas_tab(rivals_data):
    st.markdown("## 🏟️ Sistema Arene")
    st.caption("Avanza di livello per sbloccare arene sempre più epiche!")
    level = rivals_data["player_level"]

    for arena in ARENE:
        is_unlocked = level >= arena["min_level"]
        is_current  = arena["min_level"] <= level <= arena["max_level"]
        col1, col2  = st.columns([1, 3])

        with col1:
            op = "1" if is_unlocked else ".4"
            gs = "" if is_unlocked else "filter:grayscale(80%);"
            st.markdown(
                '<div class="arena-badge {css}" style="opacity:{op};{gs}">'
                '<div style="font-size:2rem">{icon}</div>'
                '<div style="font-family:Orbitron,sans-serif;font-size:.65rem;font-weight:700;'
                'color:{col}">LV.{ml}-{xl}</div>'
                '</div>'.format(
                    css=arena["css"] if is_unlocked else "",
                    op=op, gs=gs,
                    icon=arena["icon"] if is_unlocked else "🔒",
                    col=arena["color"] if is_unlocked else "#555",
                    ml=arena["min_level"], xl=arena["max_level"]),
                unsafe_allow_html=True)

        with col2:
            badge = " 🔴 ATTUALE" if is_current else (" ✅ SBLOCCATA" if is_unlocked else " 🔒")
            c = arena["color"] if is_unlocked else "#555"
            extra = '<div style="font-size:.65rem;color:#ffd700;margin-top:4px">⚡ Combatti qui per ricompense speciali!</div>' if is_current else ""
            st.markdown(
                '<div style="padding:12px 0">'
                '<div style="font-family:Orbitron,sans-serif;font-weight:700;color:{c};font-size:.9rem">{name}{badge}</div>'
                '<div style="font-size:.7rem;color:#555;margin-top:4px">Livelli {ml} – {xl}</div>'
                '{extra}</div>'.format(c=c, name=arena["name"], badge=badge,
                                       ml=arena["min_level"], xl=arena["max_level"], extra=extra),
                unsafe_allow_html=True)

        st.markdown("<hr style='border-color:#1e1e3a;margin:4px 0'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# POWERS TAB
# ══════════════════════════════════════════════════════════════════════════════

def _render_powers_tab(rivals_data):
    st.markdown("## 💪 Super Poteri")
    st.caption("Potenzia i tuoi super poteri spendendo MBT Coins")
    coins      = rivals_data.get("mbt_coins", 0)
    superpowers= rivals_data.setdefault("superpowers", {})

    for power in SUPERPOWERS:
        current_level = superpowers.get(power["id"], 0)
        max_level     = power["max_level"]
        cost          = power["cost_per_level"]
        bars          = "█" * current_level + "░" * (max_level - current_level)

        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(
                '<div style="background:#10101e;border:1px solid #1e1e3a;border-radius:8px;padding:12px;margin-bottom:8px">'
                '<div style="font-family:Orbitron,sans-serif;font-size:.8rem;font-weight:700;color:#ffd700">'
                '{name} <span style="font-size:.65rem;color:#555">LV.{cl}/{ml}</span></div>'
                '<div style="font-size:.65rem;color:#777;margin:4px 0">{desc}</div>'
                '<div style="font-size:1rem;color:#ffd700;letter-spacing:2px">{bars}</div>'
                '</div>'.format(name=power["name"], cl=current_level, ml=max_level,
                               desc=power["desc"], bars=bars),
                unsafe_allow_html=True)
        with col2:
            if current_level < max_level:
                st.metric("Costo", "&#127890; {c}".format(c=cost))
        with col3:
            if current_level < max_level:
                can_up = coins >= cost
                if st.button("⬆️ Potenzia", key="up_power_{id}".format(id=power["id"]),
                             disabled=not can_up, use_container_width=True):
                    superpowers[power["id"]] = current_level + 1
                    rivals_data["mbt_coins"] -= cost
                    st.rerun()
            else:
                st.markdown('<div style="color:#ffd700;text-align:center;padding:20px 0">✅ MAX</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN TAB — con password come originale
# ══════════════════════════════════════════════════════════════════════════════

def _render_admin_tab(state, cards_db, rivals_data):
    st.markdown("## ⚙️ Pannello Admin — Cards Creator")

    if not st.session_state.get("admin_unlocked_rivals"):
        pwd = st.text_input("🔐 Password Admin", type="password", key="admin_pwd_rivals")
        if st.button("Accedi", key="admin_login_rivals"):
            if pwd in ("admin", "mbt2025", "rivals"):
                st.session_state.admin_unlocked_rivals = True; st.rerun()
            else:
                st.error("❌ Password errata")
        return

    admin_tabs = st.tabs(["➕ Crea Carta", "📋 Gestisci Carte", "🎁 Gestisci Coins"])
    with admin_tabs[0]: _render_card_creator(state, cards_db, rivals_data)
    with admin_tabs[1]: _render_card_manager(cards_db)
    with admin_tabs[2]: _render_coins_manager(rivals_data)


def _render_card_creator(state, cards_db, rivals_data):
    st.markdown("### ✏️ Crea Nuova Carta")
    col_form, col_preview = st.columns([2, 1])

    with col_form:
        nome    = st.text_input("Nome",    key="cc_nome")
        cognome = st.text_input("Cognome", key="cc_cognome")
        ruolo   = st.selectbox("Ruolo", ROLES, key="cc_ruolo")

        st.markdown("---")
        st.markdown("**Statistiche** (0 – 125 per attributo)")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            atk = st.slider("⚡ Attacco",    0, 125, 65, key="cc_atk")
            dif = st.slider("🛡️ Difesa",     0, 125, 60, key="cc_dif")
            ric = st.slider("🤲 Ricezione",  0, 125, 55, key="cc_ric")
        with col_s2:
            bat = st.slider("🏐 Battuta",    0, 125, 58, key="cc_bat")
            mur = st.slider("🧱 Muro",       0, 125, 52, key="cc_mur")
            alz = st.slider("🎯 Alzata",     0, 125, 50, key="cc_alz")

        # OVR calcolato matematicamente
        ovr_calc   = calcola_ovr_da_stats(atk, dif, ric, bat, mur, alz)
        tier_calc  = get_tier_by_ovr(ovr_calc)
        tier_color = CARD_TIERS.get(tier_calc, {}).get("color", "#ffd700")
        st.markdown(
            '<div style="background:#10101e;border:1px solid {tc};border-radius:8px;padding:10px;margin:8px 0;display:flex;gap:16px;align-items:center">'
            '<div style="font-family:Orbitron,sans-serif;font-size:1.5rem;font-weight:900;color:{tc}">{ovr}</div>'
            '<div>'
            '<div style="font-family:Orbitron,sans-serif;font-size:.75rem;color:{tc};font-weight:700">{tier}</div>'
            '<div style="font-size:.58rem;color:#555">OVR calcolato automaticamente</div>'
            '</div></div>'.format(tc=tier_color, ovr=ovr_calc, tier=tier_calc),
            unsafe_allow_html=True)

        st.markdown("---")
        foto_file = st.file_uploader("📷 Upload Foto Atleta", type=["png","jpg","jpeg"], key="cc_foto")
        foto_path = ""
        if foto_file:
            os.makedirs(ASSETS_ICONS_DIR, exist_ok=True)
            safe_name = "{n}_{c}_{r}.jpg".format(
                n=(nome or "card").replace(" ","_"),
                c=(cognome or "").replace(" ","_"),
                r=random.randint(1000,9999))
            foto_path = os.path.join(ASSETS_ICONS_DIR, safe_name)
            with open(foto_path, "wb") as f:
                f.write(foto_file.read())
            st.success("📷 Foto salvata: {fp}".format(fp=foto_path))

        atleti_nomi = ["-- Nessuno --"] + [a["nome"] for a in state.get("atleti", [])]
        sel_atleta  = st.selectbox("🔗 Collega a Atleta Torneo (opzionale)", atleti_nomi, key="cc_atleta_link")
        atleta_id_linked = None
        if sel_atleta != "-- Nessuno --":
            linked = next((a for a in state.get("atleti",[]) if a["nome"] == sel_atleta), None)
            if linked:
                atleta_id_linked = linked["id"]
                try:
                    from data_manager import calcola_overall_fifa
                    real_ovr = calcola_overall_fifa(linked)
                    st.info("📊 OVR reale dall'app torneo: **{ovr}** — La carta si aggiornerà automaticamente.".format(ovr=real_ovr))
                except Exception:
                    pass

    with col_preview:
        st.markdown("#### 👁️ Anteprima Carta")
        preview_card = {
            "nome": nome or "NOME", "cognome": cognome or "",
            "overall": ovr_calc, "ruolo": ruolo,
            "attacco": atk, "difesa": dif, "battuta": bat,
            "muro": mur, "ricezione": ric, "alzata": alz,
            "foto_path": foto_path,
        }
        st.markdown(
            '<div class="creator-preview-wrap">{html}</div>'.format(html=render_card_html(preview_card, size="large")),
            unsafe_allow_html=True)

        st.markdown(
            '<div style="background:#10101e;border:1px solid {tc};border-radius:8px;padding:10px;text-align:center;margin-top:10px">'
            '<div style="font-family:Orbitron,sans-serif;font-size:.7rem;color:{tc};font-weight:700">{tier}</div>'
            '<div style="font-size:.6rem;color:#555;margin-top:2px">OVR {ovr}</div>'
            '</div>'.format(tc=tier_color, tier=tier_calc, ovr=ovr_calc),
            unsafe_allow_html=True)

    st.markdown("---")
    sv1, sv2 = st.columns(2)

    def _make_new_card():
        nid = "card_{n}_{r}".format(n=cards_db["next_id"], r=random.randint(1000,9999))
        cards_db["next_id"] += 1
        return {
            "id": nid, "instance_id": "admin_{nid}".format(nid=nid),
            "nome": nome, "cognome": cognome, "overall": ovr_calc, "ruolo": ruolo,
            "attacco": atk, "difesa": dif, "muro": mur,
            "ricezione": ric, "battuta": bat, "alzata": alz,
            "foto_path": foto_path, "tier": tier_calc,
            "atleta_id": atleta_id_linked, "source": "admin",
            "created_at": datetime.now().isoformat(),
        }

    with sv1:
        if st.button("💾 SALVA CARTA nel Database", use_container_width=True, type="primary"):
            if not nome:
                st.error("Inserisci il nome del giocatore!")
            else:
                nc = _make_new_card()
                cards_db["cards"].append(nc)
                save_cards_db(cards_db)
                st.session_state.cards_db = cards_db
                st.success("✅ Carta **{n} {c}** (OVR {ovr} · {tier}) salvata!".format(
                    n=nome, c=cognome, ovr=ovr_calc, tier=tier_calc))
                st.rerun()

    with sv2:
        if st.button("💾 Salva e Aggiungi a Collezione", use_container_width=True):
            if not nome:
                st.error("Inserisci il nome del giocatore!")
            else:
                nc = _make_new_card()
                cards_db["cards"].append(nc)
                save_cards_db(cards_db)
                st.session_state.cards_db = cards_db
                _add_to_coll(rivals_data, nc)
                st.success("✅ Carta creata e aggiunta alla collezione!")
                st.rerun()


def _render_card_manager(cards_db):
    st.markdown("### 📋 Carte nel Database")
    all_cards = cards_db.get("cards", [])
    if not all_cards:
        st.info("Nessuna carta nel database. Creane una con il Card Creator!")
        return

    st.caption("Totale: {n} carte".format(n=len(all_cards)))
    filter_tier = st.selectbox("Filtra Tier", ["Tutte"] + list(CARD_TIERS.keys()), key="mgr_filter")
    filtered = all_cards if filter_tier == "Tutte" else [
        c for c in all_cards if get_tier_by_ovr(c.get("overall",40)) == filter_tier
    ]

    for i, card in enumerate(filtered):
        tier = get_tier_by_ovr(card.get("overall",40))
        tc   = CARD_TIERS.get(tier, {}).get("color","#888")
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.markdown(render_card_html(card, size="small", show_special_effects=False), unsafe_allow_html=True)
        with col2:
            st.markdown(
                '<div style="padding:8px 0">'
                '<div style="font-family:Orbitron,sans-serif;font-weight:700;color:{tc};font-size:.85rem">'
                '{nome} {cogn}</div>'
                '<div style="font-size:.7rem;color:#555">OVR {ovr} · {tier} · {ruolo}</div>'
                '<div style="font-size:.55rem;color:#444">ATK:{atk} DEF:{dif} BAT:{bat} MUR:{mur} RIC:{ric} ALZ:{alz}</div>'
                '<div style="font-size:.5rem;color:#333;margin-top:2px">ID: {id}...</div>'
                '</div>'.format(
                    tc=tc, nome=card.get("nome",""), cogn=card.get("cognome",""),
                    ovr=card.get("overall",40), tier=tier, ruolo=card.get("ruolo",""),
                    atk=card.get("attacco",40), dif=card.get("difesa",40), bat=card.get("battuta",40),
                    mur=card.get("muro",40),    ric=card.get("ricezione",40), alz=card.get("alzata",40),
                    id=card.get("id","")[:16]),
                unsafe_allow_html=True)
        with col3:
            if st.button("🗑️", key="del_card_{i}_{k}".format(i=i, k=card.get("id","")[:8]), help="Elimina carta"):
                cards_db["cards"] = [c for c in all_cards if c.get("id") != card.get("id")]
                save_cards_db(cards_db)
                st.session_state.cards_db = cards_db
                st.rerun()
        st.markdown("<hr style='border-color:#1e1e3a;margin:4px 0'>", unsafe_allow_html=True)


def _render_coins_manager(rivals_data):
    st.markdown("### 🎁 Gestione Coins & XP")
    col1, col2 = st.columns(2)
    with col1:
        add_coins = st.number_input("Aggiungi MBT Coins", 0, 999999, 500, key="admin_add_coins")
        if st.button("➕ Aggiungi Coins", key="admin_btn_coins"):
            rivals_data["mbt_coins"] += add_coins
            st.success("✅ Aggiunti {:,} coins! Totale: {:,}".format(add_coins, rivals_data["mbt_coins"]))
    with col2:
        add_xp = st.number_input("Aggiungi XP", 0, 99999, 100, key="admin_add_xp")
        if st.button("➕ Aggiungi XP", key="admin_btn_xp"):
            rivals_data["player_xp"] += add_xp
            _check_level_up(rivals_data)
            st.success("✅ Aggiunti {xp} XP! Level: {lv}".format(xp=add_xp, lv=rivals_data["player_level"]))

    st.markdown("---")
    st.markdown("""
**Stato attuale:**
- MBT Coins: **{coins:,}**
- XP: **{xp}**
- Livello: **{lv}**
- Trofei: **{tr}**
- Vittorie: **{bw}**
- Carte in collezione: **{nc}**
""".format(
        coins=rivals_data["mbt_coins"], xp=rivals_data["player_xp"],
        lv=rivals_data["player_level"], tr=rivals_data["trofei_rivals"],
        bw=rivals_data["battle_wins"], nc=len(rivals_data.get("collection_cards",[]))))

    st.markdown("---")
    if st.button("🔄 Reset Dati Rivals", key="admin_reset_rivals"):
        st.session_state.rivals_data = empty_rivals_state()
        st.session_state.rivals_data["mbt_coins"] = 1000
        save_rivals_data(st.session_state.rivals_data)
        st.success("✅ Dati Rivals resettati con 1000 Coins di partenza.")
        st.rerun()
