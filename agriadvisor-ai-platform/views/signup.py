import streamlit as st
from utils.supabase_client import get_supabase_client
from utils.styling import get_base64_svg
import logging
logger = logging.getLogger(__name__)

BOTANICAL_ART_TOP_LEFT = """
<svg class="botanical-corner botanical-top-left" viewBox="0 0 400 700" xmlns="http://www.w3.org/2000/svg">
    <path d="M-20,680 Q40,550 60,420 Q80,300 40,180 Q10,90 60,-20" stroke="#34D399" stroke-width="3" fill="none" opacity="0.35"/>
    <path d="M60,420 Q100,400 140,360" stroke="#34D399" stroke-width="2.5" fill="none" opacity="0.35"/>
    <path d="M140,360 Q175,345 200,315" stroke="#34D399" stroke-width="2" fill="none" opacity="0.3"/>
    <path d="M200,315 Q225,300 260,290" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.25"/>
    <path d="M50,300 Q90,290 120,250" stroke="#34D399" stroke-width="2.5" fill="none" opacity="0.35"/>
    <path d="M120,250 Q150,235 170,205" stroke="#34D399" stroke-width="2" fill="none" opacity="0.3"/>
    <path d="M170,205 Q195,190 225,185" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.25"/>
    <path d="M45,540 Q10,520 -30,530" stroke="#34D399" stroke-width="2.5" fill="none" opacity="0.35"/>
    <path d="M55,600 Q95,610 125,650" stroke="#34D399" stroke-width="2.5" fill="none" opacity="0.35"/>
    <path d="M125,650 Q160,665 190,655" stroke="#34D399" stroke-width="2" fill="none" opacity="0.3"/>
    <path d="M190,655 Q220,645 240,615" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.25"/>
    <path d="M40,150 Q75,145 100,110" stroke="#34D399" stroke-width="2.5" fill="none" opacity="0.35"/>
    <path d="M100,110 Q130,95 150,65" stroke="#34D399" stroke-width="2" fill="none" opacity="0.3"/>
    <path d="M150,65 Q175,45 210,40" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.25"/>
    <path d="M65,460 Q160,430 230,360" stroke="#34D399" stroke-width="2.5" fill="none" opacity="0.3"/>
    <path d="M230,360 Q255,335 260,300" stroke="#34D399" stroke-width="2" fill="none" opacity="0.28"/>
    <path d="M260,300 Q280,280 310,275" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.24"/>
    <path d="M35,80 Q60,60 55,25" stroke="#34D399" stroke-width="2" fill="none" opacity="0.3"/>
    <path d="M30,610 Q0,600 -20,615" stroke="#34D399" stroke-width="2" fill="none" opacity="0.3"/>
    <path d="M90,380 Q130,375 155,350" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.22"/>
    <path d="M75,230 Q105,215 115,185" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.22"/>
    <path d="M80,500 Q45,495 20,510" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.22"/>
    <path d="M50,180 Q20,170 5,190" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.22"/>

    <ellipse cx="140" cy="360" rx="26" ry="13" fill="#34D399" opacity="0.3" transform="rotate(-35 140 360)"/>
    <ellipse cx="200" cy="315" rx="16" ry="8" fill="#34D399" opacity="0.26" transform="rotate(-45 200 315)"/>
    <ellipse cx="260" cy="290" rx="11" ry="5.5" fill="#34D399" opacity="0.22" transform="rotate(-50 260 290)"/>
    <ellipse cx="115" cy="250" rx="22" ry="11" fill="#34D399" opacity="0.3" transform="rotate(-55 115 250)"/>
    <ellipse cx="170" cy="205" rx="15" ry="7.5" fill="#34D399" opacity="0.26" transform="rotate(-60 170 205)"/>
    <ellipse cx="225" cy="185" rx="10" ry="5" fill="#34D399" opacity="0.22" transform="rotate(-65 225 185)"/>
    <ellipse cx="65" cy="460" rx="24" ry="12" fill="#34D399" opacity="0.3" transform="rotate(20 65 460)"/>
    <ellipse cx="10" cy="520" rx="20" ry="10" fill="#34D399" opacity="0.3" transform="rotate(70 10 520)"/>
    <ellipse cx="35" cy="580" rx="22" ry="11" fill="#34D399" opacity="0.3" transform="rotate(10 35 580)"/>
    <ellipse cx="190" cy="655" rx="15" ry="7.5" fill="#34D399" opacity="0.26" transform="rotate(15 190 655)"/>
    <ellipse cx="240" cy="615" rx="10" ry="5" fill="#34D399" opacity="0.22" transform="rotate(20 240 615)"/>
    <ellipse cx="100" cy="110" rx="20" ry="10" fill="#34D399" opacity="0.3" transform="rotate(-60 100 110)"/>
    <ellipse cx="150" cy="65" rx="14" ry="7" fill="#34D399" opacity="0.26" transform="rotate(-70 150 65)"/>
    <ellipse cx="210" cy="40" rx="10" ry="5" fill="#34D399" opacity="0.22" transform="rotate(-75 210 40)"/>
    <ellipse cx="120" cy="650" rx="18" ry="9" fill="#34D399" opacity="0.3" transform="rotate(30 120 650)"/>
    <ellipse cx="280" cy="345" rx="16" ry="8" fill="#34D399" opacity="0.28" transform="rotate(-20 280 345)"/>
    <ellipse cx="260" cy="300" rx="14" ry="7" fill="#34D399" opacity="0.25" transform="rotate(-10 260 300)"/>
    <ellipse cx="310" cy="275" rx="10" ry="5" fill="#34D399" opacity="0.2" transform="rotate(-15 310 275)"/>
    <ellipse cx="55" cy="25" rx="13" ry="6.5" fill="#34D399" opacity="0.26" transform="rotate(40 55 25)"/>
    <ellipse cx="-20" cy="615" rx="13" ry="6.5" fill="#34D399" opacity="0.26" transform="rotate(-30 -20 615)"/>
    <ellipse cx="155" cy="350" rx="12" ry="6" fill="#34D399" opacity="0.2" transform="rotate(-40 155 350)"/>
    <ellipse cx="115" cy="185" rx="11" ry="5.5" fill="#34D399" opacity="0.2" transform="rotate(-55 115 185)"/>
    <ellipse cx="20" cy="510" rx="11" ry="5.5" fill="#34D399" opacity="0.2" transform="rotate(20 20 510)"/>
    <ellipse cx="5" cy="190" rx="11" ry="5.5" fill="#34D399" opacity="0.2" transform="rotate(60 5 190)"/>

    <g transform="translate(100,110)">
        <ellipse cx="-10" cy="-6" rx="9" ry="5" fill="#34D399" opacity="0.25"/>
        <ellipse cx="10" cy="-6" rx="9" ry="5" fill="#34D399" opacity="0.25" transform="rotate(72 10 -6)"/>
        <ellipse cx="8" cy="10" rx="9" ry="5" fill="#34D399" opacity="0.25" transform="rotate(144 8 10)"/>
        <ellipse cx="-8" cy="10" rx="9" ry="5" fill="#34D399" opacity="0.25" transform="rotate(216 -8 10)"/>
        <ellipse cx="0" cy="-12" rx="9" ry="5" fill="#34D399" opacity="0.25" transform="rotate(288 0 -12)"/>
        <circle cx="0" cy="0" r="8" fill="#F59E0B" opacity="0.8"/>
    </g>
    <g transform="translate(45,540)">
        <ellipse cx="-8" cy="-5" rx="7" ry="4" fill="#34D399" opacity="0.25"/>
        <ellipse cx="8" cy="-5" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(72 8 -5)"/>
        <ellipse cx="6" cy="8" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(144 6 8)"/>
        <ellipse cx="-6" cy="8" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(216 -6 8)"/>
        <ellipse cx="0" cy="-10" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(288 0 -10)"/>
        <circle cx="0" cy="0" r="7" fill="#F59E0B" opacity="0.8"/>
    </g>
    <g transform="translate(120,250)">
        <ellipse cx="-8" cy="-5" rx="7" ry="4" fill="#34D399" opacity="0.25"/>
        <ellipse cx="8" cy="-5" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(72 8 -5)"/>
        <ellipse cx="6" cy="8" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(144 6 8)"/>
        <ellipse cx="-6" cy="8" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(216 -6 8)"/>
        <ellipse cx="0" cy="-10" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(288 0 -10)"/>
        <circle cx="0" cy="0" r="7" fill="#F59E0B" opacity="0.8"/>
    </g>
    <g transform="translate(120,650)">
        <ellipse cx="-8" cy="-5" rx="7" ry="4" fill="#34D399" opacity="0.25"/>
        <ellipse cx="8" cy="-5" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(72 8 -5)"/>
        <ellipse cx="6" cy="8" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(144 6 8)"/>
        <ellipse cx="-6" cy="8" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(216 -6 8)"/>
        <ellipse cx="0" cy="-10" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(288 0 -10)"/>
        <circle cx="0" cy="0" r="7" fill="#F59E0B" opacity="0.8"/>
    </g>
    <g transform="translate(200,315)">
        <ellipse cx="-6" cy="-4" rx="5" ry="3" fill="#34D399" opacity="0.22"/>
        <ellipse cx="6" cy="-4" rx="5" ry="3" fill="#34D399" opacity="0.22" transform="rotate(72 6 -4)"/>
        <ellipse cx="5" cy="6" rx="5" ry="3" fill="#34D399" opacity="0.22" transform="rotate(144 5 6)"/>
        <ellipse cx="-5" cy="6" rx="5" ry="3" fill="#34D399" opacity="0.22" transform="rotate(216 -5 6)"/>
        <ellipse cx="0" cy="-8" rx="5" ry="3" fill="#34D399" opacity="0.22" transform="rotate(288 0 -8)"/>
        <circle cx="0" cy="0" r="5" fill="#F59E0B" opacity="0.7"/>
    </g>
    <g transform="translate(260,300)">
        <ellipse cx="-6" cy="-4" rx="5" ry="3" fill="#34D399" opacity="0.2"/>
        <ellipse cx="6" cy="-4" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(72 6 -4)"/>
        <ellipse cx="5" cy="6" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(144 5 6)"/>
        <ellipse cx="-5" cy="6" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(216 -5 6)"/>
        <ellipse cx="0" cy="-8" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(288 0 -8)"/>
        <circle cx="0" cy="0" r="5" fill="#F59E0B" opacity="0.65"/>
    </g>
    <g transform="translate(190,655)">
        <ellipse cx="-6" cy="-4" rx="5" ry="3" fill="#34D399" opacity="0.2"/>
        <ellipse cx="6" cy="-4" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(72 6 -4)"/>
        <ellipse cx="5" cy="6" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(144 5 6)"/>
        <ellipse cx="-5" cy="6" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(216 -5 6)"/>
        <ellipse cx="0" cy="-8" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(288 0 -8)"/>
        <circle cx="0" cy="0" r="5" fill="#F59E0B" opacity="0.65"/>
    </g>
    <circle cx="30" cy="40" r="6" fill="#34D399" opacity="0.3"/>
    <circle cx="220" cy="370" r="4" fill="#34D399" opacity="0.25"/>
    <circle cx="300" cy="270" r="3" fill="#34D399" opacity="0.2"/>
    <circle cx="235" cy="600" r="3" fill="#34D399" opacity="0.2"/>
</svg>
"""

