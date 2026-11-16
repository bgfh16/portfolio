import streamlit as st
from utils.styling import get_base64_image
from datetime import datetime
from components.navbar import render_navbar

def show_homepage():
    render_navbar()

    # Convert hero background image to Base64 and inject it as inline CSS

    # f"""...""" — an f-string (formatted string), which lets us insert Python 
    # variables directly into text using {variable_name} syntax. This is how the 
    # actual Base64 data gets inserted into the CSS.

    # {{ and }} — since we're inside an f-string, and CSS itself uses { } for its 
    # rules, we need double curly braces to tell Python "this is a literal curly 
    # brace, not a variable placeholder." Single {hero_image_base64} (one brace) 
    # means "insert the variable here."

    # url('data:image/jpeg;base64,{hero_image_base64}') — this is a data URI,
    # a way of embedding a file's actual content directly into a URL string 
    # instead of pointing to a separate file. data:image/jpeg;base64, tells
    # the browser "what follows is Base64-encoded JPEG image data,"     
    # then our encoded string follows.
    hero_image_base64 = get_base64_image("assets/hero-bg.jpg")
    st.markdown(
        f"""
        <style>
        .hero {{
            background-image: linear-gradient(rgba(6, 78, 59, 0.6), rgba(6, 78, 59, 0.6)), url('data:image/jpeg;base64,{hero_image_base64}');
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero">
            <div class="hero-headline">Smarter Farming Guidance, Built for Nigeria</div>
            <div class="hero-tagline">Get instant, AI-powered advice on crops, pests, and diseases, tailored to your farm and grounded in trusted Nigerian agricultural knowledge.</div>
            <div class="hero-buttons">
                <a href="?page=signup" target="_self" class="btn-primary">Get Started Free</a>
                <a href="#how-it-works-section" target="_self" class="btn-secondary">Learn More</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="how-it-works" id="how-it-works-section">
            <div class="section-heading">How It Works</div>
            <div class="steps-container">
                <div class="step-card">
                    <div class="step-number">1</div>
                    <div class="step-title">Create Account</div>
                    <div class="step-description">Sign up in seconds and set up your profile.</div>
                </div>
                <div class="step-card">
                    <div class="step-number">2</div>
                    <div class="step-title">Describe Problem or Upload Image</div>
                    <div class="step-description">Ask a question in plain language, or upload or take a photo of your crop.</div>
                </div>
                <div class="step-card">
                    <div class="step-number">3</div>
                    <div class="step-title">Get Expert Advice Instantly</div>
                    <div class="step-description">Receive accurate, AI-powered guidance grounded in real agricultural knowledge.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="features-section" id="features-section">
            <div class="section-heading">Features</div>
            <div class="features-grid">
                <div class="feature-card">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="feature-icon">
                        <path d="M6 18h8"/>
                        <path d="M3 22h18"/>
                        <path d="M14 22a7 7 0 1 0 0-14h-1"/>
                        <path d="M9 14h2"/>
                        <path d="M9 12a2 2 0 0 1-2-2V6h6v4a2 2 0 0 1-2 2Z"/>
                        <path d="M12 6V3a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v3"/>
                    </svg>
                    <div class="feature-title">Crop Diagnosis</div>
                    <div class="feature-description">Identify what's affecting your crops with AI-assisted diagnosis.</div>
                </div>
                <div class="feature-card">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="feature-icon">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0ZM18.75 10.5h.008v.008h-.008V10.5Z"/>
                    </svg>
                    <div class="feature-title">Image Analysis</div>
                    <div class="feature-description">Upload a photo and get instant insight into pests, disease, or crop damage.</div>
                </div>
                <div class="feature-card">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="feature-icon">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 12.75c1.148 0 2.278.08 3.383.237 1.037.146 1.866.966 1.866 2.013 0 3.728-2.35 6.75-5.25 6.75S6.75 18.728 6.75 15c0-1.046.83-1.867 1.866-2.013A24.204 24.204 0 0 1 12 12.75Zm0 0c2.883 0 5.647.508 8.207 1.44a23.91 23.91 0 0 1-1.152 6.06M12 12.75c-2.883 0-5.647.508-8.208 1.44.125 2.104.52 4.136 1.153 6.06M12 12.75a2.25 2.25 0 0 0 2.248-2.354M12 12.75a2.25 2.25 0 0 1-2.248-2.354M12 8.25c.995 0 1.971-.08 2.922-.236.403-.066.74-.358.795-.762a3.778 3.778 0 0 0-.399-2.25M12 8.25c-.995 0-1.97-.08-2.922-.236-.402-.066-.74-.358-.795-.762a3.734 3.734 0 0 1 .4-2.253M12 8.25a2.25 2.25 0 0 0-2.248 2.146M12 8.25a2.25 2.25 0 0 1 2.248 2.146M8.683 5a6.032 6.032 0 0 1-1.155-1.002c.07-.63.27-1.222.574-1.747m.581 2.749A3.75 3.75 0 0 1 15.318 5m0 0c.427-.283.815-.62 1.155-.999a4.471 4.471 0 0 0-.575-1.752M4.921 6a24.048 24.048 0 0 0-.392 3.314c1.668.546 3.416.914 5.223 1.082M19.08 6c.205 1.08.337 2.187.392 3.314a23.882 23.882 0 0 1-5.223 1.082"/>
                    </svg>
                    <div class="feature-title">Pest & Disease Guide</div>
                    <div class="feature-description">Browse a searchable library of common pests and diseases.</div>
                </div>
                <div class="feature-card">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="feature-icon">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 0 1 1.037-.443 48.282 48.282 0 0 0 5.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"/>
                    </svg>
                    <div class="feature-title">24/7 AI Assistant</div>
                    <div class="feature-description">Get farming guidance any time, day or night.</div>
                </div>
                <div class="feature-card">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="2 2 20 20" stroke-width="1.25" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="feature-icon">
                        <path d="M7 20h10"/>
                        <path d="M10 20c5.5-2.5.8-6.4 3-10"/>
                        <path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/>
                        <path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>
                    </svg>
                    <div class="feature-title">Crop Recommendations</div>
                    <div class="feature-description">Get suggestions tailored to your crop, location, and season.</div>
                </div>
                <div class="feature-card">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="feature-icon">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
                    </svg>
                    <div class="feature-title">Conversation History</div>
                    <div class="feature-description">Revisit past advice anytime, all saved to your account.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="stats-section">
            <div class="section-heading section-heading-light">Built for Nigerian Farmers</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">22%</div>
                    <div class="stat-label">of Nigeria's GDP comes from agriculture</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">70%</div>
                    <div class="stat-label">of the rural workforce is employed in agriculture</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">80%+</div>
                    <div class="stat-label">of Nigeria's farmers are small-scale</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">90%</div>
                    <div class="stat-label">of agricultural output comes from small-scale farmers</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="trust-section">
            <div class="section-heading">Why AgriAdvisor</div>
            <div class="trust-grid">
                <div class="trust-card">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="#008751" stroke-linecap="round" stroke-linejoin="round" class="trust-icon">
                        <defs>
                            <clipPath id="ng-flag-clip">
                                <path d="M2.5 5.5Q7.25 3.1 12 5.5T21.5 5.5V18.5Q16.75 20.9 12 18.5T2.5 18.5Z"/>
                            </clipPath>
                        </defs>
                        <g clip-path="url(#ng-flag-clip)" stroke="none">
                            <rect x="2.5" y="0" width="6.33" height="24" fill="#008751"/>
                            <rect x="8.83" y="0" width="6.34" height="24" fill="#FFFFFF"/>
                            <rect x="15.17" y="0" width="6.33" height="24" fill="#008751"/>
                        </g>
                        <path d="M2.5 5.5Q7.25 3.1 12 5.5T21.5 5.5V18.5Q16.75 20.9 12 18.5T2.5 18.5Z"/>
                    </svg>
                    <div class="trust-title">Rooted in Nigeria</div>
                    <div class="trust-description">Grounded in agricultural knowledge tailored to Nigerian crops, climates, and farming practices.</div>
                </div>
                <div class="trust-card">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="trust-icon">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5 9 3.75l-1.5 6h6.75l-6 9.75 1.5-6h-6.75Z"/>
                    </svg>
                    <div class="trust-title">Instant Guidance</div>
                    <div class="trust-description">No waiting and no appointments, get answers to your farming questions right away.</div>
                </div>
                <div class="trust-card">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="trust-icon">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z"/>
                    </svg>
                    <div class="trust-title">Private & Secure</div>
                    <div class="trust-description">Your conversations and data stay protected and confidential.</div>
                </div>
                <div class="trust-card">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="trust-icon">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <div class="trust-title">Always Accessible</div>
                    <div class="trust-description">Available anytime, from any device with an internet connection.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="cta-section">
            <div class="section-heading section-heading-light">Ready to Get Started?</div>
            <div class="cta-tagline">Start getting smarter farming guidance today — free, instant, and built for Nigeria.</div>
            <div class="hero-buttons">
                <a href="?page=signup" target="_self" class="btn-primary">Get Started Free</a>
                <a href="#how-it-works-section" target="_self" class="btn-secondary">Learn More</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    current_year = datetime.now().year
    st.markdown(
        f"""
        <div class="footer">
            <div class="footer-top">
                <div class="footer-brand">
                    <div class="footer-logo">🌿 AgriAdvisor</div>
                    <div class="footer-tagline">Smarter farming, powered by AI.</div>
                </div>
                <div class="footer-links">
                    <a href="?page=home" target="_self" class="footer-link">Home</a>
                    <a href="#features-section" target="_self" class="footer-link">Features</a>
                    <a href="#how-it-works-section" target="_self" class="footer-link">How It Works</a>
                    <a href="?page=login" target="_self" class="footer-link">Login</a>
                </div>
                <div class="footer-social">
                    <a href="#" class="footer-icon" aria-label="WhatsApp">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M13.601 2.326A7.85 7.85 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.9 7.9 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.9 7.9 0 0 0 13.6 2.326zM7.994 14.521a6.6 6.6 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.56 6.56 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592m3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.198-.1-.836-.308-1.592-.982-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.198-.232.296-.346.1-.114.132-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34-.114-.007-.247-.007-.38-.007a.73.73 0 0 0-.529.247c-.182.198-.691.677-.691 1.654s.71 1.916.81 2.049c.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.08.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232"/>
                        </svg>
                    </a>
                    <a href="#" class="footer-icon" aria-label="Instagram">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.917 3.917 0 0 0-1.417.923A3.927 3.927 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.7.01 5.555 0 5.827 0 8.001c0 2.172.01 2.444.048 3.297.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923.51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.298-.048c.851-.04 1.434-.174 1.943-.372a3.916 3.916 0 0 0 1.416-.923c.445-.445.718-.891.923-1.417.197-.509.332-1.09.372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.445-.048-3.299c-.04-.851-.175-1.433-.372-1.941a3.926 3.926 0 0 0-.923-1.417A3.911 3.911 0 0 0 13.24.42c-.51-.198-1.092-.333-1.943-.372C10.443.01 10.172 0 7.998 0h.003zm-.717 1.442h.718c2.136 0 2.389.007 3.232.046.78.035 1.204.166 1.486.275.373.145.64.319.92.599.28.28.453.546.598.92.11.281.24.705.275 1.485.039.843.047 1.096.047 3.231s-.008 2.389-.047 3.232c-.035.78-.166 1.203-.275 1.485a2.47 2.47 0 0 1-.599.919c-.28.28-.546.453-.92.598-.28.11-.704.24-1.485.276-.843.038-1.096.047-3.232.047s-2.39-.009-3.233-.047c-.78-.036-1.203-.166-1.485-.276a2.478 2.478 0 0 1-.92-.598 2.48 2.48 0 0 1-.6-.92c-.109-.281-.24-.705-.275-1.485-.038-.843-.046-1.096-.046-3.233 0-2.136.008-2.388.046-3.231.036-.78.166-1.204.276-1.486.145-.373.319-.64.599-.92.28-.28.546-.453.92-.598.282-.11.705-.24 1.485-.276.738-.034 1.024-.044 2.515-.045v.002zm4.988 1.328a.96.96 0 1 0 0 1.92.96.96 0 0 0 0-1.92zm-4.27 1.122a4.109 4.109 0 1 0 0 8.217 4.109 4.109 0 0 0 0-8.217zm0 1.441a2.667 2.667 0 1 1 0 5.334 2.667 2.667 0 0 1 0-5.334z"/>
                        </svg>
                    </a>
                    <a href="#" class="footer-icon" aria-label="X">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M12.6.75h2.454l-5.36 6.142L16 15.25h-4.937l-3.867-5.07-4.425 5.07H.316l5.733-6.57L0 .75h5.063l3.495 4.633L12.601.75Zm-.86 13.028h1.36L4.323 2.145H2.865z"/>
                        </svg>
                    </a>
                    <a href="#" class="footer-icon" aria-label="Facebook">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M16 8.049c0-4.446-3.582-8.05-8-8.05C3.58 0-.002 3.603-.002 8.05c0 4.017 2.926 7.347 6.75 7.951v-5.625h-2.03V8.05H6.75V6.275c0-2.017 1.195-3.131 3.022-3.131.876 0 1.791.157 1.791.157v1.98h-1.009c-.993 0-1.303.621-1.303 1.258v1.51h2.218l-.354 2.326H9.25V16c3.824-.604 6.75-3.934 6.75-7.951"/>
                        </svg>
                    </a>
                </div>
            </div>
            <div class="footer-bottom">
                © {current_year} AgriAdvisor. All rights reserved.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
