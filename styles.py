import streamlit as st
import urllib.parse

def get_career_path_svg_url():
    """
    Constructs and URL-encodes a majestic CareerPath.AI illustration vector matching the
    exact UI design: soft blue silk ribbon waves, top-left & bottom-right dot matrices,
    and the ascending mountain staircase with a climber reaching the summit victory flag.
    """
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" width="100%" height="100%">'
        '<defs>'
        '<linearGradient id="waveGradLeft1" x1="0%" y1="100%" x2="100%" y2="0%">'
        '<stop offset="0%" stop-color="#1d4ed8" stop-opacity="0.85" />'
        '<stop offset="40%" stop-color="#2563eb" stop-opacity="0.75" />'
        '<stop offset="80%" stop-color="#60a5fa" stop-opacity="0.45" />'
        '<stop offset="100%" stop-color="#93c5fd" stop-opacity="0" />'
        '</linearGradient>'
        '<linearGradient id="waveGradLeft2" x1="0%" y1="100%" x2="100%" y2="0%">'
        '<stop offset="0%" stop-color="#2563eb" stop-opacity="0.9" />'
        '<stop offset="50%" stop-color="#38bdf8" stop-opacity="0.65" />'
        '<stop offset="100%" stop-color="#bfdbfe" stop-opacity="0.1" />'
        '</linearGradient>'
        '<linearGradient id="mountainGrad1" x1="0%" y1="100%" x2="100%" y2="0%">'
        '<stop offset="0%" stop-color="#bfdbfe" stop-opacity="0.2" />'
        '<stop offset="100%" stop-color="#3b82f6" stop-opacity="0.35" />'
        '</linearGradient>'
        '<linearGradient id="mountainGrad2" x1="0%" y1="100%" x2="100%" y2="0%">'
        '<stop offset="0%" stop-color="#93c5fd" stop-opacity="0.25" />'
        '<stop offset="100%" stop-color="#2563eb" stop-opacity="0.45" />'
        '</linearGradient>'
        '</defs>'
        '<rect width="1600" height="1000" fill="#f8fafc" />'
        '<!-- Top-Left Dot Grid Matrix -->'
        '<g opacity="0.4" fill="#3b82f6">'
        '<circle cx="45" cy="55" r="2.8"/><circle cx="65" cy="55" r="2.8"/><circle cx="85" cy="55" r="2.8"/><circle cx="105" cy="55" r="2.8"/>'
        '<circle cx="45" cy="75" r="2.8"/><circle cx="65" cy="75" r="2.8"/><circle cx="85" cy="75" r="2.8"/><circle cx="105" cy="75" r="2.8"/>'
        '<circle cx="45" cy="95" r="2.8"/><circle cx="65" cy="95" r="2.8"/><circle cx="85" cy="95" r="2.8"/><circle cx="105" cy="95" r="2.8"/>'
        '<circle cx="45" cy="115" r="2.8"/><circle cx="65" cy="115" r="2.8"/><circle cx="85" cy="115" r="2.8"/><circle cx="105" cy="115" r="2.8"/>'
        '<circle cx="45" cy="135" r="2.8"/><circle cx="65" cy="135" r="2.8"/><circle cx="85" cy="135" r="2.8"/><circle cx="105" cy="135" r="2.8"/>'
        '<circle cx="45" cy="155" r="2.8"/><circle cx="65" cy="155" r="2.8"/><circle cx="85" cy="155" r="2.8"/><circle cx="105" cy="155" r="2.8"/>'
        '</g>'
        '<!-- Bottom-Right Dot Grid Matrix -->'
        '<g opacity="0.4" fill="#3b82f6">'
        '<circle cx="1495" cy="815" r="2.8"/><circle cx="1515" cy="815" r="2.8"/><circle cx="1535" cy="815" r="2.8"/><circle cx="1555" cy="815" r="2.8"/>'
        '<circle cx="1495" cy="835" r="2.8"/><circle cx="1515" cy="835" r="2.8"/><circle cx="1535" cy="835" r="2.8"/><circle cx="1555" cy="835" r="2.8"/>'
        '<circle cx="1495" cy="855" r="2.8"/><circle cx="1515" cy="855" r="2.8"/><circle cx="1535" cy="855" r="2.8"/><circle cx="1555" cy="855" r="2.8"/>'
        '<circle cx="1495" cy="875" r="2.8"/><circle cx="1515" cy="875" r="2.8"/><circle cx="1535" cy="875" r="2.8"/><circle cx="1555" cy="875" r="2.8"/>'
        '<circle cx="1495" cy="895" r="2.8"/><circle cx="1515" cy="895" r="2.8"/><circle cx="1535" cy="895" r="2.8"/><circle cx="1555" cy="895" r="2.8"/>'
        '<circle cx="1495" cy="915" r="2.8"/><circle cx="1515" cy="915" r="2.8"/><circle cx="1535" cy="915" r="2.8"/><circle cx="1555" cy="915" r="2.8"/>'
        '</g>'
        '<!-- Sun Aura behind mountain peak -->'
        '<circle cx="1520" cy="360" r="110" fill="#ffffff" opacity="0.95" />'
        '<circle cx="1520" cy="360" r="160" fill="#dbeafe" opacity="0.4" />'
        '<!-- Mountain Layers -->'
        '<path d="M 1150,1000 L 1260,680 L 1400,500 L 1520,380 L 1650,470 L 1650,1000 Z" fill="url(#mountainGrad1)" />'
        '<path d="M 1220,1000 L 1310,740 L 1390,610 L 1480,460 L 1530,400 L 1650,490 L 1650,1000 Z" fill="url(#mountainGrad2)" />'
        '<!-- Ascending Stepping Stones Stairway -->'
        '<path d="M 1240,790 Q 1330,700 1375,630 T 1445,535 T 1505,450 T 1530,400" fill="none" stroke="#ffffff" stroke-width="26" stroke-linecap="round" opacity="0.85"/>'
        '<path d="M 1240,790 Q 1330,700 1375,630 T 1445,535 T 1505,450 T 1530,400" fill="none" stroke="#2563eb" stroke-width="3" stroke-dasharray="6,8" opacity="0.75"/>'
        '<path d="M 1285,735 L 1335,715" stroke="#ffffff" stroke-width="6" stroke-linecap="round"/>'
        '<path d="M 1335,675 L 1380,658" stroke="#ffffff" stroke-width="6" stroke-linecap="round"/>'
        '<path d="M 1385,615 L 1425,600" stroke="#ffffff" stroke-width="6" stroke-linecap="round"/>'
        '<path d="M 1435,545 L 1470,535" stroke="#ffffff" stroke-width="6" stroke-linecap="round"/>'
        '<path d="M 1480,480 L 1510,470" stroke="#ffffff" stroke-width="6" stroke-linecap="round"/>'
        '<!-- Climber Silhouette Figure -->'
        '<g transform="translate(1388, 455) scale(0.7)" fill="#2563eb">'
        '<circle cx="16" cy="6" r="5" />'
        '<path d="M 16,12 L 13,28 L 8,32 L 6,42 M 13,28 L 19,38 L 24,44" stroke="#2563eb" stroke-width="3.5" stroke-linecap="round"/>'
        '<path d="M 16,14 L 22,22 L 28,18 M 16,14 L 8,24" stroke="#2563eb" stroke-width="3.5" stroke-linecap="round"/>'
        '</g>'
        '<!-- Summit Flag -->'
        '<line x1="1530" y1="400" x2="1530" y2="340" stroke="#1d4ed8" stroke-width="3" stroke-linecap="round" />'
        '<path d="M 1530,342 L 1565,356 L 1530,370 Z" fill="#2563eb" />'
        '<!-- Bottom-Left Flowing Organic Silk Ribbon Waves -->'
        '<path d="M -50,620 C 130,620 230,750 340,820 C 470,890 600,860 740,1050 L -50,1050 Z" fill="url(#waveGradLeft2)" />'
        '<path d="M -50,710 C 110,710 200,850 300,900 C 410,950 510,920 620,1050 L -50,1050 Z" fill="url(#waveGradLeft1)" />'
        '</svg>'
    )
    return f"data:image/svg+xml,{urllib.parse.quote(svg)}"

