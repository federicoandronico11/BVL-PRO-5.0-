"""
mbt_rivals.py — MBT RIVALS: Sistema Carte, Collezione, Negozio, Battaglia v2.0
Completamente scollegato dal sistema torneo tranne per l'evoluzione OVR degli atleti.
MIGLIORAMENTI v2.0:
- Forme geometriche progressive per rarità (clip-path SVG avanzati)
- Badge HTML non più visibili come testo grezzo
- OVR calcolato matematicamente da 6 stat (range 40-125)
- Nome piccolo sopra al COGNOME grande
- Animazioni professionali: shimmer, holographic, beam, fire, cracks
- Slider stat 0-125 in Admin
- Carte Rivals con immagine di sfondo reale
- Effetti hover: riflessi animati, bagliori, overlay
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
ASSETS_CARDS_DIR = "assets/card_templates"

# ─── CALCOLO OVR DA STATS ────────────────────────────────────────────────────

def calcola_ovr_da_stats(atk=40, dif=40, ric=40, bat=40, mur=40, alz=40):
    """Calcola OVR matematicamente da 6 statistiche. Range 40-125."""
    # Pesi per il calcolo: ATK e DEF più importanti, ALZ meno
    pesi = {"atk": 1.4, "dif": 1.2, "bat": 1.1, "ric": 1.0, "mur": 0.9, "alz": 0.8}
    somma_pesi = sum(pesi.values())
    media_pesata = (
        atk * pesi["atk"] +
        dif * pesi["dif"] +
        bat * pesi["bat"] +
        ric * pesi["ric"] +
        mur * pesi["mur"] +
        alz * pesi["alz"]
    ) / somma_pesi
    # Scala da 0-125 a 40-125
    ovr = int(max(40, min(125, media_pesata)))
    return ovr


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
  --font-rivals: 'Orbitron', 'Rajdhani', sans-serif;
  --font-body: 'Exo 2', sans-serif;
}

/* ── Keyframes ── */
@keyframes goldShine {
  0%{background-position:200% center}
  100%{background-position:-200% center}
}
@keyframes pulseGlow {
  0%,100%{box-shadow:0 0 10px currentColor}
  50%{box-shadow:0 0 30px currentColor,0 0 60px currentColor}
}
@keyframes floatUp {
  0%,100%{transform:translateY(0)}
  50%{transform:translateY(-8px)}
}
@keyframes shimmer {
  0%{left:-100%}100%{left:200%}
}
@keyframes shimmerH {
  0%{background-position:200% center}
  100%{background-position:-200% center}
}
@keyframes particleFall {
  0%{transform:translateY(-20px) rotate(0deg);opacity:1}
  100%{transform:translateY(60px) rotate(360deg);opacity:0}
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
@keyframes snakeWiggle {
  0%,100%{transform:scaleX(1) rotate(0deg)}
  25%{transform:scaleX(-1) rotate(5deg)}
  75%{transform:scaleX(1) rotate(-5deg)}
}
@keyframes fireFlicker {
  0%,100%{transform:scaleY(1) translateX(0)}
  25%{transform:scaleY(1.1) translateX(-2px)}
  75%{transform:scaleY(0.95) translateX(2px)}
}
@keyframes smokeRise {
  0%{transform:translateY(0) scale(1);opacity:0.6}
  100%{transform:translateY(-30px) scale(2);opacity:0}
}
@keyframes goldDust {
  0%{transform:translate(0,0) rotate(0deg);opacity:1}
  100%{transform:translate(var(--dx,20px),var(--dy,-30px)) rotate(720deg);opacity:0}
}
@keyframes nebulaSwirl {
  0%{transform:rotate(0deg) scale(1)}
  50%{transform:rotate(180deg) scale(1.1)}
  100%{transform:rotate(360deg) scale(1)}
}
@keyframes explosion {
  0%{transform:scale(0) rotate(0deg);opacity:1}
  60%{transform:scale(1.5) rotate(180deg);opacity:0.8}
  100%{transform:scale(3) rotate(360deg);opacity:0}
}
@keyframes packReveal {
  0%{transform:rotateY(0deg);opacity:1}
  50%{transform:rotateY(90deg);opacity:0.5}
  100%{transform:rotateY(0deg);opacity:1}
}
@keyframes screenShake {
  0%,100%{transform:translate(0,0)}
  10%{transform:translate(-8px,4px)}
  20%{transform:translate(8px,-4px)}
  30%{transform:translate(-6px,6px)}
  40%{transform:translate(6px,-2px)}
  50%{transform:translate(-4px,4px)}
  60%{transform:translate(4px,-4px)}
  70%{transform:translate(-2px,2px)}
  80%{transform:translate(2px,-2px)}
  90%{transform:translate(-1px,1px)}
}
@keyframes hpBar {
  0%{width:var(--hp-from)}
  100%{width:var(--hp-to)}
}
@keyframes battleHit {
  0%{transform:translateX(0);filter:brightness(1)}
  20%{transform:translateX(-15px);filter:brightness(3) saturate(0)}
  40%{transform:translateX(10px);filter:brightness(1)}
  60%{transform:translateX(-5px)}
  100%{transform:translateX(0);filter:brightness(1)}
}
@keyframes evolutionGlow {
  0%{opacity:0;transform:scale(0.5)}
  50%{opacity:1;transform:scale(1.2)}
  100%{opacity:0;transform:scale(2)}
}
@keyframes beamRotate {
  0%{transform:rotate(0deg)}
  100%{transform:rotate(360deg)}
}
@keyframes cardFlipIn {
  0%{transform:rotateY(90deg) scale(0.8);opacity:0;filter:brightness(3)}
  50%{transform:rotateY(-10deg) scale(1.05)}
  100%{transform:rotateY(0deg) scale(1);opacity:1;filter:brightness(1)}
}
@keyframes driftParticle {
  0%{transform:translate(0,0) scale(1);opacity:0.8}
  100%{transform:translate(var(--dx,15px),var(--dy,-40px)) scale(0);opacity:0}
}
@keyframes cracksAnimate {
  0%,100%{opacity:0.4;stroke-dashoffset:100}
  50%{opacity:1;stroke-dashoffset:0}
}
@keyframes godPulse {
  0%,100%{filter:brightness(1) saturate(1)}
  50%{filter:brightness(1.5) saturate(1.8)}
}
@keyframes holoSheen {
  0%{background-position:0% 50%;opacity:0.6}
  50%{background-position:100% 50%;opacity:1}
  100%{background-position:0% 50%;opacity:0.6}
}
@keyframes hoverLift {
  0%{transform:translateY(0) rotateX(0deg)}
  100%{transform:translateY(-12px) rotateX(4deg)}
}

/* ── CARDS ── */
.mbt-card-wrap {
  position:relative;
  display:inline-block;
  cursor:pointer;
  transition:transform 0.35s cubic-bezier(0.34,1.56,0.64,1),filter 0.35s;
  perspective:600px;
}
.mbt-card-wrap:hover {
  transform:translateY(-10px) scale(1.06) rotateX(3deg);
  z-index:10;
  filter:drop-shadow(0 20px 40px rgba(0,0,0,0.8));
}
.mbt-card {
  width:140px;
  min-height:200px;
  border-radius:12px;
  position:relative;
  overflow:hidden;
  font-family:var(--font-rivals);
  user-select:none;
  transform-style:preserve-3d;
}

/* ── Hover reflection overlay ── */
.mbt-card::after {
  content:'';
  position:absolute;
  top:0;left:-100%;
  width:50%;height:100%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,0.12),transparent);
  transition:left 0.5s ease;
  z-index:20;
  pointer-events:none;
  border-radius:12px;
}
.mbt-card-wrap:hover .mbt-card::after {
  left:150%;
  transition:left 0.5s ease;
}

/* ── Base/Bronzo ── */
.mbt-card.bronzo {
  background:linear-gradient(160deg,#3d2b1f 0%,#6b4226 50%,#3d2b1f 100%);
  border:2px solid #cd7f32;
  box-shadow:0 4px 15px rgba(205,127,50,0.3);
  clip-path:polygon(0% 6%,6% 0%,94% 0%,100% 6%,100% 94%,94% 100%,6% 100%,0% 94%);
}
/* ── Argento ── */
.mbt-card.argento {
  background:linear-gradient(160deg,#2a2a2a 0%,#555 50%,#2a2a2a 100%);
  border:2px solid #c0c0c0;
  box-shadow:0 4px 20px rgba(192,192,192,0.4);
  clip-path:polygon(0% 8%,4% 0%,96% 0%,100% 8%,100% 50%,96% 100%,4% 100%,0% 50%);
}
.mbt-card.argento::before {
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,transparent 40%,rgba(255,255,255,0.08) 50%,transparent 60%);
  background-size:200% 200%;
  animation:holoSheen 4s infinite;
  z-index:1;pointer-events:none;border-radius:10px;
}
/* ── Oro ── */
.mbt-card.oro {
  background:linear-gradient(160deg,#2a1f00 0%,#5a4200 50%,#2a1f00 100%);
  border:2px solid #ffd700;
  box-shadow:0 6px 25px rgba(255,215,0,0.5);
  clip-path:polygon(4% 0%,50% 2%,96% 0%,100% 4%,100% 96%,96% 100%,4% 100%,0% 96%);
}
.mbt-card.oro::before {
  content:'';position:absolute;inset:0;
  background:linear-gradient(90deg,transparent,rgba(255,215,0,0.25),transparent);
  background-size:200% 100%;
  animation:shimmerH 2.5s infinite;z-index:1;pointer-events:none;
}
/* ── Eroe ── */
.mbt-card.eroe {
  background:linear-gradient(160deg,#1a0033 0%,#4a0080 50%,#1a0033 100%);
  border:2px solid #9b59b6;
  box-shadow:0 6px 30px rgba(155,89,182,0.6);
  animation:pulseGlow 2s infinite;
  color:var(--rivals-purple);
  clip-path:polygon(6% 0%,50% 3%,94% 0%,100% 10%,97% 50%,100% 90%,94% 100%,6% 100%,0% 90%,3% 50%,0% 10%);
}
.mbt-card.eroe::before {
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 30%,rgba(155,89,182,0.3) 0%,transparent 70%);
  animation:holoSheen 3s infinite;z-index:1;pointer-events:none;
}
/* ── Leggenda ── */
.mbt-card.leggenda {
  background:linear-gradient(160deg,#1a1a1a 0%,#3a3a3a 50%,#1a1a1a 100%);
  border:2px solid #ffffff;
  box-shadow:0 8px 40px rgba(255,255,255,0.4),inset 0 0 20px rgba(255,255,255,0.05);
  clip-path:polygon(50% 0%,93% 7%,100% 50%,93% 93%,50% 100%,7% 93%,0% 50%,7% 7%);
}
.mbt-card.leggenda::before {
  content:'';position:absolute;inset:0;
  background:linear-gradient(45deg,transparent 30%,rgba(255,255,255,0.15) 50%,transparent 70%);
  background-size:200% 200%;
  animation:holographic 3s infinite;z-index:1;pointer-events:none;
}
/* ── TOTY ── */
.mbt-card.toty {
  background:linear-gradient(160deg,#000820 0%,#001855 50%,#000820 100%);
  border:3px solid #4169e1;
  box-shadow:0 8px 40px rgba(65,105,225,0.7),0 0 80px rgba(65,105,225,0.3);
  clip-path:polygon(10% 0%,90% 0%,100% 10%,100% 90%,90% 100%,10% 100%,0% 90%,0% 10%);
}
.mbt-card.toty::before {
  content:'';position:absolute;inset:-50%;
  background:conic-gradient(from 0deg,transparent 0deg,rgba(65,105,225,0.3) 30deg,transparent 60deg);
  animation:beamRotate 4s linear infinite;z-index:1;pointer-events:none;
}
.mbt-card.toty::after {
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,transparent 40%,rgba(65,105,225,0.2) 50%,transparent 60%);
  background-size:200% 200%;
  animation:holographic 2.5s infinite;z-index:2;pointer-events:none;
}
/* ── ICON BASE (OVR 100-104) ── */
.mbt-card.icon-base {
  background:linear-gradient(160deg,#1a0f00 0%,#3d2800 50%,#1a0f00 100%);
  border:3px solid #ffd700;
  box-shadow:0 10px 50px rgba(255,215,0,0.8),0 0 100px rgba(255,215,0,0.4);
  clip-path:polygon(50% 0%,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%);
}
.mbt-card.icon-base::before {
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 30% 20%,rgba(255,215,0,0.2) 0%,transparent 70%);
  animation:nebulaSwirl 8s infinite linear;z-index:1;pointer-events:none;
}
/* ── ICON EPICA (OVR 105-109) ── */
.mbt-card.icon-epica {
  background:linear-gradient(160deg,#1a0030 0%,#4a0090 50%,#1a0030 100%);
  border:3px solid #cc44ff;
  box-shadow:0 10px 60px rgba(180,0,255,0.9),0 0 120px rgba(130,0,200,0.5);
  clip-path:polygon(50% 0%,55% 35%,90% 10%,70% 45%,100% 50%,70% 55%,90% 90%,55% 65%,50% 100%,45% 65%,10% 90%,30% 55%,0% 50%,30% 45%,10% 10%,45% 35%);
}
.mbt-card.icon-epica::before {
  content:'';position:absolute;inset:-50%;
  background:conic-gradient(from 0deg,transparent 0deg,rgba(180,0,255,0.25) 30deg,transparent 60deg,rgba(100,0,200,0.2) 120deg,transparent 150deg);
  animation:nebulaSwirl 5s infinite linear;z-index:1;pointer-events:none;
}
/* ── ICON LEGGENDARIA (OVR 110-114) ── */
.mbt-card.icon-leggendaria {
  background:linear-gradient(160deg,#111 0%,#2a2a2a 50%,#111 100%);
  border:3px solid #ffffff;
  box-shadow:0 12px 70px rgba(255,255,255,0.9),0 0 140px rgba(255,255,255,0.5),inset 0 0 30px rgba(255,255,255,0.1);
  clip-path:polygon(50% 0%,56% 30%,93% 13%,67% 41%,100% 50%,67% 59%,93% 87%,56% 70%,50% 100%,44% 70%,7% 87%,33% 59%,0% 50%,33% 41%,7% 13%,44% 30%);
}
.mbt-card.icon-leggendaria::before {
  content:'';position:absolute;inset:0;
  background:linear-gradient(45deg,transparent 30%,rgba(255,255,255,0.15) 50%,transparent 70%);
  background-size:200% 200%;
  animation:holographic 2s infinite;z-index:1;pointer-events:none;
}
/* ── ICON TOTY (OVR 115-119) ── */
.mbt-card.icon-toty {
  background:linear-gradient(160deg,#000820 0%,#001060 50%,#000820 100%);
  border:4px solid #4169e1;
  box-shadow:0 15px 80px rgba(65,105,225,1),0 0 160px rgba(65,105,225,0.6),inset 0 0 40px rgba(65,105,225,0.2);
  clip-path:polygon(30% 0%,70% 0%,100% 30%,100% 70%,70% 100%,30% 100%,0% 70%,0% 30%);
}
.mbt-card.icon-toty::before {
  content:'';position:absolute;inset:-60%;
  background:conic-gradient(from 0deg,transparent,rgba(65,105,225,0.4),transparent,rgba(100,180,255,0.3),transparent);
  animation:beamRotate 3s linear infinite;z-index:1;pointer-events:none;
}
/* ── ICON GOD (OVR 120-125) ── */
.mbt-card.icon-god {
  background:linear-gradient(160deg,#0a0000 0%,#2a0000 30%,#000000 70%,#0a0000 100%);
  border:4px solid #ff2200;
  box-shadow:0 0 20px #ff2200,0 0 40px #880000,0 0 80px #440000;
  animation:iconGodPulse 1.5s infinite;
  clip-path:polygon(0% 15%,15% 0%,50% 5%,85% 0%,100% 15%,95% 50%,100% 85%,85% 100%,50% 95%,15% 100%,0% 85%,5% 50%,0% 15%);
}
.mbt-card.icon-god::before {
  content:'';position:absolute;inset:0;
  background:repeating-linear-gradient(
    -45deg,transparent,transparent 10px,
    rgba(255,30,0,0.06) 10px,rgba(255,30,0,0.06) 11px
  );
  animation:lightningFlash 2s infinite;z-index:1;pointer-events:none;
}

/* ── Card Inner ── */
.mbt-card-bg-image {
  position:absolute;inset:0;
  background-size:cover;background-position:center top;
  z-index:0;border-radius:inherit;
  transition:transform 0.4s ease;
}
.mbt-card-wrap:hover .mbt-card-bg-image {
  transform:scale(1.05);
}
.mbt-card-overlay {
  position:absolute;inset:0;z-index:1;pointer-events:none;border-radius:inherit;
}
.mbt-card-ovr {
  position:absolute;top:8px;left:8px;
  font-family:var(--font-rivals);font-size:1.4rem;font-weight:900;
  line-height:1;z-index:5;
  text-shadow:0 2px 8px rgba(0,0,0,0.8);
}
.mbt-card-tier-label {
  position:absolute;top:8px;right:8px;
  font-size:0.5rem;letter-spacing:2px;font-weight:700;opacity:0.9;
  text-transform:uppercase;z-index:5;
  text-shadow:0 1px 4px rgba(0,0,0,0.8);
}
.mbt-card-photo {
  width:100%;height:100px;object-fit:cover;object-position:top;
  display:block;position:relative;z-index:2;
}
.mbt-card-photo-placeholder {
  width:100%;height:100px;display:flex;align-items:center;justify-content:center;
  font-size:2.5rem;background:rgba(0,0,0,0.3);position:relative;z-index:2;
}
.mbt-card-name-block {
  position:relative;z-index:5;
  text-align:center;padding:2px 6px 0;
}
.mbt-card-firstname {
  font-family:var(--font-rivals);font-size:0.42rem;font-weight:400;
  letter-spacing:2px;text-transform:uppercase;opacity:0.75;
  display:block;line-height:1.2;
}
.mbt-card-lastname {
  font-family:var(--font-rivals);font-size:0.72rem;font-weight:900;
  letter-spacing:1px;text-transform:uppercase;
  display:block;line-height:1.1;
  text-shadow:0 1px 6px rgba(0,0,0,0.7);
}
.mbt-card-role {
  font-size:0.5rem;text-align:center;opacity:0.75;letter-spacing:2px;
  text-transform:uppercase;margin-bottom:4px;position:relative;z-index:5;
}
.mbt-card-stats {
  display:grid;grid-template-columns:1fr 1fr 1fr;gap:2px;padding:4px 6px 6px;
  position:relative;z-index:5;
  background:linear-gradient(0deg,rgba(0,0,0,0.6) 0%,transparent 100%);
}
.mbt-stat {
  text-align:center;
}
.mbt-stat-val {
  font-family:var(--font-rivals);font-size:0.75rem;font-weight:900;line-height:1;
  text-shadow:0 1px 4px rgba(0,0,0,0.8);
}
.mbt-stat-lbl {
  font-size:0.38rem;letter-spacing:1px;text-transform:uppercase;opacity:0.7;
}

/* ── Hover overlay ── */
.mbt-card-hover-overlay {
  position:absolute;inset:0;z-index:18;pointer-events:none;
  opacity:0;transition:opacity 0.3s;border-radius:inherit;
  background:radial-gradient(circle at var(--mx,50%) var(--my,50%),rgba(255,255,255,0.12) 0%,transparent 60%);
}
.mbt-card-wrap:hover .mbt-card-hover-overlay {opacity:1;}

/* ── Pack Opening ── */
.pack-container {
  perspective:1000px;
  display:flex;flex-direction:column;align-items:center;gap:20px;
  padding:40px 20px;
}
.pack-card {
  width:200px;height:280px;border-radius:16px;cursor:pointer;
  transition:transform 0.4s;position:relative;overflow:hidden;
  transform-style:preserve-3d;
}
.pack-card:hover {transform:rotateY(10deg) scale(1.05);}
.pack-base {
  background:linear-gradient(160deg,#2a1f0f 0%,#5a3a0f 50%,#2a1f0f 100%);
  border:3px solid #cd7f32;
  box-shadow:0 8px 30px rgba(205,127,50,0.5);
}
.pack-epico {
  background:linear-gradient(160deg,#1a0035 0%,#4a0080 50%,#1a0035 100%);
  border:3px solid #9b59b6;
  box-shadow:0 8px 40px rgba(155,89,182,0.7);
}
.pack-leggenda {
  background:linear-gradient(160deg,#0a0000 0%,#2a0000 50%,#0a0000 100%);
  border:4px solid #ff6600;
  box-shadow:0 10px 60px rgba(255,102,0,0.8),0 0 120px rgba(255,50,0,0.4);
}
.pack-label {
  position:absolute;bottom:20px;width:100%;text-align:center;
  font-family:var(--font-rivals);font-size:1rem;font-weight:900;letter-spacing:3px;
}
.pack-price {
  position:absolute;bottom:6px;width:100%;text-align:center;
  font-family:var(--font-rivals);font-size:0.7rem;opacity:0.8;
}

/* ── Battle UI ── */
.battle-arena {
  background:linear-gradient(180deg,#030308 0%,#0a0a18 50%,#030308 100%);
  border:2px solid #1e1e3a;
  border-radius:16px;
  padding:20px;
  min-height:500px;
  position:relative;
}
.hp-bar-container {
  height:20px;background:#1a1a2a;border-radius:10px;overflow:hidden;
  border:1px solid var(--rivals-border);position:relative;
}
.hp-bar-fill {
  height:100%;border-radius:10px;transition:width 0.5s ease;
  background:linear-gradient(90deg,#16a34a,#4ade80);
}
.hp-bar-fill.danger {
  background:linear-gradient(90deg,#dc2626,#ef4444);
  animation:pulseGlow 1s infinite;
}
.battle-card-slot {
  border:2px solid #1e1e3a;border-radius:10px;padding:10px;
  background:rgba(255,255,255,0.02);min-height:180px;
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;transition:border-color 0.2s,background 0.2s;
}
.battle-card-slot.active {
  border-color:#ffd700;background:rgba(255,215,0,0.05);
}
.battle-card-slot:hover {
  border-color:#4169e1;background:rgba(65,105,225,0.05);
}
.move-btn {
  border:2px solid;border-radius:8px;padding:8px 14px;cursor:pointer;
  font-family:var(--font-rivals);font-size:0.7rem;font-weight:700;
  letter-spacing:1px;text-transform:uppercase;transition:all 0.2s;
  background:rgba(0,0,0,0.5);
}
.move-btn:hover {transform:scale(1.05);filter:brightness(1.3);}
.move-btn.attack {border-color:#dc2626;color:#ef4444;}
.move-btn.special {border-color:#ffd700;color:#ffd700;}
.move-btn.defend {border-color:#4169e1;color:#60a5fa;}
.battle-log {
  background:#05050f;border:1px solid #1e1e3a;border-radius:8px;
  padding:10px;max-height:200px;overflow-y:auto;
  font-family:var(--font-body);font-size:0.75rem;
}

/* ── Arena ── */
.arena-badge {
  border-radius:10px;padding:16px;text-align:center;cursor:pointer;
  transition:transform 0.2s,box-shadow 0.2s;position:relative;overflow:hidden;
}
.arena-badge:hover {transform:translateY(-4px);}
.arena-base {background:linear-gradient(135deg,#2a1f0f,#5a3a0f);border:2px solid #cd7f32;}
.arena-epica {background:linear-gradient(135deg,#1a003a,#4a0080);border:2px solid #9b59b6;}
.arena-leggendaria {background:linear-gradient(135deg,#0a0a0a,#2a2a2a);border:2px solid #fff;}
.arena-toty {background:linear-gradient(135deg,#000820,#001855);border:2px solid #4169e1;}
.arena-icona {background:linear-gradient(135deg,#1a0f00,#3d2800);border:3px solid #ffd700;}
.arena-icona-epica {background:linear-gradient(135deg,#1a0030,#4a0090);border:3px solid #cc44ff;}
.arena-icona-leggendaria {background:linear-gradient(135deg,#111,#2a2a2a);border:3px solid #fff;box-shadow:0 0 30px rgba(255,255,255,0.3);}
.arena-toty-plus {background:linear-gradient(135deg,#000820,#001060);border:4px solid #4169e1;box-shadow:0 0 30px rgba(65,105,225,0.5);}
.arena-god {background:linear-gradient(135deg,#0a0000,#2a0000);border:4px solid #ff2200;box-shadow:0 0 40px rgba(255,34,0,0.6);}
.arena-omega {background:linear-gradient(135deg,#000,#000);border:4px solid transparent;
  background-clip:padding-box;box-shadow:0 0 60px rgba(255,0,200,0.8),0 0 120px rgba(0,100,255,0.6);}

/* ── Collection ── */
.collection-filter-btn {
  border:1px solid;border-radius:20px;padding:4px 12px;cursor:pointer;
  font-size:0.7rem;font-family:var(--font-rivals);transition:all 0.2s;
  background:transparent;
}
.collection-filter-btn.active {background:var(--rivals-gold);border-color:var(--rivals-gold);color:#000;}
.collection-filter-btn:not(.active) {color:var(--rivals-gold);border-color:#555;}

/* ── Admin Card Creator ── */
.creator-preview-wrap {
  display:flex;justify-content:center;padding:20px;
  background:radial-gradient(ellipse at center,rgba(255,215,0,0.05) 0%,transparent 70%);
  border-radius:12px;border:1px dashed #333;
}
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
        "mbt_coins": 500,
        "trofei_rivals": 0,
        "collection": [],          # lista card_id possedute
        "active_team": [],         # max 5 card_id
        "arena_unlocked": 1,
        "battle_wins": 0,
        "battle_losses": 0,
        "special_moves_learned": [],
        "superpowers": {},          # {power_id: level}
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

ROLE_DESCRIPTIONS = {
    "SPIKER": "Super Attacco: Nocchino di Ghiaccio – attacco che non fallisce mai",
    "IRONBLOCKER": "Fortezza di Titanio (Annulla danni) o Muro Corna (danno+difesa)",
    "DIFENSORE": "Dig Classico / Sky Dive / Sabbia Mobile (recupera HP)",
    "ACER": "Jump Float Infuocato – danni critici doppi se vince il turno battuta",
    "SPECIALISTA": "Seconda Intenzione – attacca nel turno difesa",
    "TRAINER - Fisioterapista": "Riduce consumo Stamina del 20%",
    "TRAINER - Mental Coach": "Aumenta danni Super quando HP < 30%",
    "TRAINER - Scoutman": "Vedi in anticipo la prima carta CPU",
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

# Mapping tier → nome file immagine carta (in assets/card_templates/)
TIER_CARD_IMAGES = {
    "Bronzo Comune":    "BRONZO_png.webp",
    "Bronzo Raro":      "BRONZO_RARO_png.webp",
    "Argento Comune":   "ARGENTO.png",
    "Argento Raro":     "argento_raro_png.webp",
    "Oro Comune":       "gold3.png",
    "Oro Raro":         "ORO_RARO_png.webp",
    "Eroe":             "EROE.png",
    "IF (In Form)":     "EROE.png",
    "Leggenda":         "LEGGENDA.png",
    "TOTY":             "TOTY.webp",
    "TOTY Evoluto":     "TOTY_EVOLUTO.png",
    "GOAT":             "GOAT_png.webp",
    "ICON BASE":        "ICON_BASE.png",
    "ICON EPICA":       "ICON_BASE.png",
    "ICON LEGGENDARIA": "ICON_LEGGENDARIA.png",
    "ICON TOTY":        "ICON_TOTY_png.webp",
    "ICON GOD":         "ICONA_GOD.png",
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
        "css_class": "pack-base",
        "label_color": "#cd7f32",
        "description": "6 carte | Comuni e Rare",
        "weights": {
            "Bronzo Comune":0.30, "Bronzo Raro":0.25, "Argento Comune":0.20,
            "Argento Raro":0.12, "Oro Comune":0.07, "Oro Raro":0.04,
            "Eroe":0.015, "IF (In Form)":0.005
        }
    },
    "Epico": {
        "price": 500,
        "css_class": "pack-epico",
        "label_color": "#9b59b6",
        "description": "6 carte | Da Oro a Leggenda",
        "weights": {
            "Oro Comune":0.25, "Oro Raro":0.22, "Eroe":0.18,
            "IF (In Form)":0.15, "Leggenda":0.08, "TOTY":0.04,
            "TOTY Evoluto":0.02, "GOAT":0.01,
            "ICON BASE":0.008, "ICON EPICA":0.002
        }
    },
    "Leggenda": {
        "price": 1200,
        "css_class": "pack-leggenda",
        "label_color": "#ff6600",
        "description": "6 carte | Alta probabilità di Speciali",
        "weights": {
            "Leggenda":0.25, "TOTY":0.20, "TOTY Evoluto":0.18,
            "GOAT":0.12, "ICON BASE":0.10, "ICON EPICA":0.07,
            "ICON LEGGENDARIA":0.04, "ICON TOTY":0.02, "ICON GOD":0.01,
            "IF (In Form)":0.01
        }
    },
}

ARENE = [
    {"min_level":1,  "max_level":2,  "name":"Arena Base",            "css":"arena-base",             "color":"#cd7f32", "icon":"🏟️"},
    {"min_level":3,  "max_level":4,  "name":"Arena Epica",           "css":"arena-epica",            "color":"#9b59b6", "icon":"⚡"},
    {"min_level":5,  "max_level":6,  "name":"Arena Leggendaria",     "css":"arena-leggendaria",      "color":"#ffffff", "icon":"👑"},
    {"min_level":7,  "max_level":8,  "name":"Arena TOTY",            "css":"arena-toty",             "color":"#4169e1", "icon":"🌟"},
    {"min_level":9,  "max_level":10, "name":"Arena ICONA",           "css":"arena-icona",            "color":"#ffd700", "icon":"🏆"},
    {"min_level":11, "max_level":12, "name":"Arena ICONA EPICA",     "css":"arena-icona-epica",      "color":"#cc44ff", "icon":"💫"},
    {"min_level":13, "max_level":14, "name":"Arena ICONA LEGGEND.",  "css":"arena-icona-leggendaria","color":"#ffffff", "icon":"✨"},
    {"min_level":15, "max_level":16, "name":"Arena TOTY SUPREMA",    "css":"arena-toty-plus",        "color":"#4169e1", "icon":"🔮"},
    {"min_level":17, "max_level":18, "name":"Arena GOD MODE",        "css":"arena-god",              "color":"#ff2200", "icon":"🔥"},
    {"min_level":19, "max_level":20, "name":"Arena OMEGA",           "css":"arena-omega",            "color":"#ff00cc", "icon":"⚜️"},
]

XP_PER_LEVEL = [0, 100, 250, 450, 700, 1000, 1350, 1750, 2200, 2700,
                3250, 3850, 4500, 5200, 5950, 6750, 7600, 8500, 9450, 10450]

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


# ─── CARD BACKGROUND IMAGE HELPER ─────────────────────────────────────────────

def _get_card_bg_b64(tier_name):
    """Restituisce base64 dell'immagine di sfondo per il tier, cercando in assets/ e uploads."""
    img_filename = TIER_CARD_IMAGES.get(tier_name, "")
    if not img_filename:
        return None, None

    # Cerca prima in assets/card_templates, poi in assets/icons, poi nella directory uploads
    search_paths = [
        os.path.join(ASSETS_CARDS_DIR, img_filename),
        os.path.join("assets", img_filename),
        os.path.join("assets/icons", img_filename),
        # Se in esecuzione su ambiente con uploads montati
        os.path.join("/mnt/user-data/uploads", img_filename),
    ]
    for p in search_paths:
        if os.path.exists(p):
            ext = img_filename.rsplit(".", 1)[-1].lower()
            mime = {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg",
                    "webp":"image/webp","gif":"image/gif"}.get(ext,"image/png")
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return b64, mime
    return None, None