BOTANICAL_ART_BOTTOM_RIGHT = """
<svg class="botanical-corner botanical-bottom-right" viewBox="0 0 400 700" xmlns="http://www.w3.org/2000/svg">
    <path d="M420,20 Q360,150 340,280 Q320,400 360,520 Q390,610 340,720" stroke="#34D399" stroke-width="3" fill="none" opacity="0.35"/>
    <path d="M340,280 Q300,300 260,340" stroke="#34D399" stroke-width="2.5" fill="none" opacity="0.35"/>
    <path d="M260,340 Q225,355 200,385" stroke="#34D399" stroke-width="2" fill="none" opacity="0.3"/>
    <path d="M200,385 Q175,400 140,410" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.25"/>
    <path d="M350,400 Q310,410 280,450" stroke="#34D399" stroke-width="2.5" fill="none" opacity="0.35"/>
    <path d="M280,450 Q250,465 230,495" stroke="#34D399" stroke-width="2" fill="none" opacity="0.3"/>
    <path d="M230,495 Q205,510 175,515" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.25"/>
    <path d="M355,160 Q390,180 430,170" stroke="#34D399" stroke-width="2.5" fill="none" opacity="0.35"/>
    <path d="M345,100 Q305,90 275,50" stroke="#34D399" stroke-width="2.5" fill="none" opacity="0.35"/>
    <path d="M275,50 Q240,35 210,45" stroke="#34D399" stroke-width="2" fill="none" opacity="0.3"/>
    <path d="M210,45 Q180,55 160,85" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.25"/>
    <path d="M360,550 Q325,555 300,590" stroke="#34D399" stroke-width="2.5" fill="none" opacity="0.35"/>
    <path d="M300,590 Q270,605 250,635" stroke="#34D399" stroke-width="2" fill="none" opacity="0.3"/>
    <path d="M250,635 Q220,645 190,635" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.25"/>
    <path d="M335,240 Q240,270 170,340" stroke="#34D399" stroke-width="2.5" fill="none" opacity="0.3"/>
    <path d="M170,340 Q145,365 140,400" stroke="#34D399" stroke-width="2" fill="none" opacity="0.28"/>
    <path d="M140,400 Q120,420 90,425" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.24"/>
    <path d="M365,80 Q340,60 345,25" stroke="#34D399" stroke-width="2" fill="none" opacity="0.3"/>
    <path d="M370,610 Q400,600 420,615" stroke="#34D399" stroke-width="2" fill="none" opacity="0.3"/>
    <path d="M310,380 Q270,375 245,350" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.22"/>
    <path d="M325,230 Q295,215 285,185" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.22"/>
    <path d="M320,500 Q355,495 380,510" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.22"/>
    <path d="M350,180 Q380,170 395,190" stroke="#34D399" stroke-width="1.5" fill="none" opacity="0.22"/>

    <ellipse cx="260" cy="340" rx="26" ry="13" fill="#34D399" opacity="0.3" transform="rotate(145 260 340)"/>
    <ellipse cx="200" cy="385" rx="16" ry="8" fill="#34D399" opacity="0.26" transform="rotate(135 200 385)"/>
    <ellipse cx="140" cy="410" rx="11" ry="5.5" fill="#34D399" opacity="0.22" transform="rotate(130 140 410)"/>
    <ellipse cx="285" cy="450" rx="22" ry="11" fill="#34D399" opacity="0.3" transform="rotate(125 285 450)"/>
    <ellipse cx="230" cy="495" rx="15" ry="7.5" fill="#34D399" opacity="0.26" transform="rotate(120 230 495)"/>
    <ellipse cx="175" cy="515" rx="10" ry="5" fill="#34D399" opacity="0.22" transform="rotate(115 175 515)"/>
    <ellipse cx="335" cy="240" rx="24" ry="12" fill="#34D399" opacity="0.3" transform="rotate(200 335 240)"/>
    <ellipse cx="390" cy="185" rx="20" ry="10" fill="#34D399" opacity="0.3" transform="rotate(250 390 185)"/>
    <ellipse cx="365" cy="120" rx="22" ry="11" fill="#34D399" opacity="0.3" transform="rotate(190 365 120)"/>
    <ellipse cx="210" cy="45" rx="15" ry="7.5" fill="#34D399" opacity="0.26" transform="rotate(165 210 45)"/>
    <ellipse cx="160" cy="85" rx="10" ry="5" fill="#34D399" opacity="0.22" transform="rotate(170 160 85)"/>
    <ellipse cx="275" cy="50" rx="20" ry="10" fill="#34D399" opacity="0.3" transform="rotate(120 275 50)"/>
    <ellipse cx="300" cy="590" rx="18" ry="9" fill="#34D399" opacity="0.3" transform="rotate(210 300 590)"/>
    <ellipse cx="250" cy="635" rx="14" ry="7" fill="#34D399" opacity="0.26" transform="rotate(220 250 635)"/>
    <ellipse cx="190" cy="635" rx="10" ry="5" fill="#34D399" opacity="0.22" transform="rotate(225 190 635)"/>
    <ellipse cx="120" cy="365" rx="16" ry="8" fill="#34D399" opacity="0.28" transform="rotate(200 120 365)"/>
    <ellipse cx="140" cy="400" rx="14" ry="7" fill="#34D399" opacity="0.25" transform="rotate(190 140 400)"/>
    <ellipse cx="90" cy="425" rx="10" ry="5" fill="#34D399" opacity="0.2" transform="rotate(185 90 425)"/>
    <ellipse cx="345" cy="25" rx="13" ry="6.5" fill="#34D399" opacity="0.26" transform="rotate(220 345 25)"/>
    <ellipse cx="420" cy="615" rx="13" ry="6.5" fill="#34D399" opacity="0.26" transform="rotate(150 420 615)"/>
    <ellipse cx="245" cy="350" rx="12" ry="6" fill="#34D399" opacity="0.2" transform="rotate(220 245 350)"/>
    <ellipse cx="285" cy="185" rx="11" ry="5.5" fill="#34D399" opacity="0.2" transform="rotate(235 285 185)"/>
    <ellipse cx="380" cy="510" rx="11" ry="5.5" fill="#34D399" opacity="0.2" transform="rotate(200 380 510)"/>
    <ellipse cx="395" cy="190" rx="11" ry="5.5" fill="#34D399" opacity="0.2" transform="rotate(240 395 190)"/>

    <g transform="translate(275,50)">
        <ellipse cx="-10" cy="-6" rx="9" ry="5" fill="#34D399" opacity="0.25"/>
        <ellipse cx="10" cy="-6" rx="9" ry="5" fill="#34D399" opacity="0.25" transform="rotate(72 10 -6)"/>
        <ellipse cx="8" cy="10" rx="9" ry="5" fill="#34D399" opacity="0.25" transform="rotate(144 8 10)"/>
        <ellipse cx="-8" cy="10" rx="9" ry="5" fill="#34D399" opacity="0.25" transform="rotate(216 -8 10)"/>
        <ellipse cx="0" cy="-12" rx="9" ry="5" fill="#34D399" opacity="0.25" transform="rotate(288 0 -12)"/>
        <circle cx="0" cy="0" r="8" fill="#F59E0B" opacity="0.8"/>
    </g>
    <g transform="translate(300,590)">
        <ellipse cx="-8" cy="-5" rx="7" ry="4" fill="#34D399" opacity="0.25"/>
        <ellipse cx="8" cy="-5" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(72 8 -5)"/>
        <ellipse cx="6" cy="8" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(144 6 8)"/>
        <ellipse cx="-6" cy="8" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(216 -6 8)"/>
        <ellipse cx="0" cy="-10" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(288 0 -10)"/>
        <circle cx="0" cy="0" r="7" fill="#F59E0B" opacity="0.8"/>
    </g>
    <g transform="translate(335,240)">
        <ellipse cx="-8" cy="-5" rx="7" ry="4" fill="#34D399" opacity="0.25"/>
        <ellipse cx="8" cy="-5" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(72 8 -5)"/>
        <ellipse cx="6" cy="8" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(144 6 8)"/>
        <ellipse cx="-6" cy="8" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(216 -6 8)"/>
        <ellipse cx="0" cy="-10" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(288 0 -10)"/>
        <circle cx="0" cy="0" r="7" fill="#F59E0B" opacity="0.8"/>
    </g>
    <g transform="translate(300,50)">
        <ellipse cx="-8" cy="-5" rx="7" ry="4" fill="#34D399" opacity="0.25"/>
        <ellipse cx="8" cy="-5" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(72 8 -5)"/>
        <ellipse cx="6" cy="8" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(144 6 8)"/>
        <ellipse cx="-6" cy="8" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(216 -6 8)"/>
        <ellipse cx="0" cy="-10" rx="7" ry="4" fill="#34D399" opacity="0.25" transform="rotate(288 0 -10)"/>
        <circle cx="0" cy="0" r="7" fill="#F59E0B" opacity="0.8"/>
    </g>
    <g transform="translate(200,385)">
        <ellipse cx="-6" cy="-4" rx="5" ry="3" fill="#34D399" opacity="0.22"/>
        <ellipse cx="6" cy="-4" rx="5" ry="3" fill="#34D399" opacity="0.22" transform="rotate(72 6 -4)"/>
        <ellipse cx="5" cy="6" rx="5" ry="3" fill="#34D399" opacity="0.22" transform="rotate(144 5 6)"/>
        <ellipse cx="-5" cy="6" rx="5" ry="3" fill="#34D399" opacity="0.22" transform="rotate(216 -5 6)"/>
        <ellipse cx="0" cy="-8" rx="5" ry="3" fill="#34D399" opacity="0.22" transform="rotate(288 0 -8)"/>
        <circle cx="0" cy="0" r="5" fill="#F59E0B" opacity="0.7"/>
    </g>
    <g transform="translate(230,495)">
        <ellipse cx="-6" cy="-4" rx="5" ry="3" fill="#34D399" opacity="0.2"/>
        <ellipse cx="6" cy="-4" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(72 6 -4)"/>
        <ellipse cx="5" cy="6" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(144 5 6)"/>
        <ellipse cx="-5" cy="6" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(216 -5 6)"/>
        <ellipse cx="0" cy="-8" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(288 0 -8)"/>
        <circle cx="0" cy="0" r="5" fill="#F59E0B" opacity="0.65"/>
    </g>
    <g transform="translate(250,635)">
        <ellipse cx="-6" cy="-4" rx="5" ry="3" fill="#34D399" opacity="0.2"/>
        <ellipse cx="6" cy="-4" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(72 6 -4)"/>
        <ellipse cx="5" cy="6" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(144 5 6)"/>
        <ellipse cx="-5" cy="6" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(216 -5 6)"/>
        <ellipse cx="0" cy="-8" rx="5" ry="3" fill="#34D399" opacity="0.2" transform="rotate(288 0 -8)"/>
        <circle cx="0" cy="0" r="5" fill="#F59E0B" opacity="0.65"/>
    </g>
    <circle cx="370" cy="360" r="6" fill="#34D399" opacity="0.3"/>
    <circle cx="180" cy="390" r="4" fill="#34D399" opacity="0.25"/>
    <circle cx="100" cy="290" r="3" fill="#34D399" opacity="0.2"/>
    <circle cx="165" cy="620" r="3" fill="#34D399" opacity="0.2"/>
</svg>
"""