def apply_custom_styles():
    """
    Transforms Streamlit into a modern, high-conversion White and Blue SaaS UI matching
    the exact design from the specification and user screenshot.
    """
    try:
        import assets_b64
        bg_b64 = assets_b64.CLEAN_BG_B64
    except Exception:
        bg_b64 = ""

    js_flowing_waves = f"""
    <script>
        const parentDoc = window.parent.document;
        let existingCanvas = parentDoc.getElementById('careerPathFlowingCanvas');
        if (existingCanvas) {{
            existingCanvas.remove();
        }}
        
        const wrap = parentDoc.createElement('div');
        wrap.id = 'careerPathFlowingCanvas';
        wrap.style.position = 'fixed';
        wrap.style.top = '0';
        wrap.style.left = '0';
        wrap.style.width = '100vw';
        wrap.style.height = '100vh';
        wrap.style.pointerEvents = 'none';
        wrap.style.zIndex = '0';
        wrap.style.overflow = 'hidden';
        wrap.style.backgroundColor = '#f8fafc';
        wrap.style.backgroundImage = 'url("data:image/png;base64,{bg_b64}")';
        wrap.style.backgroundRepeat = 'no-repeat';
        wrap.style.backgroundPosition = 'center center';
        wrap.style.backgroundSize = 'cover';
        
        parentDoc.body.prepend(wrap);
    </script>
    """
    import streamlit.components.v1 as components
    components.html(js_flowing_waves, height=0, width=0)


    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

            /* Complete Streamlit Default Chrome Removal */
            header[data-testid="stHeader"] { display: none !important; }
            div[data-testid="stDecoration"] { display: none !important; }
            div[data-testid="stStatusWidget"] { display: none !important; }
            #MainMenu { visibility: hidden !important; }
            footer { display: none !important; }
            [data-testid="collapsedControl"] { display: none !important; }
            section[data-testid="stSidebar"] { display: none !important; }

            /* Enterprise White & Royal Blue Design System Variables */
            :root {
                --primary: #2563eb;
                --primary-dark: #1d4ed8;
                --primary-light: #60a5fa;
                --primary-glow: rgba(37, 99, 235, 0.25);
                --bg-base: #f8fafc;
                --bg-card: rgba(255, 255, 255, 0.98);
                --border-card: rgba(226, 232, 240, 0.95);
                --text-main: #0f172a;
                --text-muted: #475569;
                --text-sub: #64748b;
                --accent-blue: #0284c7;
                --soft-blue: #eff6ff;
            }

            /* Global App Canvas */
            html, body, [class*="css"], .stApp {
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
                background-color: transparent !important;
                color: #0f172a !important;
            }

            /* Headers and Core Typography */
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                color: #0f172a !important;
                font-weight: 800 !important;
                letter-spacing: -0.4px !important;
            }
            p, span, div, label {
                color: #334155;
            }

            /* Main Layout Width & Margins */
            .main .block-container {
                position: relative !important;
                z-index: 1 !important;
                padding-top: 1.2rem !important;
                padding-bottom: 3.5rem !important;
                max-width: 1200px !important;
            }

            /* Top Unified Header matching media_1791308758811.png */
            .unified-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: #ffffff;
                border-radius: 20px;
                padding: 12px 28px;
                border: 1px solid rgba(226, 232, 240, 0.85);
                box-shadow: 0 4px 20px rgba(37, 99, 235, 0.05);
                margin-bottom: 24px;
            }

            /* Outstanding Merged Navbar Buttons */
            div[data-testid="column"]:nth-of-type(2) div.stButton > button,
            button[data-testid*="nav_resume_analyzer"],
            button[data-testid*="nav_mock_test"],
            button[data-testid*="nav_performance"] {
                border-radius: 20px !important;
                padding: 10px 16px !important;
                font-weight: 700 !important;
                font-size: 0.95rem !important;
                transition: all 0.25s ease !important;
                min-height: 46px !important;
                height: 46px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }
            div[data-testid="column"]:nth-of-type(2) div.stButton > button[kind="primary"],
            button[data-testid*="nav_resume_analyzer"][kind="primary"],
            button[data-testid*="nav_mock_test"][kind="primary"],
            button[data-testid*="nav_performance"][kind="primary"] {
                background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
                color: #ffffff !important;
                border: none !important;
                box-shadow: 0 4px 18px rgba(37, 99, 235, 0.35) !important;
            }
            div[data-testid="column"]:nth-of-type(2) div.stButton > button[kind="secondary"],
            button[data-testid*="nav_resume_analyzer"][kind="secondary"],
            button[data-testid*="nav_mock_test"][kind="secondary"],
            button[data-testid*="nav_performance"][kind="secondary"] {
                background: #ffffff !important;
                color: #334155 !important;
                border: 1.5px solid #e2e8f0 !important;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
            }
            div[data-testid="column"]:nth-of-type(2) div.stButton > button[kind="secondary"]:hover,
            button[data-testid*="nav_resume_analyzer"][kind="secondary"]:hover,
            button[data-testid*="nav_mock_test"][kind="secondary"]:hover,
            button[data-testid*="nav_performance"][kind="secondary"]:hover {
                border-color: #93c5fd !important;
                background: #f8fafc !important;
                color: #1d4ed8 !important;
                transform: translateY(-1px) !important;
            }

            /* Outstanding Action Tiles for View Analysis & Take Mock Test */
            div.stButton > button[key*="btn_view_analysis"],
            div.stButton > button[key*="btn_take_mock_test"],
            button[data-testid*="btn_view_analysis"],
            button[data-testid*="btn_take_mock_test"] {
                background: #ffffff !important;
                border: 1.5px solid #e2e8f0 !important;
                border-radius: 20px !important;
                padding: 16px 22px !important;
                color: #0f172a !important;
                box-shadow: 0 4px 16px rgba(37, 99, 235, 0.05) !important;
                text-align: left !important;
                white-space: pre-line !important;
                line-height: 1.4 !important;
                font-weight: 700 !important;
                font-size: 0.95rem !important;
                transition: all 0.25s ease !important;
            }
            div.stButton > button[key*="btn_view_analysis"]:hover,
            div.stButton > button[key*="btn_take_mock_test"]:hover,
            button[data-testid*="btn_view_analysis"]:hover,
            button[data-testid*="btn_take_mock_test"]:hover {
                border-color: #60a5fa !important;
                background: #f8fafc !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 24px rgba(37, 99, 235, 0.12) !important;
            }

            /* Logged-in Dashboard Cards */
            .dash-main-card {
                background: #ffffff;
                border-radius: 24px;
                border: 1px solid rgba(226, 232, 240, 0.85);
                padding: 36px 40px;
                box-shadow: 0 10px 30px rgba(37, 99, 235, 0.05);
                position: relative;
                overflow: hidden;
                height: 100%;
            }
            .badge-ai-assistant {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: #eff6ff;
                color: #2563eb;
                font-size: 0.95rem;
                font-weight: 800;
                padding: 7px 18px;
                border-radius: 20px;
                border: 1.5px solid #bfdbfe;
                margin-bottom: 16px;
            }
            .dash-main-title {
                font-size: 2.55rem;
                font-weight: 900;
                line-height: 1.18;
                color: #1e3a8a;
                letter-spacing: -0.8px;
                margin-bottom: 16px;
            }
            .dash-main-subtitle {
                font-size: 1.12rem;
                color: #475569;
                line-height: 1.68;
                margin-bottom: 30px;
                max-width: 520px;
                font-weight: 500;
            }
            .features-trio {
                display: flex;
                gap: 24px;
                align-items: center;
                flex-wrap: wrap;
            }
            .feature-trio-item {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            .feature-trio-icon {
                width: 42px;
                height: 42px;
                border-radius: 12px;
                background: #eff6ff;
                border: 1.5px solid #bfdbfe;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
            }
            .feature-trio-title {
                font-size: 1.0rem;
                font-weight: 800;
                color: #0f172a;
            }
            .feature-trio-desc {
                font-size: 0.88rem;
                color: #64748b;
                font-weight: 500;
            }

            /* Right Action Cards */
            .action-tile-primary {
                background: linear-gradient(90deg, #2563eb 0%, #0284c7 60%, #06b6d4 100%);
                border-radius: 20px;
                padding: 24px 28px;
                color: #ffffff;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 10px 25px rgba(37, 99, 235, 0.25);
                margin-bottom: 16px;
                cursor: pointer;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .action-tile-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 14px 30px rgba(37, 99, 235, 0.35);
            }
            .action-tile-secondary {
                background: #ffffff;
                border: 1px solid rgba(226, 232, 240, 0.9);
                border-radius: 20px;
                padding: 20px 26px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 4px 16px rgba(37, 99, 235, 0.04);
                margin-bottom: 16px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .action-tile-secondary:hover {
                border-color: #bfdbfe;
                transform: translateY(-2px);
                box-shadow: 0 8px 22px rgba(37, 99, 235, 0.08);
            }
            .arrow-circle-btn {
                width: 38px;
                height: 38px;
                border-radius: 50%;
                background: #ffffff;
                color: #2563eb;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 800;
                font-size: 18px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }

            /* Recent Uploads & Career Journey Lower Cards */
            .dash-lower-card {
                background: #ffffff;
                border-radius: 24px;
                border: 1px solid rgba(226, 232, 240, 0.85);
                padding: 26px 32px;
                box-shadow: 0 8px 25px rgba(37, 99, 235, 0.04);
                height: 100%;
            }
            .metric-stat-box {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 16px 20px;
                display: flex;
                align-items: center;
                gap: 14px;
                flex: 1;
            }

            /* Pill Capsule Tabs (Sign In, Create Account) */
            div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
            div[data-testid="stTabs"] [data-baseweb="tab-border"] {
                display: none !important;
                background-color: transparent !important;
                height: 0px !important;
            }
            div[data-testid="stTabs"] [data-baseweb="tab-list"] {
                display: flex !important;
                justify-content: center !important;
                gap: 12px !important;
                background-color: #ffffff !important;
                border-radius: 50px !important;
                border: 1px solid rgba(226, 232, 240, 0.85) !important;
                box-shadow: 0 4px 20px rgba(37, 99, 235, 0.05) !important;
                padding: 6px 8px !important;
                max-width: 440px !important;
                margin: 0 auto 22px auto !important;
            }
            div[data-testid="stTabs"] button[role="tab"] {
                border-radius: 40px !important;
                padding: 10px 32px !important;
                font-weight: 700 !important;
                font-size: 0.98rem !important;
                color: #475569 !important;
                background: transparent !important;
                border: none !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 8px !important;
                flex: 1 !important;
            }
            div[data-testid="stTabs"] button[role="tab"]:hover {
                color: #1d4ed8 !important;
            }
            div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
                background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
                color: #ffffff !important;
                box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35) !important;
            }

            /* Auth Card Matching Screenshot Exactly */
            div[data-testid="stForm"] {
                background: #ffffff !important;
                border-radius: 26px !important;
                border: 1px solid rgba(226, 232, 240, 0.85) !important;
                box-shadow: 0 20px 45px rgba(37, 99, 235, 0.07), 0 2px 6px rgba(0, 0, 0, 0.02) !important;
                padding: 36px 40px !important;
                max-width: 530px !important;
                margin: 0 auto !important;
            }
            .auth-card-title {
                font-size: 1.65rem;
                font-weight: 800;
                color: #0f172a;
                margin: 0 0 22px 0;
            }

            /* White & Royal Blue Hero Banner */
            .saas-hero {
                position: relative;
                background: linear-gradient(135deg, rgba(239, 246, 255, 0.95) 0%, rgba(255, 255, 255, 0.98) 100%) !important;
                backdrop-filter: blur(28px) saturate(190%) !important;
                -webkit-backdrop-filter: blur(28px) saturate(190%) !important;
                border: 1.5px solid rgba(191, 219, 254, 0.8) !important;
                border-radius: 24px;
                padding: 34px 38px;
                margin-bottom: 26px;
                box-shadow: 
                    0 18px 45px rgba(37, 99, 235, 0.08),
                    inset 0 1px 1px rgba(255, 255, 255, 0.9) !important;
                overflow: hidden;
            }
            .saas-hero-title {
                font-size: 2.35rem;
                font-weight: 900;
                line-height: 1.18;
                letter-spacing: -1px;
                margin-bottom: 8px;
                background: linear-gradient(135deg, #0f172a 40%, #1d4ed8 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .saas-hero-subtitle {
                font-size: 1.05rem;
                color: #475569;
                max-width: 760px;
                line-height: 1.6;
                margin: 0;
                font-weight: 500;
            }

            /* Crisp Frosted Glassmorphic Panels */
            .glass-panel {
                background: rgba(255, 255, 255, 0.96) !important;
                backdrop-filter: blur(26px) saturate(185%) !important;
                -webkit-backdrop-filter: blur(26px) saturate(185%) !important;
                border: 1.5px solid rgba(226, 232, 240, 0.95) !important;
                border-radius: 22px;
                padding: 26px 30px;
                margin-bottom: 22px;
                box-shadow: 
                    0 14px 35px rgba(37, 99, 235, 0.06),
                    inset 0 1px 1px 0 rgba(255, 255, 255, 0.9) !important;
                transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.25s ease, box-shadow 0.25s ease !important;
            }
            .glass-panel:hover {
                border-color: rgba(37, 99, 235, 0.35) !important;
                transform: translateY(-2px) !important;
                box-shadow: 
                    0 20px 45px rgba(37, 99, 235, 0.12),
                    0 0 20px rgba(59, 130, 246, 0.08) !important;
            }

            /* High-Impact Metric Cards */
            .metric-card {
                background: rgba(255, 255, 255, 0.96) !important;
                backdrop-filter: blur(22px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(22px) saturate(180%) !important;
                border: 1.5px solid rgba(219, 234, 254, 0.9) !important;
                border-top: 4px solid #2563eb !important;
                border-radius: 20px;
                padding: 24px;
                text-align: center;
                box-shadow: 
                    0 12px 30px rgba(37, 99, 235, 0.07),
                    inset 0 1px 1px rgba(255, 255, 255, 0.9) !important;
                transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
            }
            .metric-card:hover {
                transform: translateY(-3px);
                border-color: rgba(37, 99, 235, 0.4) !important;
                border-top-color: #1d4ed8 !important;
                box-shadow: 0 18px 40px rgba(37, 99, 235, 0.15) !important;
            }
            .metric-val {
                font-size: 3.1rem;
                font-weight: 900;
                line-height: 1;
                color: #1d4ed8;
                text-shadow: 0 2px 10px rgba(37, 99, 235, 0.15);
            }
            .metric-lbl {
                font-size: 0.85rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                color: #64748b;
                margin-top: 10px;
            }

            /* Tech Pills */
            .tech-pill {
                display: inline-flex;
                align-items: center;
                background: #eff6ff;
                backdrop-filter: blur(14px);
                color: #1d4ed8;
                border: 1.5px solid #bfdbfe;
                border-radius: 14px;
                padding: 7px 15px;
                margin: 4px;
                font-size: 0.88rem;
                font-weight: 700;
                transition: all 0.25s ease;
            }
            .tech-pill:hover {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                color: #ffffff;
                border-color: #1d4ed8;
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35);
            }

            /* Feedback Insight Cards */
            .insight-card {
                display: flex;
                align-items: flex-start;
                gap: 12px;
                border-radius: 14px;
                padding: 16px 20px;
                margin-bottom: 12px;
                font-size: 0.95rem;
                line-height: 1.5;
                font-weight: 600;
            }
            .insight-card-green {
                background: #f0fdf4 !important;
                border: 1px solid #bbf7d0 !important;
                border-left: 4px solid #16a34a !important;
                color: #166534 !important;
            }
            .insight-card-amber {
                background: #fffbeb !important;
                border: 1px solid #fde68a !important;
                border-left: 4px solid #d97706 !important;
                color: #92400e !important;
            }

            /* Buttons */
            div.stButton > button {
                width: 100%;
                border-radius: 14px !important;
                padding: 13px 26px !important;
                font-weight: 700 !important;
                font-size: 0.98rem !important;
                letter-spacing: 0.2px !important;
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
                border: 1.5px solid #bfdbfe !important;
                background: #ffffff !important;
                color: #1d4ed8 !important;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08) !important;
            }
            div.stButton > button:hover {
                border-color: #2563eb !important;
                background: #eff6ff !important;
                color: #1e40af !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 20px rgba(37, 99, 235, 0.16) !important;
            }
            /* Primary Gradient Blue Button Matching Screenshot */
            div.stButton > button[kind="primary"], div[data-testid="stFormSubmitButton"] > button {
                background: linear-gradient(90deg, #0284c7 0%, #2563eb 50%, #3b82f6 100%) !important;
                border: none !important;
                color: #ffffff !important;
                font-weight: 800 !important;
                box-shadow: 0 6px 24px rgba(37, 99, 235, 0.35) !important;
                border-radius: 16px !important;
                padding: 14px !important;
            }
            div.stButton > button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"] > button:hover {
                background: linear-gradient(90deg, #0369a1 0%, #1d4ed8 50%, #2563eb 100%) !important;
                color: #ffffff !important;
                box-shadow: 0 8px 32px rgba(37, 99, 235, 0.5) !important;
                transform: translateY(-2px) !important;
            }

            /* Outstanding Action Tiles (View Analysis & Take Mock Test) */
            div.stButton > button:has(div:contains("View Analysis")),
            div.stButton > button:has(div:contains("Take Mock Test")),
            div[data-testid="stVerticalBlock"] > div.stButton > button {
                white-space: pre-line !important;
            }

            /* Custom Inputs - 100% Pure White Background Matching Screenshot */
            div[data-baseweb="input"],
            div[data-baseweb="input"] > div,
            div[data-baseweb="base-input"],
            div[data-testid="stTextInput"] input,
            div[data-testid="stTextInput"] div[data-baseweb="input"],
            div[data-testid="stTextInput"] div[data-baseweb="base-input"],
            input[type="text"],
            input[type="password"],
            input[type="email"],
            input {
                background-color: #ffffff !important;
                background: #ffffff !important;
                color: #0f172a !important;
                border-radius: 14px !important;
                font-size: 0.98rem !important;
            }

            div[data-baseweb="input"] {
                border: 1.5px solid #cbd5e1 !important;
                padding: 4px 14px !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04) !important;
                background-color: #ffffff !important;
            }
            div[data-baseweb="input"]:focus-within {
                border-color: #2563eb !important;
                box-shadow: 0 0 0 3.5px rgba(37, 99, 235, 0.18) !important;
                background-color: #ffffff !important;
            }
            div[data-baseweb="input"] input::placeholder {
                color: #94a3b8 !important;
                opacity: 1 !important;
            }
            div[data-baseweb="input"] svg {
                fill: #64748b !important;
            }

            /* Selectbox */
            div[data-baseweb="select"] {
                background-color: #ffffff !important;
                border: 1.5px solid #cbd5e1 !important;
                border-radius: 14px !important;
            }
            div[data-baseweb="select"] * {
                color: #0f172a !important;
            }

            /* File Uploader */
            div[data-testid="stFileUploader"] {
                background: rgba(239, 246, 255, 0.7) !important;
                backdrop-filter: blur(22px) !important;
                border: 2px dashed #93c5fd !important;
                border-radius: 22px !important;
                padding: 26px !important;
                transition: all 0.25s ease !important;
            }
            div[data-testid="stFileUploader"]:hover {
                border-color: #2563eb !important;
                background: #eff6ff !important;
                box-shadow: 0 10px 30px rgba(37, 99, 235, 0.12) !important;
            }

            /* Progress Bar */
            div[data-testid="stProgress"] > div > div > div > div {
                background: linear-gradient(90deg, #2563eb 0%, #38bdf8 100%) !important;
                box-shadow: 0 0 16px rgba(37, 99, 235, 0.4) !important;
                border-radius: 10px !important;
            }

            /* History Timeline Card */
            .history-card {
                background: rgba(255, 255, 255, 0.96) !important;
                backdrop-filter: blur(18px) !important;
                border-left: 4px solid #2563eb !important;
                border-radius: 16px;
                padding: 18px 22px;
                margin-bottom: 14px;
                transition: all 0.2s ease;
                border-top: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
                box-shadow: 0 8px 20px rgba(37, 99, 235, 0.06) !important;
            }
            .history-card:hover {
                background: #ffffff !important;
                transform: translateX(4px);
                border-top-color: #bfdbfe;
                border-right-color: #bfdbfe;
                border-bottom-color: #bfdbfe;
                box-shadow: 0 12px 28px rgba(37, 99, 235, 0.12) !important;
            }
            /* Visual Interactive Roadmap Design System */
            .roadmap-track {
                position: relative;
                padding: 24px 0 24px 28px;
                margin: 20px 0;
            }
            .roadmap-track::before {
                content: '';
                position: absolute;
                top: 0;
                bottom: 0;
                left: 17px;
                width: 4px;
                background: linear-gradient(180deg, #2563eb 0%, #38bdf8 50%, #818cf8 100%);
                border-radius: 6px;
                box-shadow: 0 0 12px rgba(37, 99, 235, 0.4);
            }
            .roadmap-node {
                position: relative;
                margin-bottom: 26px;
                padding-left: 28px;
            }
            .roadmap-marker {
                position: absolute;
                left: -28px;
                top: 14px;
                width: 36px;
                height: 36px;
                border-radius: 50%;
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                color: #ffffff;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 900;
                font-size: 14px;
                border: 3.5px solid #ffffff;
                box-shadow: 0 4px 16px rgba(37, 99, 235, 0.45);
                z-index: 2;
                transition: transform 0.25s ease, box-shadow 0.25s ease;
            }
            .roadmap-node:hover .roadmap-marker {
                transform: scale(1.15);
                box-shadow: 0 6px 22px rgba(37, 99, 235, 0.6);
            }
            .roadmap-card {
                background: #ffffff;
                border: 1.5px solid #dbeafe;
                border-radius: 20px;
                padding: 24px 28px;
                box-shadow: 0 10px 30px rgba(37, 99, 235, 0.07);
                transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s ease, border-color 0.25s ease;
                position: relative;
                overflow: hidden;
            }
            .roadmap-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 6px;
                height: 100%;
                background: linear-gradient(180deg, #2563eb 0%, #38bdf8 100%);
            }
            .roadmap-card:hover {
                transform: translateY(-3px) translateX(4px);
                border-color: #93c5fd;
                box-shadow: 0 16px 40px rgba(37, 99, 235, 0.14);
            }
            .roadmap-stage-pill {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 4px 12px;
                border-radius: 30px;
                font-size: 11px;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.6px;
            }
            .stage-foundation { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
            .stage-core { background: #f0fdf4; color: #15803d; border: 1px solid #86efac; }
            .stage-mastery { background: #faf5ff; color: #7e22ce; border: 1px solid #d8b4fe; }
            
            .roadmap-progress-bar {
                height: 10px;
                background: #e2e8f0;
                border-radius: 10px;
                overflow: hidden;
                margin: 16px 0 24px 0;
            }
            .roadmap-progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #2563eb 0%, #38bdf8 50%, #22c55e 100%);
                border-radius: 10px;
                transition: width 1s ease-in-out;
            }
        </style>
    """, unsafe_allow_html=True)