# ─── CARD RENDERING ───────────────────────────────────────────────────────────

def render_card_html(card_data, size="normal", show_special_effects=True):
    """Genera HTML completo per una carta MBT con tutti gli effetti v2.0."""
    ovr = card_data.get("overall", 40)
    tier_name = get_tier_by_ovr(ovr)
    tier_info = CARD_TIERS.get(tier_name, CARD_TIERS["Bronzo Comune"])
    css_class = tier_info["css"]
    color = tier_info["color"]
    nome = card_data.get("nome", "Unknown")
    cognome = card_data.get("cognome", "")
    role = card_data.get("ruolo", "SPIKER")
    role_icon = ROLE_ICONS.get(role, "⚡")
    photo_path = card_data.get("foto_path", "")

    # Stats
    atk = card_data.get("attacco", 40)
    dif = card_data.get("difesa", 40)
    ric = card_data.get("ricezione", 40)
    bat = card_data.get("battuta", 40)
    mur = card_data.get("muro", 40)
    alz = card_data.get("alzata", 40)

    width = "140px" if size == "normal" else "100px" if size == "small" else "180px"
    font_ovr = "1.4rem" if size == "normal" else "1rem" if size == "small" else "1.8rem"
    font_name = "0.72rem" if size == "normal" else "0.52rem" if size == "small" else "0.9rem"
    font_first = "0.42rem" if size == "normal" else "0.32rem" if size == "small" else "0.52rem"

    # Immagine di sfondo tier
    bg_b64, bg_mime = _get_card_bg_b64(tier_name)
    if bg_b64:
        bg_style = "background-image:url('data:{};base64,{}');background-size:cover;background-position:center top;".format(bg_mime, bg_b64)
        bg_div = '<div class="mbt-card-bg-image" style="{}"></div>'.format(bg_style)
    else:
        bg_div = ""

    # Overlay gradient sopra l'immagine di sfondo
    overlay_gradient = "linear-gradient(180deg,rgba(0,0,0,0.25) 0%,rgba(0,0,0,0.1) 40%,rgba(0,0,0,0.7) 75%,rgba(0,0,0,0.85) 100%)"
    overlay_div = '<div class="mbt-card-overlay" style="background:{};"></div>'.format(overlay_gradient)

    # Foto atleta sopra sfondo
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        foto_html = '<img class="mbt-card-photo" src="data:image/jpeg;base64,{}" style="opacity:0.85">'.format(b64)
    else:
        foto_html = '<div class="mbt-card-photo-placeholder">{}</div>'.format(role_icon)

    # Effetti speciali ICON e rare
    special_overlay = ""
    if show_special_effects:
        rarity = tier_info.get("rarity", 0)

        if css_class == "icon-god":
            # Fire effect + SVG cracks animate
            special_overlay = """
            <div style="position:absolute;inset:0;pointer-events:none;z-index:6;overflow:hidden;border-radius:inherit">
                <div style="position:absolute;bottom:0;left:0;right:0;height:45%;
                    background:linear-gradient(0deg,rgba(255,40,0,0.5),rgba(255,100,0,0.2),transparent);
                    animation:fireFlicker 0.4s infinite alternate"></div>
                <div style="position:absolute;top:15%;left:48%;width:3px;height:70%;
                    background:linear-gradient(180deg,rgba(255,255,0,0.9),transparent);
                    transform:rotate(8deg);animation:lightningFlash 1.2s infinite;
                    box-shadow:0 0 8px #ffff00"></div>
                <div style="position:absolute;top:20%;left:30%;width:2px;height:50%;
                    background:linear-gradient(180deg,rgba(255,200,0,0.7),transparent);
                    transform:rotate(-15deg);animation:lightningFlash 1.8s 0.3s infinite;
                    box-shadow:0 0 6px #ffaa00"></div>
                <svg style="position:absolute;inset:0;width:100%;height:100%;z-index:7;opacity:0.6" viewBox="0 0 140 200">
                    <path d="M20,40 L80,80 L40,120 L100,160" stroke="#ff3300" stroke-width="1.5"
                        fill="none" stroke-dasharray="10,5" style="animation:cracksAnimate 2s infinite;stroke-dashoffset:100"/>
                    <path d="M110,30 L60,90 L120,130" stroke="#ff6600" stroke-width="1"
                        fill="none" stroke-dasharray="8,4" style="animation:cracksAnimate 2.5s 0.5s infinite;stroke-dashoffset:100"/>
                </svg>
            </div>"""

        elif css_class == "icon-toty":
            # Beam + particles
            particles = ""
            for i in range(6):
                dx = random.randint(-25, 25)
                dy = random.randint(-45, -10)
                delay = random.uniform(0, 2.5)
                dur = random.uniform(1.5, 3)
                particles += '<div style="position:absolute;width:3px;height:3px;background:{};border-radius:50%;top:{}%;left:{}%;animation:driftParticle {}s {}s infinite;--dx:{}px;--dy:{}px;z-index:8;box-shadow:0 0 4px {}"></div>'.format(
                    color, random.randint(20,75), random.randint(10,90),
                    dur, delay, dx, dy, color)
            special_overlay = '<div style="position:absolute;inset:0;pointer-events:none;z-index:6;overflow:hidden">{}</div>'.format(particles)

        elif css_class in ("icon-leggendaria", "icon-epica"):
            # Particles + holographic sheen
            particles = ""
            for i in range(5):
                dx = random.randint(-20, 20)
                dy = random.randint(-40, -8)
                delay = random.uniform(0, 3)
                dur = random.uniform(2, 4)
                particles += '<div style="position:absolute;width:3px;height:3px;background:{};border-radius:50%;top:{}%;left:{}%;animation:driftParticle {}s {}s infinite;--dx:{}px;--dy:{}px;z-index:8"></div>'.format(
                    color, random.randint(25,70), random.randint(15,85),
                    dur, delay, dx, dy)
            special_overlay = '<div style="position:absolute;inset:0;pointer-events:none;z-index:6;overflow:hidden">{}</div>'.format(particles)

        elif css_class == "icon-base":
            particles = ""
            for i in range(4):
                dx = random.randint(-15, 15)
                dy = random.randint(-30, -8)
                delay = random.uniform(0, 2)
                particles += '<div style="position:absolute;width:2px;height:2px;background:{};border-radius:50%;top:{}%;left:{}%;animation:driftParticle 2.5s {}s infinite;--dx:{}px;--dy:{}px;z-index:8"></div>'.format(
                    color, random.randint(30,70), random.randint(20,80),
                    delay, dx, dy)
            special_overlay = '<div style="position:absolute;inset:0;pointer-events:none;z-index:6;overflow:hidden">{}</div>'.format(particles)

        elif css_class == "toty":
            # Beam conic ring
            special_overlay = '<div style="position:absolute;inset:0;pointer-events:none;z-index:6;overflow:hidden;border-radius:inherit"><div style="position:absolute;inset:-30px;background:conic-gradient(from 0deg,transparent 0deg,rgba(65,105,225,0.2) 30deg,transparent 60deg);animation:beamRotate 4s linear infinite;border-radius:50%"></div></div>'

        elif css_class == "leggenda":
            # Holographic sheen
            special_overlay = '<div style="position:absolute;inset:0;pointer-events:none;z-index:6;overflow:hidden;border-radius:inherit"><div style="position:absolute;inset:0;background:linear-gradient(135deg,transparent 30%,rgba(255,255,255,0.1) 50%,transparent 70%);background-size:200% 200%;animation:holographic 2.5s infinite"></div></div>'

        elif rarity >= 5:  # Oro Raro+
            # Shimmer
            special_overlay = '<div style="position:absolute;inset:0;pointer-events:none;z-index:6;overflow:hidden;border-radius:inherit"><div style="position:absolute;top:0;left:-100%;width:50%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,215,0,0.2),transparent);animation:shimmer 2s infinite;border-radius:inherit"></div></div>'

    # Hover overlay (radial glow)
    hover_overlay = '<div class="mbt-card-hover-overlay"></div>'

    # Firma su hover per carte ICON
    hover_sign = ""
    if css_class.startswith("icon"):
        hover_sign = '<div class="card-signature" style="position:absolute;bottom:72px;width:100%;text-align:center;font-family:cursive;font-size:0.75rem;color:{};opacity:0;transition:opacity 0.35s;z-index:15;text-shadow:0 0 10px {}">✦ {} ✦</div>'.format(color, color, cognome or nome)

    # Build HTML — nessun tag Python visibile
    html = (
        '<div class="mbt-card-wrap" style="width:{width}">'
        '<div class="mbt-card {css}" style="width:{width}">'
        '{bg}{overlay}'
        '<div class="mbt-card-ovr" style="color:{color};font-size:{fovr}">{ovr}</div>'
        '<div class="mbt-card-tier-label" style="color:{color}">{tier_short}</div>'
        '{foto}'
        '<div class="mbt-card-name-block">'
        '<span class="mbt-card-firstname" style="color:{color}">{nome}</span>'
        '<span class="mbt-card-lastname" style="color:{color};font-size:{fname}">{cognome}</span>'
        '</div>'
        '<div class="mbt-card-role" style="color:{color}">{role_icon} {role}</div>'
        '<div class="mbt-card-stats">'
        '<div class="mbt-stat"><div class="mbt-stat-val" style="color:{color}">{atk}</div><div class="mbt-stat-lbl">ATK</div></div>'
        '<div class="mbt-stat"><div class="mbt-stat-val" style="color:{color}">{dif}</div><div class="mbt-stat-lbl">DEF</div></div>'
        '<div class="mbt-stat"><div class="mbt-stat-val" style="color:{color}">{bat}</div><div class="mbt-stat-lbl">BAT</div></div>'
        '</div>'
        '{special}{hover}{sign}'
        '</div>'
        '</div>'
        '<style>.mbt-card-wrap:hover .card-signature{{opacity:1!important;}}</style>'
    ).format(
        width=width,
        css=css_class,
        bg=bg_div,
        overlay=overlay_div,
        color=color,
        fovr=font_ovr,
        ovr=ovr,
        tier_short=(tier_name.split()[0] if len(tier_name.split()) > 1 else tier_name),
        foto=foto_html,
        nome=nome.upper() if not cognome else nome.upper(),
        cognome=cognome.upper() if cognome else nome.upper(),
        fname=font_name,
        role_icon=role_icon,
        role=role,
        atk=atk,
        dif=dif,
        bat=bat,
        special=special_overlay,
        hover=hover_overlay,
        sign=hover_sign,
    )
    return html


