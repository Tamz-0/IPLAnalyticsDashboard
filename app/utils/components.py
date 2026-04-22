import streamlit as st
from utils.theme import COLORS


# ----------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------
def sidebar_header(subtitle: str) -> None:
    st.sidebar.markdown(f"""
    <div style="padding:8px 4px 16px;border-bottom:1px solid {COLORS['border']};
                margin-bottom:16px;">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:22px;
                    font-weight:800;color:{COLORS['text_primary']};letter-spacing:0.06em;">
            IPL ANALYTICS
        </div>
        <div style="font-size:11px;color:{COLORS['text_dim']};letter-spacing:0.1em;
                    text-transform:uppercase;margin-top:4px;">
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_label(text: str) -> None:
    st.sidebar.markdown(
        f"<p style='font-size:11px;text-transform:uppercase;letter-spacing:0.08em;"
        f"color:{COLORS['text_dim']};font-weight:600;margin:14px 0 4px;'>{text}</p>",
        unsafe_allow_html=True,
    )


def sidebar_footer(start_year: int, end_year: int) -> None:
    st.sidebar.markdown(
        f"<p style='font-size:11px;color:{COLORS['text_faint']};text-align:center;"
        f"letter-spacing:0.06em;margin-top:16px;'>"
        f"DATA &middot; IPL {start_year}&ndash;{end_year}"
        f"<br>Built By Taha Murad Zaman"
        f"<br><a href='https://github.com/Tamz-0' style='font-size:11px;color:{COLORS['text_faint']};text-align:center;'>GitHub</a>"
        f"<br><a href='https://www.linkedin.com/in/taha-0-zaman/' style='font-size:11px;color:{COLORS['text_faint']};text-align:center;'>Linkdin</a></p>",
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------
# PAGE HEADER
# ----------------------------------------------------------------
def page_header(title: str, subtitle: str, accent: str = None) -> None:
    color = accent or COLORS["accent"]
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;
                margin-bottom:28px;padding-bottom:20px;
                border-bottom:1px solid {COLORS['border']};">
        <div style="width:6px;align-self:stretch;background:{color};
                    border-radius:3px;flex-shrink:0;"></div>
        <div>
            <div style="font-family:'Barlow Condensed',sans-serif;
                        font-size:34px;font-weight:800;color:{COLORS['text_primary']};
                        letter-spacing:0.04em;line-height:1;">
                {title}
            </div>
            <div style="font-size:12px;color:{COLORS['text_dim']};letter-spacing:0.1em;
                        text-transform:uppercase;margin-top:3px;">
                {subtitle}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------------
# SECTION HEADER
# ----------------------------------------------------------------
def section_header(title: str, color: str = None) -> None:
    c = color or COLORS["accent"]
    st.markdown(f"""
    <div style="font-family:'Barlow Condensed',sans-serif;font-size:18px;
                font-weight:700;letter-spacing:0.06em;text-transform:uppercase;
                color:{COLORS['text_primary']};margin:24px 0 16px;
                padding-left:10px;border-left:3px solid {c};">
        {title}
    </div>""", unsafe_allow_html=True)


# ----------------------------------------------------------------
# STAT CARD
# ----------------------------------------------------------------
def stat_card(
    col,
    label: str,
    value: str,
    value_color: str = None,
    accent: str = None,
) -> None:
    vc = value_color or COLORS["text_primary"]
    ac = accent or COLORS["accent"]
    col.markdown(f"""
    <div style="background:{COLORS['bg_surface']};border:1px solid {COLORS['border']};
                border-top:3px solid {ac};border-radius:10px;padding:14px 16px;">
        <div style="font-size:10px;text-transform:uppercase;
                    letter-spacing:0.1em;color:{COLORS['text_dim']};margin-bottom:6px;">
            {label}
        </div>
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:26px;font-weight:800;color:{vc};">
            {value}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------------
# CHAMPION BANNER
# ----------------------------------------------------------------
def champion_banner(team_name: str, season: int, team_color: str) -> None:
    st.markdown(f"""
    <div style="background:{COLORS['bg_surface']};border:1px solid {COLORS['border']};
                border-left:6px solid {team_color};border-radius:12px;
                padding:24px 28px;display:flex;align-items:center;gap:20px;
                margin-bottom:28px;">
        <div style="font-size:36px;line-height:1;">&#x1F3C6;</div>
        <div>
            <div style="font-family:'Barlow Condensed',sans-serif;
                        font-size:36px;font-weight:800;
                        color:{team_color};letter-spacing:0.04em;line-height:1.1;">
                {team_name.upper()}
            </div>
            <div style="font-size:12px;color:{COLORS['text_dim']};
                        letter-spacing:0.12em;text-transform:uppercase;margin-top:4px;">
                IPL {season} Champions
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------------
# LEADERBOARD CARD — rendered via st.components.v1.html
# ----------------------------------------------------------------
def leaderboard_card(
    title: str,
    data,
    value_label: str,
    accent: str = None,
) -> str:
    ac = accent or COLORS["amber"]
    rows = ""
    items = list(data.items())
    for i, (name, val) in enumerate(items, 1):
        is_first   = i == 1
        name_color = ac if is_first else COLORS["text_primary"]
        val_color  = ac if is_first else COLORS["text_muted"]
        rank_style = (
            f"font-family:'Barlow Condensed',sans-serif;font-size:16px;"
            f"font-weight:800;color:{ac};"
            if is_first
            else f"font-size:13px;color:{COLORS['text_faint']};"
        )
        border = f"border-bottom:1px solid {COLORS['border']};" if i < len(items) else ""
        rows += f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:10px 0;{border}">
            <span style="{rank_style}min-width:24px;">#{i}</span>
            <span style="color:{name_color};font-size:14px;flex:1;padding:0 12px;
                         font-weight:{'700' if is_first else '400'};">
                {name}
            </span>
            <span style="color:{val_color};font-family:'Barlow Condensed',sans-serif;
                         font-size:18px;font-weight:700;">
                {int(val)}
                <span style="font-size:11px;color:{COLORS['text_dim']};font-weight:400;">
                    {value_label}
                </span>
            </span>
        </div>
        """

    return f"""
    <style>
        body {{ margin:0; background:{COLORS['bg_surface']}; }}
    </style>
    <div style="background:{COLORS['bg_surface']};border:1px solid {COLORS['border']};
                border-top:3px solid {ac};border-radius:10px;padding:16px 20px;">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:14px;
                    font-weight:700;text-transform:uppercase;letter-spacing:0.08em;
                    color:{COLORS['text_dim']};margin-bottom:12px;">{title}</div>
        {rows}
    </div>
    """.strip()


# ----------------------------------------------------------------
# RIVALRY BANNER  (team vs team summary)
# ----------------------------------------------------------------
def rivalry_banner(team1: str, team2: str, w1: int, w2: int) -> None:
    st.markdown(f"""
    <div style="background:{COLORS['bg_surface']};border:1px solid {COLORS['border']};
                border-radius:12px;padding:24px 28px;
                display:flex;justify-content:space-between;align-items:center;
                margin-bottom:24px;">
        <div>
            <div style="font-size:11px;text-transform:uppercase;
                        letter-spacing:0.1em;color:{COLORS['text_dim']};
                        margin-bottom:4px;">Rivalry</div>
            <div style="font-family:'Barlow Condensed',sans-serif;
                        font-size:28px;font-weight:800;color:{COLORS['text_primary']};">
                {team1} vs {team2}
            </div>
        </div>
        <div style="font-family:'Barlow Condensed',sans-serif;
                    font-size:40px;font-weight:800;color:{COLORS['text_primary']};">
            {w1} &ndash; {w2}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------------
# SPLIT BAR  (two-color progress)
# ----------------------------------------------------------------
def split_bar(
    label_left: str,
    label_right: str,
    pct_left: float,
    color_left: str,
    color_right: str,
) -> None:
    pct_right = 1.0 - pct_left
    st.markdown(f"""
    <div style="margin-top:8px;">
        <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;
                    color:{COLORS['text_faint']};margin-bottom:6px;">
            {label_left} &nbsp;&middot;&nbsp; {label_right}
        </div>
        <div style="display:flex;height:10px;border-radius:5px;overflow:hidden;">
            <div style="width:{pct_left*100:.1f}%;background:{color_left};"></div>
            <div style="width:{pct_right*100:.1f}%;background:{color_right};"></div>
        </div>
        <div style="display:flex;justify-content:space-between;
                    font-family:'Barlow Condensed',sans-serif;
                    font-size:18px;font-weight:800;margin-top:6px;">
            <span style="color:{color_left};">{pct_left*100:.0f}%</span>
            <span style="color:{color_right};">{pct_right*100:.0f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------------
# SPACER
# ----------------------------------------------------------------
def spacer(px: int = 8) -> None:
    st.markdown(f"<div style='height:{px}px'></div>", unsafe_allow_html=True)