def show_signup():
    if st.session_state.get("logged_in"):
        st.query_params["page"] = "chat"
        st.rerun()
    if "signup_submitting" not in st.session_state:
        st.session_state["signup_submitting"] = False
    if "signup_error" not in st.session_state:
        st.session_state["signup_error"] = None
    if "signup_success" not in st.session_state:
        st.session_state["signup_success"] = False

    top_left_b64 = get_base64_svg(BOTANICAL_ART_TOP_LEFT)
    bottom_right_b64 = get_base64_svg(BOTANICAL_ART_BOTTOM_RIGHT)

    st.markdown(
        f"""
        <style>
        .botanical-top-left {{
            background-image: url('data:image/svg+xml;base64,{top_left_b64}');
            background-repeat: no-repeat;
        }}
        .botanical-bottom-right {{
            background-image: url('data:image/svg+xml;base64,{bottom_right_b64}');
            background-repeat: no-repeat;
        }}
        </style>
        <div class="botanical-corner botanical-top-left"></div>
        <div class="botanical-corner botanical-bottom-right"></div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <a href="?page=home" target="_self" class="back-home-link">‹ Back to Home</a>
        """,
        unsafe_allow_html=True
    )

    with st.form("signup_form"):
        st.markdown(
            """
            <div class="auth-logo">🌿 AgriAdvisor</div>
            <div class="auth-title">Your Farm, Backed by AI</div>
            <div class="auth-subtitle">Sign up for free and get guidance built for Nigerian conditions.</div>
            """,
            unsafe_allow_html=True
        )

        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password", autocomplete="new-password")

        button_label = "Signing Up..." if st.session_state["signup_submitting"] else "Sign Up"
        submitted = st.form_submit_button(button_label, disabled=st.session_state["signup_submitting"] or st.session_state["signup_success"])

        if submitted:
            first_name = first_name.strip()
            last_name = last_name.strip()
            email = email.strip()
            if not first_name or not last_name or not email or not password:
                st.error("Please fill in all fields.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                st.session_state["signup_submitting"] = True
                st.session_state["signup_first_name"] = first_name
                st.session_state["signup_last_name"] = last_name
                st.session_state["signup_email"] = email
                st.session_state["signup_password"] = password
                st.session_state["signup_error"] = None
                st.rerun()

        if st.session_state["signup_submitting"]:
            first = st.session_state.pop("signup_first_name", "")
            last = st.session_state.pop("signup_last_name", "")
            stored_email = st.session_state.pop("signup_email", "")
            stored_password = st.session_state.pop("signup_password", "")

            error_message = None
            try:
                supabase = get_supabase_client()
                supabase.auth.sign_up({
                    "email": stored_email,
                    "password": stored_password,
                    "options": {
                        "email_redirect_to": st.secrets.get("APP_URL", "http://localhost:8501") + "/?page=login",
                        "data": {"first_name": first, "last_name": last}
                    }
                })
            except Exception as e:
                msg = str(e).lower()
                if "rate limit" in msg or "too many" in msg:
                    error_message = "Too many attempts. Please wait a few minutes and try again."
                elif "password" in msg:
                    error_message = "That password doesn't meet the requirements. Try a longer one."
                elif "email" in msg and "invalid" in msg:
                    error_message = "That email address doesn't look valid."
                elif any(w in msg for w in ("connect", "timeout", "network", "resolve")):
                    error_message = "Couldn't reach the server. Check your connection and try again."
                else:
                    error_message = "Something went wrong. Please try again."
                logger.exception("Signup failed")

            st.session_state["signup_submitting"] = False
            if error_message:
                st.session_state["signup_error"] = error_message
            else:
                st.session_state["signup_success"] = True
            st.rerun()

        if st.session_state.get("signup_error"):
            st.error(st.session_state["signup_error"])

        if st.session_state.get("signup_success"):
            st.success("Almost there! Confirm your email to activate your account. Didn't get it? Refresh the page to try again.")

        st.markdown(
            """
            <div class="auth-links">
                <span class="auth-divider">Already have an account? <a href="?page=login" target="_self" class="auth-link-bold">Log in</a></span>
            </div>
            """,
            unsafe_allow_html=True
        )