# ─── PACK OPENING ─────────────────────────────────────────────────────────────

def draw_cards_from_pack(pack_name, cards_db):
    """Pesca 6 carte da un pacchetto secondo le probabilità."""
    pack_info = PACKS[pack_name]
    weights = pack_info["weights"]
    tiers = list(weights.keys())
    probs = list(weights.values())
    # Normalizza
    total = sum(probs)
    probs = [p/total for p in probs]

    drawn = []
    all_cards = cards_db.get("cards", [])

    for _ in range(6):
        chosen_tier = random.choices(tiers, weights=probs, k=1)[0]
        # Cerca carte di quel tier nel DB
        matching = [c for c in all_cards if get_tier_by_ovr(c.get("overall",40)) == chosen_tier]
        if matching:
            card = random.choice(matching).copy()
        else:
            # Genera carta generica del tier
            tier_info = CARD_TIERS.get(chosen_tier, CARD_TIERS["Bronzo Comune"])
            lo, hi = tier_info["ovr_range"]
            ovr = random.randint(lo, hi)
            card = {
                "id": "gen_{}".format(random.randint(100000,999999)),
                "nome": random.choice(["Marco","Luca","Andrea","Fabio","Simone","Giulio","Matteo","Riccardo"]),
                "cognome": random.choice(["Rossi","Bianchi","Ferrari","Conti","Esposito","Costa","Ricci","Serra"]),
                "overall": ovr,
                "ruolo": random.choice(list(ROLE_ICONS.keys())[:5]),
                "attacco": max(40, ovr - random.randint(0,15)),
                "difesa": max(40, ovr - random.randint(0,15)),
                "muro": max(40, ovr - random.randint(0,20)),
                "ricezione": max(40, ovr - random.randint(0,20)),
                "battuta": max(40, ovr - random.randint(0,18)),
                "alzata": max(40, ovr - random.randint(0,20)),
                "foto_path": "",
                "tier": chosen_tier,
                "generated": True,
            }
        card["instance_id"] = "inst_{}".format(random.randint(1000000,9999999))
        drawn.append(card)

    return drawn


# ─── ANIMAZIONE APERTURA PACK ─────────────────────────────────────────────────

def render_pack_opening_animation(drawn_cards, pack_name):
    """Mostra le carte una per una con animazioni dinamiche v2.0."""
    st.markdown("""
    <style>
    @keyframes cardFlip {
        0%{transform:rotateY(0deg) scale(0.8);opacity:0}
        40%{transform:rotateY(90deg) scale(1.1)}
        100%{transform:rotateY(0deg) scale(1);opacity:1}
    }
    @keyframes screenTremor {
        0%,100%{transform:translate(0,0) rotate(0deg)}
        10%{transform:translate(-10px,5px) rotate(-1deg)}
        20%{transform:translate(10px,-5px) rotate(1deg)}
        30%{transform:translate(-8px,8px) rotate(-0.5deg)}
        40%{transform:translate(8px,-3px) rotate(0.5deg)}
        50%{transform:translate(-4px,4px)}
        60%{transform:translate(4px,-4px)}
    }
    @keyframes cardFlipIn {
        0%{transform:rotateY(90deg) scale(0.8);opacity:0;filter:brightness(3)}
        50%{transform:rotateY(-10deg) scale(1.05)}
        100%{transform:rotateY(0deg) scale(1);opacity:1;filter:brightness(1)}
    }
    @keyframes godReveal {
        0%{transform:scale(0.5) rotate(-10deg);opacity:0;filter:brightness(5) saturate(3)}
        60%{transform:scale(1.2) rotate(2deg);opacity:1;filter:brightness(2)}
        100%{transform:scale(1) rotate(0deg);opacity:1;filter:brightness(1)}
    }
    .pack-revealed-card {animation:cardFlipIn 0.7s cubic-bezier(0.34,1.56,0.64,1) both;}
    .pack-revealed-card-god {animation:godReveal 1s cubic-bezier(0.34,1.56,0.64,1) both;}
    .screen-shake-container.shaking {animation:screenTremor 0.5s ease;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 🎁 Apertura Pacchetto **{}** — Hai trovato:".format(pack_name))

    cols = st.columns(6)
    for i, card in enumerate(drawn_cards):
        tier = get_tier_by_ovr(card.get("overall", 40))
        rarity = CARD_TIERS.get(tier, {}).get("rarity", 0)
        tier_color = CARD_TIERS.get(tier, {}).get("color","#fff")

        with cols[i]:
            delay = i * 0.15
            anim_class = "pack-revealed-card-god" if rarity >= 16 else "pack-revealed-card"

            if rarity >= 12:  # ICON
                st.markdown(
                    '<div class="{}" style="animation-delay:{}s">{}</div>'
                    '<div style="text-align:center;font-size:0.6rem;color:{};margin-top:4px;'
                    'font-weight:700;letter-spacing:2px;text-shadow:0 0 8px {}">⚡ {} ⚡</div>'.format(
                        anim_class, delay,
                        render_card_html(card, size="small"),
                        tier_color, tier_color, tier
                    ), unsafe_allow_html=True)
            elif rarity >= 8:  # Leggenda+
                st.markdown(
                    '<div class="pack-revealed-card" style="animation-delay:{}s">{}</div>'
                    '<div style="text-align:center;font-size:0.55rem;color:{};margin-top:4px">'
                    '✦ {} ✦</div>'.format(
                        delay, render_card_html(card, size="small"), tier_color, tier
                    ), unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="pack-revealed-card" style="animation-delay:{}s">{}</div>'
                    '<div style="text-align:center;font-size:0.5rem;color:#888;margin-top:4px">{}</div>'.format(
                        delay, render_card_html(card, size="small"), tier
                    ), unsafe_allow_html=True)


# ─── BATTLE ENGINE ────────────────────────────────────────────────────────────

def init_battle_state(player_cards, cpu_level=1):
    """Inizializza lo stato di una partita MBT RIVALS."""
    def make_fighter(card, is_cpu=False):
        ovr = card.get("overall", 40)
        base_hp = 80 + ovr * 2
        if is_cpu:
            base_hp = int(base_hp * (0.9 + cpu_level * 0.1))
        return {
            "card": card,
            "hp": base_hp,
            "max_hp": base_hp,
            "stamina": 100,
            "shield": 0,
            "status": None,
        }

    player_fighters = [make_fighter(c) for c in player_cards[:3]]

    # CPU team generato casualmente proporzionale al livello
    cpu_ovr_base = 40 + cpu_level * 4
    cpu_cards = []
    for _ in range(3):
        ovr = min(99, cpu_ovr_base + random.randint(-5, 10))
        cpu_cards.append({
            "nome": random.choice(["Robot","CPU","AI","BOT"]),
            "overall": ovr,
            "ruolo": random.choice(list(ROLE_ICONS.keys())[:5]),
            "attacco": max(40, ovr - random.randint(0, 10)),
            "difesa": max(40, ovr - random.randint(0, 10)),
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
        "phase": "battle",   # battle / win / lose
        "log": [],
        "stamina_charges": 0,
        "start_time": time.time(),
        "time_limit": 300,  # 5 minuti
    }


def calculate_damage(attacker_card, defender_card, move_type="attack", superpowers=None):
    """Calcola danno con pesi statistiche e superpowers."""
    atk = attacker_card.get("attacco", 40)
    def_ = defender_card.get("difesa", 40)
    base = max(5, (atk - def_ * 0.6) * 0.4 + random.randint(3, 12))

    if move_type == "special":
        base *= 1.8
    elif move_type == "super":
        base *= 2.5

    if superpowers:
        kill_shot_lvl = superpowers.get("kill_shot", 0)
        base *= (1 + kill_shot_lvl * 0.08)

    return max(5, int(base))


def cpu_choose_action(cpu_fighter, player_fighter, turn):
    """IA semplice per la CPU."""
    hp_ratio = cpu_fighter["hp"] / cpu_fighter["max_hp"]
    actions = ["attack", "attack", "attack", "defend"]
    if hp_ratio < 0.3:
        actions = ["attack", "attack", "special", "defend"]
    if cpu_fighter["stamina"] >= 50 and random.random() < 0.3:
        return "special"
    return random.choice(actions)


def process_battle_action(battle_state, action, rivals_data):
    """Processa un'azione in battaglia."""
    p_idx = battle_state["player_active_idx"]
    c_idx = battle_state["cpu_active_idx"]
    p_fighter = battle_state["player_fighters"][p_idx]
    c_fighter = battle_state["cpu_fighters"][c_idx]
    log = battle_state["log"]
    superpowers = rivals_data.get("superpowers", {})

    # Turno giocatore
    player_name = p_fighter["card"].get("nome","Player")
    cpu_name = c_fighter["card"].get("nome","CPU")

    if action == "attack":
        dmg = calculate_damage(p_fighter["card"], c_fighter["card"], "attack", superpowers)
        c_fighter["hp"] = max(0, c_fighter["hp"] - dmg)
        p_fighter["stamina"] = min(100, p_fighter["stamina"] + 10)
        log.append("⚡ {} attacca → {} danni! (HP CPU: {})".format(player_name, dmg, c_fighter['hp']))
        battle_state["stamina_charges"] += 1

    elif action == "special":
        if p_fighter["stamina"] >= 40:
            dmg = calculate_damage(p_fighter["card"], c_fighter["card"], "special", superpowers)
            c_fighter["hp"] = max(0, c_fighter["hp"] - dmg)
            p_fighter["stamina"] -= 40
            log.append("🔥 {} SUPER ATTACCO → {} danni! BOOM!".format(player_name, dmg))
        else:
            log.append("⚠️ Stamina insufficiente per Super Attacco!")

    elif action == "defend":
        p_fighter["shield"] = 30
        p_fighter["stamina"] = min(100, p_fighter["stamina"] + 20)
        log.append("🛡️ {} si difende! Scudo attivato.".format(player_name))

    elif action == "final":
        if battle_state["stamina_charges"] >= 10:
            dmg = calculate_damage(p_fighter["card"], c_fighter["card"], "super", superpowers)
            c_fighter["hp"] = max(0, c_fighter["hp"] - dmg)
            battle_state["stamina_charges"] = 0
            log.append("💥 MOSSA FINALE! {} → {} danni DEVASTANTI!".format(player_name, dmg))
        else:
            log.append("⚠️ Carica la Stamina per la Mossa Finale (10 attacchi)!")

    # Controlla HP CPU
    if c_fighter["hp"] <= 0:
        next_cpu = c_idx + 1
        if next_cpu < len(battle_state["cpu_fighters"]):
            battle_state["cpu_active_idx"] = next_cpu
            log.append("💀 {} è stato eliminato! Prossimo avversario!".format(cpu_name))
        else:
            battle_state["phase"] = "win"
            log.append("🏆 HAI VINTO LA PARTITA!")
            return

    # Turno CPU
    if battle_state["phase"] == "battle":
        cpu_action = cpu_choose_action(c_fighter, p_fighter, battle_state["turn"])
        if cpu_action == "attack":
            cpu_dmg = calculate_damage(c_fighter["card"], p_fighter["card"], "attack")
            if p_fighter["shield"] > 0:
                cpu_dmg = max(0, cpu_dmg - p_fighter["shield"])
                p_fighter["shield"] = 0
                log.append("🛡️ Scudo! {} attacca → {} danni dopo difesa".format(cpu_name, cpu_dmg))
            else:
                log.append("🤖 {} attacca → {} danni!".format(cpu_name, cpu_dmg))
            p_fighter["hp"] = max(0, p_fighter["hp"] - cpu_dmg)
        elif cpu_action == "special":
            cpu_dmg = calculate_damage(c_fighter["card"], p_fighter["card"], "special")
            log.append("💫 {} SUPER MOSSA → {} danni!".format(cpu_name, cpu_dmg))
            p_fighter["hp"] = max(0, p_fighter["hp"] - cpu_dmg)
        elif cpu_action == "defend":
            c_fighter["shield"] = 25
            log.append("🤖 {} si difende!".format(cpu_name))

    # Controlla HP player
    if p_fighter["hp"] <= 0:
        next_p = p_idx + 1
        if next_p < len(battle_state["player_fighters"]):
            battle_state["player_active_idx"] = next_p
            log.append("💔 {} KO! Prossima carta!".format(player_name))
        else:
            battle_state["phase"] = "lose"
            log.append("💀 HAI PERSO! Le tue carte sono cadute tutte!")

    battle_state["turn"] += 1
    # Mantieni solo ultimi 20 log
    if len(log) > 20:
        battle_state["log"] = log[-20:]


# ─── SEZIONI UI ───────────────────────────────────────────────────────────────

def render_mbt_rivals(state):
    """Entry point principale per la sezione MBT RIVALS."""
    st.markdown(RIVALS_CSS, unsafe_allow_html=True)

    rivals_data = st.session_state.get("rivals_data")
    if rivals_data is None:
        rivals_data = load_rivals_data()
        st.session_state.rivals_data = rivals_data

    cards_db = st.session_state.get("cards_db")
    if cards_db is None:
        cards_db = load_cards_db()
        st.session_state.cards_db = cards_db

    # Sync OVR dalle carte atleti del torneo (collegamento torneo ↔ rivals)
    _sync_ovr_from_tournament(state, cards_db)

    # Header
    level = rivals_data["player_level"]
    xp = rivals_data["player_xp"]
    coins = rivals_data["mbt_coins"]
    xp_needed = XP_PER_LEVEL[min(level, 19)] if level < 20 else 99999
    xp_pct = min(100, int(xp / max(xp_needed, 1) * 100))

    # Trova arena
    current_arena = next((a for a in ARENE if a["min_level"] <= level <= a["max_level"]), ARENE[0])

    st.markdown("""
    <div style="background:linear-gradient(135deg,#080810,#10101e,#080810);
        border:2px solid #1e1e3a;border-radius:16px;padding:16px 24px;margin-bottom:20px;
        display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
        <div>
            <div style="font-family:'Orbitron',sans-serif;font-size:1.6rem;font-weight:900;
                background:linear-gradient(90deg,#ffd700,#ffec4a,#ffd700);
                background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
                animation:goldShine 3s linear infinite">
                ⚡ MBT RIVALS
            </div>
            <div style="font-size:0.75rem;color:#666;letter-spacing:3px;margin-top:2px">
                CARD BATTLE SYSTEM
            </div>
        </div>
        <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:center">
            <div style="text-align:center">
                <div style="font-family:'Orbitron',sans-serif;font-size:1.2rem;font-weight:900;color:#ffd700">LV.{level}</div>
                <div style="font-size:0.6rem;color:#888;letter-spacing:2px">LIVELLO</div>
                <div style="width:80px;height:6px;background:#1a1a2a;border-radius:3px;margin-top:4px;overflow:hidden">
                    <div style="width:{xp_pct}%;height:100%;background:linear-gradient(90deg,#ffd700,#ffec4a);border-radius:3px;transition:width 0.5s"></div>
                </div>
                <div style="font-size:0.5rem;color:#666;margin-top:2px">{xp}/{xp_needed} XP</div>
            </div>
            <div style="text-align:center">
                <div style="font-family:'Orbitron',sans-serif;font-size:1.2rem;font-weight:900;color:#ffd700">🪙 {coins}</div>
                <div style="font-size:0.6rem;color:#888;letter-spacing:2px">MBT COINS</div>
            </div>
            <div style="text-align:center">
                <div style="font-family:'Orbitron',sans-serif;font-size:1.2rem;font-weight:900;color:{arena_color}">{arena_icon}</div>
                <div style="font-size:0.6rem;color:{arena_color};letter-spacing:1px">{arena_name}</div>
            </div>
            <div style="text-align:center">
                <div style="font-family:'Orbitron',sans-serif;font-size:1.2rem;font-weight:900;color:#4ade80">{wins}W</div>
                <div style="font-size:0.6rem;color:#888;letter-spacing:2px">VITTORIE</div>
            </div>
        </div>
    </div>
    """.format(
        level=level, xp_pct=xp_pct, xp=xp, xp_needed=xp_needed, coins=coins,
        arena_color=current_arena['color'], arena_icon=current_arena['icon'],
        arena_name=current_arena['name'], wins=rivals_data['battle_wins']
    ), unsafe_allow_html=True)

    tabs = st.tabs(["⚔️ MBT RIVALS", "🃏 Collezione", "🛒 Negozio", "🏟️ Arene", "💪 Poteri", "⚙️ Admin"])

    with tabs[0]:
        _render_battle_tab(rivals_data, cards_db, state)
    with tabs[1]:
        _render_collection_tab(rivals_data, cards_db)
    with tabs[2]:
        _render_shop_tab(rivals_data, cards_db)
    with tabs[3]:
        _render_arenas_tab(rivals_data)
    with tabs[4]:
        _render_powers_tab(rivals_data)
    with tabs[5]:
        _render_admin_tab(state, cards_db, rivals_data)

    save_rivals_data(rivals_data)
    save_cards_db(cards_db)


def _sync_ovr_from_tournament(state, cards_db):
    """Sincronizza l'OVR delle carte atleti reali dal sistema torneo."""
    from data_manager import calcola_overall_fifa
    for atleta in state.get("atleti", []):
        ovr = calcola_overall_fifa(atleta)
        # Trova la carta corrispondente nel DB
        for card in cards_db.get("cards", []):
            if card.get("atleta_id") == atleta["id"]:
                card["overall"] = ovr
                # Aggiorna anche stats
                s = atleta["stats"]
                card["attacco"] = s.get("attacco", 40)
                card["difesa"] = s.get("difesa", 40)
                card["muro"] = s.get("muro", 40)
                card["ricezione"] = s.get("ricezione", 40)
                card["battuta"] = s.get("battuta", 40)
                card["alzata"] = s.get("alzata", 40)


# ─── BATTLE TAB ───────────────────────────────────────────────────────────────

def _render_battle_tab(rivals_data, cards_db, state):
    st.markdown("## ⚔️ MBT RIVALS — Battaglia vs CPU")

    battle_state = st.session_state.get("battle_state")

    if battle_state is None:
        # Selezione squadra
        active_team_ids = rivals_data.get("active_team", [])
        all_cards = cards_db.get("cards", [])
        team_cards = [c for c in all_cards if c.get("id") in active_team_ids]

        st.markdown("### 🏆 La Tua Squadra Attiva")
        if not team_cards:
            st.warning("⚠️ Nessuna carta nella squadra attiva! Vai in **Collezione** → seleziona fino a 5 carte.")
            return

        # Mostra team
        cols = st.columns(min(5, len(team_cards)))
        for i, card in enumerate(team_cards[:5]):
            with cols[i]:
                st.markdown(render_card_html(card, size="small"), unsafe_allow_html=True)

        st.markdown("---")
        level = rivals_data["player_level"]
        current_arena = next((a for a in ARENE if a["min_level"] <= level <= a["max_level"]), ARENE[0])

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="arena-badge {css}" style="margin-bottom:12px">
                <div style="font-size:2rem">{icon}</div>
                <div style="font-family:'Orbitron',sans-serif;font-weight:700;color:{color};font-size:0.9rem">{name}</div>
                <div style="font-size:0.65rem;color:#888;margin-top:4px">LV.{level} Arena</div>
            </div>
            """.format(
                css=current_arena['css'], icon=current_arena['icon'],
                color=current_arena['color'], name=current_arena['name'], level=level
            ), unsafe_allow_html=True)
        with col2:
            cpu_level = level
            st.markdown("""
            <div style="background:#10101e;border:1px solid #1e1e3a;border-radius:10px;padding:16px;text-align:center">
                <div style="font-size:1.5rem">🤖</div>
                <div style="font-family:'Orbitron',sans-serif;color:#dc2626;font-weight:700">CPU LV.{lvl}</div>
                <div style="font-size:0.65rem;color:#888">Difficoltà proporzionale al tuo livello</div>
            </div>
            """.format(lvl=cpu_level), unsafe_allow_html=True)

        st.markdown("**Ricompense vittoria:**")
        st.markdown("🪙 +{} Coins | ⭐ +{} XP | 🏆 +{} Trofei".format(
            50 + level * 10, 30 + level * 5, 2 + level))

        if st.button("⚔️ INIZIA BATTAGLIA!", use_container_width=True, type="primary"):
            play_cards = team_cards[:3]
            st.session_state.battle_state = init_battle_state(play_cards, cpu_level=level)
            st.rerun()

    else:
        _render_active_battle(battle_state, rivals_data, cards_db)


def _render_active_battle(battle_state, rivals_data, cards_db):
    phase = battle_state["phase"]

    if phase == "win":
        st.markdown("""
        <div style="text-align:center;padding:30px;background:linear-gradient(135deg,#001a00,#003300);
            border:3px solid #16a34a;border-radius:16px;animation:pulseGlow 1s infinite">
            <div style="font-size:3rem">🏆</div>
            <div style="font-family:'Orbitron',sans-serif;font-size:2rem;font-weight:900;color:#4ade80">
                VITTORIA!
            </div>
        </div>
        """, unsafe_allow_html=True)
        level = rivals_data["player_level"]
        xp_gain = 30 + level * 5
        coins_gain = 50 + level * 10
        trofei_gain = 2 + level
        rivals_data["player_xp"] += xp_gain
        rivals_data["mbt_coins"] += coins_gain
        rivals_data["trofei_rivals"] += trofei_gain
        rivals_data["battle_wins"] += 1
        _check_level_up(rivals_data)
        st.success("🎉 +{} XP | +{} Coins | +{} Trofei".format(xp_gain, coins_gain, trofei_gain))
        if st.button("🔄 Nuova Partita", use_container_width=True):
            st.session_state.battle_state = None
            st.rerun()
        return

    if phase == "lose":
        st.markdown("""
        <div style="text-align:center;padding:30px;background:linear-gradient(135deg,#1a0000,#330000);
            border:3px solid #dc2626;border-radius:16px">
            <div style="font-size:3rem">💀</div>
            <div style="font-family:'Orbitron',sans-serif;font-size:2rem;font-weight:900;color:#ef4444">
                SCONFITTA
            </div>
        </div>
        """, unsafe_allow_html=True)
        rivals_data["battle_losses"] += 1
        xp_gain = 10
        rivals_data["player_xp"] += xp_gain
        rivals_data["mbt_coins"] += 20
        _check_level_up(rivals_data)
        st.info("+{} XP per aver combattuto | +20 Coins".format(xp_gain))
        if st.button("🔄 Riprova", use_container_width=True):
            st.session_state.battle_state = None
            st.rerun()
        return

    # Battaglia attiva
    p_idx = battle_state["player_active_idx"]
    c_idx = battle_state["cpu_active_idx"]
    p_fighter = battle_state["player_fighters"][p_idx]
    c_fighter = battle_state["cpu_fighters"][c_idx]

    # Timer
    elapsed = time.time() - battle_state["start_time"]
    remaining = max(0, battle_state["time_limit"] - elapsed)
    min_r = int(remaining // 60)
    sec_r = int(remaining % 60)
    if remaining <= 0:
        battle_state["phase"] = "lose"
        st.rerun()

    col_p, col_mid, col_c = st.columns([2, 1, 2])

    with col_p:
        st.markdown("**⚡ {}**".format(p_fighter['card'].get('nome','Player')))
        hp_pct = int(p_fighter['hp'] / p_fighter['max_hp'] * 100)
        hp_class = "danger" if hp_pct < 30 else ""
        st.markdown("""
        <div class="hp-bar-container">
            <div class="hp-bar-fill {cls}" style="width:{pct}%"></div>
        </div>
        <div style="font-size:0.7rem;color:#888;margin-top:2px">HP: {hp}/{max_hp}</div>
        """.format(cls=hp_class, pct=hp_pct, hp=p_fighter['hp'], max_hp=p_fighter['max_hp']), unsafe_allow_html=True)
        # Stamina
        sta_pct = int(p_fighter['stamina'])
        st.markdown("""
        <div style="height:8px;background:#1a1a2a;border-radius:4px;overflow:hidden;margin-top:8px">
            <div style="width:{sta}%;height:100%;background:linear-gradient(90deg,#ffd700,#ffec4a);border-radius:4px;transition:width 0.3s"></div>
        </div>
        <div style="font-size:0.6rem;color:#888;margin-top:1px">STAMINA: {sta}%</div>
        """.format(sta=sta_pct), unsafe_allow_html=True)
        st.markdown(render_card_html(p_fighter["card"], size="small", show_special_effects=False), unsafe_allow_html=True)

    with col_mid:
        st.markdown("""
        <div style="text-align:center;padding:20px 0">
            <div style="font-family:'Orbitron',sans-serif;font-size:1.5rem;font-weight:900;color:#dc2626">VS</div>
            <div style="font-size:0.7rem;color:#888;margin-top:8px">⏱️ {:02d}:{:02d}</div>
            <div style="font-size:0.65rem;color:#ffd700;margin-top:4px">Turno {}</div>
            <div style="font-size:0.6rem;color:#888;margin-top:8px">Carica: {}/10</div>
        </div>
        """.format(min_r, sec_r, battle_state['turn'], battle_state['stamina_charges']), unsafe_allow_html=True)

    with col_c:
        st.markdown("**🤖 {}**".format(c_fighter['card'].get('nome','CPU')))
        chp_pct = int(c_fighter['hp'] / c_fighter['max_hp'] * 100)
        st.markdown("""
        <div class="hp-bar-container">
            <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#dc2626,#ef4444);border-radius:10px;transition:width 0.5s"></div>
        </div>
        <div style="font-size:0.7rem;color:#888;margin-top:2px">HP: {hp}/{max_hp}</div>
        """.format(pct=chp_pct, hp=c_fighter['hp'], max_hp=c_fighter['max_hp']), unsafe_allow_html=True)
        st.markdown(render_card_html(c_fighter["card"], size="small", show_special_effects=False), unsafe_allow_html=True)

    # Azioni
    st.markdown("#### 🎮 Scegli la tua mossa:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("⚡ ATTACCO", key="battle_attack", use_container_width=True):
            process_battle_action(battle_state, "attack", rivals_data)
            st.rerun()
    with col2:
        can_special = p_fighter["stamina"] >= 40
        if st.button("🔥 SUPER {}".format('✓' if can_special else '✗'), key="battle_special", use_container_width=True, disabled=not can_special):
            process_battle_action(battle_state, "special", rivals_data)
            st.rerun()
    with col3:
        if st.button("🛡️ DIFENDI", key="battle_defend", use_container_width=True):
            process_battle_action(battle_state, "defend", rivals_data)
            st.rerun()
    with col4:
        can_final = battle_state["stamina_charges"] >= 10
        charges = battle_state["stamina_charges"]
        finale_label = "💥 FINALE {}".format('✓' if can_final else str(charges)+'/10')
        if st.button(finale_label, key="battle_final", use_container_width=True, disabled=not can_final):
            process_battle_action(battle_state, "final", rivals_data)
            st.rerun()

    # Log
    if battle_state["log"]:
        with st.expander("📋 Log Battaglia", expanded=True):
            log_html = '<div class="battle-log">'
            for entry in reversed(battle_state["log"][-8:]):
                log_html += '<div style="padding:2px 0;border-bottom:1px solid #1a1a2a;color:#ccc">{}</div>'.format(entry)
            log_html += '</div>'
            st.markdown(log_html, unsafe_allow_html=True)

    if st.button("🏳️ Abbandona Partita", key="battle_quit"):
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
        new_arena = next((a for a in ARENE if a["min_level"] <= rivals_data["player_level"] <= a["max_level"]), None)
        if new_arena:
            rivals_data["arena_unlocked"] = rivals_data["player_level"]


# ─── COLLECTION TAB ───────────────────────────────────────────────────────────

def _render_collection_tab(rivals_data, cards_db):
    st.markdown("## 🃏 La Mia Collezione")

    all_cards = cards_db.get("cards", [])
    owned_ids = rivals_data.get("collection", [])
    active_team = rivals_data.get("active_team", [])

    # Per demo: mostra tutte le carte del DB come possedute se collezione vuota
    if not owned_ids and all_cards:
        st.info("💡 La tua collezione cresce acquistando pacchetti! Ecco l'anteprima di tutte le carte disponibili.")
        owned_cards = all_cards
    else:
        owned_cards = [c for c in all_cards if c.get("id") in owned_ids]

    if not owned_cards:
        st.warning("📦 Nessuna carta! Vai nel **Negozio** per acquistare pacchetti.")
        return

    # Filtro rarità
    tier_filter = st.selectbox("🔍 Filtra per Rarità", ["Tutte"] + list(CARD_TIERS.keys()))

    filtered = owned_cards
    if tier_filter != "Tutte":
        filtered = [c for c in owned_cards if get_tier_by_ovr(c.get("overall",40)) == tier_filter]

    st.caption("📊 Totale: {} carte | Mostrate: {}".format(len(owned_cards), len(filtered)))

    # Gestione squadra attiva
    st.markdown("### 👥 Squadra Attiva (max 5 carte)")
    st.caption("Seleziona le carte da usare in battaglia:")

    cols_grid = st.columns(5)
    for i, card in enumerate(all_cards[:5] if len(all_cards) <= 10 else filtered[:5]):
        with cols_grid[i % 5]:
            card_id = card.get("id", "")
            is_active = card_id in active_team
            st.markdown(render_card_html(card, size="small"), unsafe_allow_html=True)
            if is_active:
                if st.button("✅ IN SQUADRA", key="rm_team_{}_{}".format(i, card_id[:8]), use_container_width=True):
                    active_team.remove(card_id)
                    rivals_data["active_team"] = active_team
                    st.rerun()
            else:
                disabled = len(active_team) >= 5
                if st.button("➕ Aggiungi", key="add_team_{}_{}".format(i, card_id[:8]), disabled=disabled, use_container_width=True):
                    active_team.append(card_id)
                    rivals_data["active_team"] = active_team
                    st.rerun()

    st.markdown("---")
    st.markdown("### 🗂️ Tutte le Carte")

    # Raggruppa per rarità
    rarity_groups = {}
    for card in filtered:
        tier = get_tier_by_ovr(card.get("overall", 40))
        rarity_groups.setdefault(tier, []).append(card)

    for tier_name in reversed(list(CARD_TIERS.keys())):
        if tier_name not in rarity_groups:
            continue
        tier_cards = rarity_groups[tier_name]
        tier_info = CARD_TIERS[tier_name]

        with st.expander("{} ({} carte)".format(tier_name, len(tier_cards)), expanded=tier_info["rarity"] >= 12):
            cols_per_row = 5
            for i in range(0, len(tier_cards), cols_per_row):
                chunk = tier_cards[i:i+cols_per_row]
                row_cols = st.columns(cols_per_row)
                for j, card in enumerate(chunk):
                    with row_cols[j]:
                        st.markdown(render_card_html(card, size="small"), unsafe_allow_html=True)
                        role = card.get("ruolo", "")
                        ovr = card.get("overall", 40)
                        st.caption("OVR {} | {}".format(ovr, role[:10]))


# ─── SHOP TAB ─────────────────────────────────────────────────────────────────

def _render_shop_tab(rivals_data, cards_db):
    st.markdown("## 🛒 Negozio Pacchetti")

    coins = rivals_data.get("mbt_coins", 0)
    st.markdown("""
    <div style="text-align:right;margin-bottom:20px">
        <span style="font-family:'Orbitron',sans-serif;font-size:1.2rem;color:#ffd700;font-weight:700">
            🪙 {} MBT Coins
        </span>
    </div>
    """.format(coins), unsafe_allow_html=True)

    # Mostra i 3 tipi di pacchetto
    pack_cols = st.columns(3)
    pack_names = ["Base", "Epico", "Leggenda"]

    pack_emojis = {"Base":"🟫", "Epico":"💜", "Leggenda":"🔥"}
    pack_descs = {
        "Base": "Perfetto per iniziare. Carte Bronzo, Argento e raramente Oro.",
        "Epico": "Alta probabilità di Oro ed Eroi. Chance di Leggenda e TOTY!",
        "Leggenda": "Solo carte di alto livello. Garantisce almeno una Leggenda!",
    }

    for i, pack_name in enumerate(pack_names):
        pack_info = PACKS[pack_name]
        with pack_cols[i]:
            color = pack_info["label_color"]
            can_afford = coins >= pack_info["price"]
            st.markdown("""
            <div class="pack-card {css}" style="width:100%;height:220px;border-radius:16px;
                position:relative;overflow:hidden;display:flex;flex-direction:column;
                align-items:center;justify-content:center;margin-bottom:8px">
                <div style="font-size:3rem;z-index:2">{emoji}</div>
                <div style="font-family:'Orbitron',sans-serif;font-size:1.1rem;font-weight:900;
                    color:{color};z-index:2;letter-spacing:3px;text-transform:uppercase">{name}</div>
                <div style="font-size:0.65rem;color:#888;z-index:2;text-align:center;padding:0 10px;margin-top:4px">
                    {desc}
                </div>
                <div style="font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:700;
                    color:#ffd700;z-index:2;margin-top:8px">🪙 {price}</div>
            </div>
            """.format(
                css=pack_info['css_class'], emoji=pack_emojis[pack_name],
                color=color, name=pack_name, desc=pack_descs[pack_name],
                price=pack_info['price']
            ), unsafe_allow_html=True)

            if st.button(
                "{} {}".format('🛒 Acquista' if can_afford else '🔒 Non hai abbastanza coins', pack_name),
                key="buy_pack_{}".format(pack_name),
                use_container_width=True,
                disabled=not can_afford
            ):
                st.session_state["opening_pack"] = pack_name
                rivals_data["mbt_coins"] -= pack_info["price"]
                drawn = draw_cards_from_pack(pack_name, cards_db)
                st.session_state["drawn_cards"] = drawn
                # Aggiungi alla collezione
                for card in drawn:
                    rivals_data["collection"].append(card.get("id", card.get("instance_id", "")))
                st.rerun()

    # Mostra apertura pack
    if st.session_state.get("drawn_cards"):
        pack_name_opened = st.session_state.get("opening_pack", "Base")
        drawn = st.session_state["drawn_cards"]

        st.markdown("---")
        # Animazione
        max_rarity = max(CARD_TIERS.get(get_tier_by_ovr(c.get("overall",40)),{}).get("rarity",0) for c in drawn)
        if max_rarity >= 12:
            st.markdown("""
            <div style="text-align:center;animation:screenShake 0.5s infinite;background:rgba(255,215,0,0.1);
                border:2px solid #ffd700;border-radius:10px;padding:10px;margin-bottom:10px">
                <span style="font-family:'Orbitron',sans-serif;font-size:1rem;color:#ffd700;
                    animation:goldShine 1s infinite">⚡💥 CARTA ICONA! 💥⚡</span>
            </div>
            """, unsafe_allow_html=True)
        elif max_rarity >= 8:
            st.markdown("""
            <div style="text-align:center;background:rgba(255,255,255,0.05);
                border:2px solid #ffffff;border-radius:10px;padding:8px;margin-bottom:10px">
                <span style="font-family:'Orbitron',sans-serif;font-size:0.9rem;color:#fff">
                    ✨ CARTA LEGGENDARIA O SUPERIORE! ✨
                </span>
            </div>
            """, unsafe_allow_html=True)

        render_pack_opening_animation(drawn, pack_name_opened)

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ Aggiungi TUTTE alla Collezione e Continua", use_container_width=True, type="primary"):
                st.session_state["drawn_cards"] = None
                st.session_state["opening_pack"] = None
                st.rerun()
        with col_btn2:
            if st.button("🔄 Apri un altro pacchetto", use_container_width=True):
                st.session_state["drawn_cards"] = None
                st.session_state["opening_pack"] = None
                st.rerun()

    # Sezione mosse speciali
    st.markdown("---")
    st.markdown("### ⚡ Mosse Speciali")
    st.caption("Insegna mosse speciali alle tue carte spendendo MBT Coins")

    learned = rivals_data.get("special_moves_learned", [])
    move_cols = st.columns(3)
    for i, move in enumerate(SPECIAL_MOVES[:9]):
        with move_cols[i % 3]:
            already_learned = move["id"] in learned
            role_tag = "[{}]".format(move['role']) if move.get("role") else "[Universale]"
            role_desc = ROLE_DESCRIPTIONS.get(move.get("role",""), "")
            can_afford_move = coins >= move["cost_coins"]
            border_color = '#ffd700' if already_learned else '#1e1e3a'
            name_color = '#ffd700' if already_learned else '#ccc'
            price_or_learned = '✅ Appresa' if already_learned else '🪙 {} Coins'.format(move["cost_coins"])
            st.markdown("""
            <div style="background:#10101e;border:1px solid {bc};
                border-radius:8px;padding:10px;margin-bottom:8px;min-height:100px">
                <div style="font-family:'Orbitron',sans-serif;font-size:0.7rem;font-weight:700;
                    color:{nc}">{name}</div>
                <div style="font-size:0.55rem;color:#666;margin:4px 0">{role_tag}</div>
                <div style="font-size:0.6rem;color:#888">{desc}</div>
                <div style="font-size:0.6rem;color:#ffd700;margin-top:4px">{pol}</div>
            </div>
            """.format(
                bc=border_color, nc=name_color, name=move['name'],
                role_tag=role_tag, desc=move['desc'], pol=price_or_learned
            ), unsafe_allow_html=True)
            if not already_learned:
                if st.button("Apprendi", key="learn_{}".format(move['id']), disabled=not can_afford_move, use_container_width=True):
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
        col1, col2 = st.columns([1, 3])
        with col1:
            opacity_style = 'opacity:0.4;filter:grayscale(80%)' if not is_unlocked else ''
            st.markdown("""
            <div class="arena-badge {css}" style="{op}">
                <div style="font-size:2rem">{icon}</div>
                <div style="font-family:'Orbitron',sans-serif;font-size:0.65rem;font-weight:700;
                    color:{color}">
                    LV.{min_lv}-{max_lv}
                </div>
            </div>
            """.format(
                css=arena['css'] if is_unlocked else 'arena-badge',
                op=opacity_style,
                icon=arena['icon'] if is_unlocked else '🔒',
                color=arena['color'] if is_unlocked else '#555',
                min_lv=arena['min_level'], max_lv=arena['max_level']
            ), unsafe_allow_html=True)
        with col2:
            badge = " 🔴 ATTUALE" if is_current else (" ✅ SBLOCCATA" if is_unlocked else " 🔒")
            current_extra = '<div style="font-size:0.65rem;color:#ffd700;margin-top:4px">⚡ Combatti qui per guadagnare ricompense speciali!</div>' if is_current else ''
            st.markdown("""
            <div style="padding:12px 0">
                <div style="font-family:'Orbitron',sans-serif;font-weight:700;
                    color:{color};font-size:0.9rem">
                    {name}{badge}
                </div>
                <div style="font-size:0.7rem;color:#666;margin-top:4px">
                    Livelli {min_lv} – {max_lv}
                </div>
                {extra}
            </div>
            """.format(
                color=arena['color'] if is_unlocked else '#555',
                name=arena['name'], badge=badge,
                min_lv=arena['min_level'], max_lv=arena['max_level'],
                extra=current_extra
            ), unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#1e1e3a;margin:4px 0'>", unsafe_allow_html=True)


# ─── POWERS TAB ───────────────────────────────────────────────────────────────

def _render_powers_tab(rivals_data):
    st.markdown("## 💪 Super Poteri")
    st.caption("Potenzia i tuoi super poteri spendendo MBT Coins nella sezione La Mia Collezione")

    coins = rivals_data.get("mbt_coins", 0)
    superpowers = rivals_data.setdefault("superpowers", {})

    for power in SUPERPOWERS:
        current_level = superpowers.get(power["id"], 0)
        max_level = power["max_level"]
        cost = power["cost_per_level"]

        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            bars = "█" * current_level + "░" * (max_level - current_level)
            st.markdown("""
            <div style="background:#10101e;border:1px solid #1e1e3a;border-radius:8px;padding:12px;margin-bottom:8px">
                <div style="font-family:'Orbitron',sans-serif;font-size:0.8rem;font-weight:700;color:#ffd700">
                    {name} <span style="font-size:0.65rem;color:#888">LV.{cur}/{max}</span>
                </div>
                <div style="font-size:0.65rem;color:#888;margin:4px 0">{desc}</div>
                <div style="font-size:1rem;color:#ffd700;letter-spacing:2px">{bars}</div>
            </div>
            """.format(name=power['name'], cur=current_level, max=max_level,
                       desc=power['desc'], bars=bars), unsafe_allow_html=True)
        with col2:
            if current_level < max_level:
                st.metric("Costo", "🪙 {}".format(cost))
        with col3:
            if current_level < max_level:
                can_up = coins >= cost
                if st.button("⬆️ Potenzia", key="up_power_{}".format(power['id']), disabled=not can_up, use_container_width=True):
                    superpowers[power["id"]] = current_level + 1
                    rivals_data["mbt_coins"] -= cost
                    st.rerun()
            else:
                st.markdown('<div style="color:#ffd700;text-align:center;padding:20px 0">✅ MAX</div>', unsafe_allow_html=True)


# ─── ADMIN TAB ────────────────────────────────────────────────────────────────

def _render_admin_tab(state, cards_db, rivals_data):
    st.markdown("## ⚙️ Pannello Admin — Cards Creator")

    # Password semplice
    if not st.session_state.get("admin_unlocked_rivals"):
        pwd = st.text_input("🔐 Password Admin", type="password", key="admin_pwd_rivals")
        if st.button("Accedi", key="admin_login_rivals"):
            if pwd in ("admin", "mbt2025", "rivals"):
                st.session_state.admin_unlocked_rivals = True
                st.rerun()
            else:
                st.error("Password errata")
        return

    admin_tabs = st.tabs(["➕ Crea Carta", "📋 Gestisci Carte", "🎁 Gestisci Coins"])

    with admin_tabs[0]:
        _render_card_creator(state, cards_db)
    with admin_tabs[1]:
        _render_card_manager(cards_db)
    with admin_tabs[2]:
        _render_coins_manager(rivals_data)


def _render_card_creator(state, cards_db):
    st.markdown("### ✏️ Crea Nuova Carta")

    col_form, col_preview = st.columns([2, 1])

    with col_form:
        nome = st.text_input("Nome", key="cc_nome")
        cognome = st.text_input("Cognome", key="cc_cognome")

        ruolo = st.selectbox("Ruolo", ROLES, key="cc_ruolo")

        st.markdown("---")
        st.markdown("**Statistiche (0–125) — L'OVR viene calcolato automaticamente**")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            atk = st.slider("⚡ Attacco", 0, 125, 70, key="cc_atk")
            dif = st.slider("🛡️ Difesa", 0, 125, 68, key="cc_dif")
            ric = st.slider("🤲 Ricezione", 0, 125, 65, key="cc_ric")
        with col_s2:
            bat = st.slider("🏐 Battuta", 0, 125, 67, key="cc_bat")
            mur = st.slider("🧱 Muro", 0, 125, 62, key="cc_mur")
            alz = st.slider("🎯 Alzata", 0, 125, 60, key="cc_alz")

        # OVR calcolato matematicamente
        overall = calcola_ovr_da_stats(atk, dif, ric, bat, mur, alz)
        tier_preview = get_tier_by_ovr(overall)
        tier_color = CARD_TIERS.get(tier_preview, {}).get("color", "#ffd700")
        st.markdown(
            '<div style="font-family:Orbitron,sans-serif;font-size:0.9rem;color:{};margin-bottom:4px;font-weight:700">'
            'OVR Calcolato: {} | Tier: {}'
            '</div>'.format(tier_color, overall, tier_preview),
            unsafe_allow_html=True
        )

        st.markdown("---")
        # Upload foto
        foto_file = st.file_uploader("📷 Upload Foto Atleta", type=["png","jpg","jpeg"], key="cc_foto")
        foto_path = ""
        if foto_file:
            os.makedirs(ASSETS_ICONS_DIR, exist_ok=True)
            foto_path = os.path.join(ASSETS_ICONS_DIR, "{}_{}_{}".format(nome, cognome, random.randint(1000,9999)))
            ext = foto_file.name.rsplit(".",1)[-1].lower()
            foto_path = foto_path + "." + ext
            with open(foto_path, "wb") as f:
                f.write(foto_file.read())
            st.success("📷 Foto salvata: {}".format(foto_path))

        # Collegamento atleta esistente
        atleti_nomi = ["-- Nessuno --"] + [a["nome"] for a in state.get("atleti", [])]
        selected_atleta_nome = st.selectbox("🔗 Collega a Atleta Torneo (opzionale)", atleti_nomi, key="cc_atleta_link")
        atleta_id_linked = None
        if selected_atleta_nome != "-- Nessuno --":
            linked = next((a for a in state["atleti"] if a["nome"] == selected_atleta_nome), None)
            if linked:
                atleta_id_linked = linked["id"]
                # Carica OVR reale
                from data_manager import calcola_overall_fifa
                real_ovr = calcola_overall_fifa(linked)
                st.info("📊 OVR reale dall'app torneo: **{}** — La carta si aggiornerà automaticamente.".format(real_ovr))

    with col_preview:
        st.markdown("#### 👁️ Anteprima Carta")
        preview_card = {
            "id": "preview",
            "nome": nome or "NOME",
            "cognome": cognome or "",
            "overall": overall,
            "ruolo": ruolo,
            "attacco": atk,
            "difesa": dif,
            "battuta": bat,
            "muro": mur,
            "ricezione": ric,
            "alzata": alz,
            "foto_path": foto_path,
        }
        st.markdown(
            '<div class="creator-preview-wrap">{}</div>'.format(render_card_html(preview_card, size="large")),
            unsafe_allow_html=True
        )

        st.markdown("""
        <div style="background:#10101e;border:1px solid {tc};border-radius:8px;padding:10px;text-align:center;margin-top:10px">
            <div style="font-family:Orbitron,sans-serif;font-size:0.7rem;color:{tc};font-weight:700">{tier}</div>
            <div style="font-size:0.6rem;color:#888;margin-top:2px">OVR {ovr}</div>
        </div>
        """.format(tc=tier_color, tier=tier_preview, ovr=overall), unsafe_allow_html=True)

    st.markdown("---")
    if st.button("💾 SALVA CARTA nel Database", use_container_width=True, type="primary"):
        if not nome:
            st.error("Inserisci il nome del giocatore!")
        else:
            new_id = "card_{}_{}".format(cards_db['next_id'], random.randint(1000,9999))
            cards_db["next_id"] += 1

            new_card = {
                "id": new_id,
                "nome": nome,
                "cognome": cognome,
                "overall": overall,
                "ruolo": ruolo,
                "attacco": atk,
                "difesa": dif,
                "muro": mur,
                "ricezione": ric,
                "battuta": bat,
                "alzata": alz,
                "foto_path": foto_path,
                "tier": tier_preview,
                "atleta_id": atleta_id_linked,
                "created_at": datetime.now().isoformat(),
            }
            cards_db["cards"].append(new_card)
            save_cards_db(cards_db)
            st.success("✅ Carta **{} {}** (OVR {} · {}) salvata nel database!".format(
                nome, cognome, overall, tier_preview))
            st.session_state.cards_db = cards_db
            st.rerun()


def _render_card_manager(cards_db):
    st.markdown("### 📋 Carte nel Database")
    all_cards = cards_db.get("cards", [])

    if not all_cards:
        st.info("Nessuna carta nel database. Creane una con il Card Creator!")
        return

    st.caption("Totale: {} carte".format(len(all_cards)))

    # Filtro
    filter_tier = st.selectbox("Filtra Tier", ["Tutte"] + list(CARD_TIERS.keys()), key="mgr_filter")

    filtered = all_cards if filter_tier == "Tutte" else [c for c in all_cards if get_tier_by_ovr(c.get("overall",40)) == filter_tier]

    for i, card in enumerate(filtered):
        tier = get_tier_by_ovr(card.get("overall",40))
        tc = CARD_TIERS.get(tier, {}).get("color","#888")
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.markdown(render_card_html(card, size="small", show_special_effects=False), unsafe_allow_html=True)
        with col2:
            # Mostra anche statistiche dettagliate
            atk = card.get('attacco', 40)
            dif = card.get('difesa', 40)
            bat = card.get('battuta', 40)
            mur = card.get('muro', 40)
            ric = card.get('ricezione', 40)
            alz = card.get('alzata', 40)
            st.markdown("""
            <div style="padding:8px 0">
                <div style="font-family:Orbitron,sans-serif;font-weight:700;color:{tc}">{nome} {cognome}</div>
                <div style="font-size:0.7rem;color:#888">OVR {ovr} · {tier} · {ruolo}</div>
                <div style="font-size:0.6rem;color:#666;margin-top:4px">
                    ATK:{atk} | DEF:{dif} | BAT:{bat} | MUR:{mur} | RIC:{ric} | ALZ:{alz}
                </div>
                <div style="font-size:0.55rem;color:#444;margin-top:2px">ID: {id}...</div>
            </div>
            """.format(
                tc=tc, nome=card.get('nome',''), cognome=card.get('cognome',''),
                ovr=card.get('overall',40), tier=tier, ruolo=card.get('ruolo',''),
                atk=atk, dif=dif, bat=bat, mur=mur, ric=ric, alz=alz,
                id=card.get('id','')[:16]
            ), unsafe_allow_html=True)

            # Editing stats inline
            with st.expander("✏️ Modifica Stats"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    new_atk = st.slider("ATK", 0, 125, int(atk), key="edit_atk_{}_{}".format(i, card.get('id','')[:6]))
                    new_dif = st.slider("DEF", 0, 125, int(dif), key="edit_dif_{}_{}".format(i, card.get('id','')[:6]))
                    new_ric = st.slider("RIC", 0, 125, int(ric), key="edit_ric_{}_{}".format(i, card.get('id','')[:6]))
                with ec2:
                    new_bat = st.slider("BAT", 0, 125, int(bat), key="edit_bat_{}_{}".format(i, card.get('id','')[:6]))
                    new_mur = st.slider("MUR", 0, 125, int(mur), key="edit_mur_{}_{}".format(i, card.get('id','')[:6]))
                    new_alz = st.slider("ALZ", 0, 125, int(alz), key="edit_alz_{}_{}".format(i, card.get('id','')[:6]))
                new_ovr = calcola_ovr_da_stats(new_atk, new_dif, new_ric, new_bat, new_mur, new_alz)
                st.caption("OVR calcolato: {} | Tier: {}".format(new_ovr, get_tier_by_ovr(new_ovr)))
                if st.button("💾 Salva Modifiche", key="save_card_{}_{}".format(i, card.get('id','')[:6])):
                    card['attacco'] = new_atk
                    card['difesa'] = new_dif
                    card['ricezione'] = new_ric
                    card['battuta'] = new_bat
                    card['muro'] = new_mur
                    card['alzata'] = new_alz
                    card['overall'] = new_ovr
                    card['tier'] = get_tier_by_ovr(new_ovr)
                    save_cards_db(cards_db)
                    st.session_state.cards_db = cards_db
                    st.success("✅ Stats aggiornate!")
                    st.rerun()

        with col3:
            if st.button("🗑️", key="del_card_{}_{}".format(i, card.get('id','')[:8]), help="Elimina carta"):
                cards_db["cards"] = [c for c in all_cards if c.get("id") != card.get("id")]
                save_cards_db(cards_db)
                st.session_state.cards_db = cards_db
                st.rerun()
        st.markdown("<hr style='border-color:#1e1e3a;margin:4px 0'>", unsafe_allow_html=True)


def _render_coins_manager(rivals_data):
    st.markdown("### 🎁 Gestione Coins & XP")

    col1, col2 = st.columns(2)
    with col1:
        add_coins = st.number_input("Aggiungi MBT Coins", 0, 99999, 500, key="admin_add_coins")
        if st.button("➕ Aggiungi Coins", key="admin_btn_coins"):
            rivals_data["mbt_coins"] += add_coins
            st.success("✅ Aggiunti {} coins! Totale: {}".format(add_coins, rivals_data['mbt_coins']))
    with col2:
        add_xp = st.number_input("Aggiungi XP", 0, 99999, 100, key="admin_add_xp")
        if st.button("➕ Aggiungi XP", key="admin_btn_xp"):
            rivals_data["player_xp"] += add_xp
            _check_level_up(rivals_data)
            st.success("✅ Aggiunti {} XP! Level: {}".format(add_xp, rivals_data['player_level']))

    st.markdown("---")
    st.markdown("""
    **Stato attuale:**
    - MBT Coins: **{}**
    - XP: **{}**
    - Livello: **{}**
    - Trofei: **{}**
    - Vittorie: **{}**
    """.format(
        rivals_data['mbt_coins'], rivals_data['player_xp'],
        rivals_data['player_level'], rivals_data['trofei_rivals'],
        rivals_data['battle_wins']
    ))

    if st.button("🔄 Reset Dati Rivals", key="admin_reset_rivals"):
        st.session_state.rivals_data = empty_rivals_state()
        st.session_state.rivals_data["mbt_coins"] = 1000
        save_rivals_data(st.session_state.rivals_data)
        st.success("✅ Dati Rivals resettati con 1000 Coins di partenza.")
        st.rerun()
