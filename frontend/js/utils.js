function formatDate(iso) {
    if (!iso) return "—";
    const [y, m, d] = iso.split("-");
    const months = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"];
    return `${parseInt(d)} ${months[parseInt(m)-1]} ${y}`;
}

function showAlert(containerId, message, type = "error") {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    if (type === "success") setTimeout(() => { el.innerHTML = ""; }, 4000);
}

// SVG icons (inline, no emoji)
const ICONS = {
    plane:   `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5"/></svg>`,
    user:    `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"/></svg>`,
    settings:`<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/></svg>`,
    edit:    `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125"/></svg>`,
    trash:   `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"/></svg>`,
    plus:    `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/></svg>`,
    globe:   `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253M3 12a8.959 8.959 0 0 0 .284 2.253"/></svg>`,
};

function icon(name, size = 16) {
    return `<span style="display:inline-flex;width:${size}px;height:${size}px;">${ICONS[name] || ""}</span>`;
}

function renderNavbar(user) {
    const nav = document.getElementById("navbar");
    if (!nav || !user) return;
    const current = window.location.pathname;
    const adminLink = user.is_admin ? `<a href="/pages/admin.html" class="nav-link ${current.includes('admin') ? 'active' : ''}">Admin</a>` : "";
    nav.innerHTML = `
        <div class="navbar-inner">
            <a href="/pages/trips.html" class="navbar-brand">Loving<span>App</span></a>
            <div class="navbar-links">
                <a href="/pages/trips.html" class="nav-link ${current.includes('trips') ? 'active' : ''}">Viajes</a>
                <a href="/pages/profile.html" class="nav-link ${current.includes('profile') ? 'active' : ''}">Perfil</a>
                ${adminLink}
                <div class="nav-divider"></div>
                <button class="btn-nav-logout" id="btn-logout">Salir</button>
            </div>
            <button class="nav-hamburger" id="btn-hamburger" aria-label="Menu" aria-expanded="false">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"/></svg>
            </button>
        </div>
    `;

    // Mobile menu must live outside <nav> — backdrop-filter on nav creates a new
    // containing block for fixed descendants, which clips the overlay to 56px.
    let mobileMenu = document.getElementById("navbar-mobile-menu");
    if (!mobileMenu) {
        mobileMenu = document.createElement("div");
        mobileMenu.id = "navbar-mobile-menu";
        mobileMenu.className = "navbar-mobile-menu";
        document.body.appendChild(mobileMenu);
    }
    mobileMenu.setAttribute("aria-hidden", "true");
    mobileMenu.innerHTML = `
        <a href="/pages/trips.html" class="nav-link ${current.includes('trips') ? 'active' : ''}">Viajes</a>
        <a href="/pages/profile.html" class="nav-link ${current.includes('profile') ? 'active' : ''}">Perfil</a>
        ${adminLink}
        <div class="nav-divider"></div>
        <button class="btn-nav-logout" id="btn-logout-mobile">Salir</button>
    `;

    const logout = async () => {
        await api.logout();
        window.location.href = "/pages/login.html";
    };
    document.getElementById("btn-logout").addEventListener("click", logout);
    document.getElementById("btn-logout-mobile").addEventListener("click", logout);

    const hamburger = document.getElementById("btn-hamburger");
    hamburger.addEventListener("click", () => {
        const open = mobileMenu.classList.toggle("open");
        hamburger.setAttribute("aria-expanded", open);
        mobileMenu.setAttribute("aria-hidden", !open);
    });
    mobileMenu.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", () => {
            mobileMenu.classList.remove("open");
            hamburger.setAttribute("aria-expanded", "false");
            mobileMenu.setAttribute("aria-hidden", "true");
        });
    });
}

async function requireAuth() {
    try {
        const user = await api.getProfile();
        renderNavbar(user);
        return user;
    } catch {
        window.location.href = "/pages/login.html";
        return null;
    }
}

function initials(name) {
    if (!name) return "?";
    return name.split(" ").map(w => w[0]).slice(0, 2).join("").toUpperCase();
}

function confirmModal(message) {
    return new Promise((resolve) => {
        const existing = document.getElementById("confirm-overlay");
        if (existing) existing.remove();

        const overlay = document.createElement("div");
        overlay.id = "confirm-overlay";
        overlay.innerHTML = `
            <div class="confirm-box">
                <div class="confirm-icon">💔</div>
                <p class="confirm-msg">${message}</p>
                <div class="confirm-actions">
                    <button class="btn btn-ghost" id="confirm-cancel">Cancelar</button>
                    <button class="btn btn-primary" id="confirm-ok">Eliminar</button>
                </div>
            </div>`;

        Object.assign(overlay.style, {
            position: "fixed", inset: "0", zIndex: "9999",
            display: "flex", alignItems: "center", justifyContent: "center",
            background: "rgba(0,0,0,.45)", backdropFilter: "blur(3px)",
            animation: "fadeIn .2s ease",
        });

        const box = overlay.querySelector(".confirm-box");
        Object.assign(box.style, {
            background: "#fff", borderRadius: "16px", padding: "2rem",
            maxWidth: "360px", width: "90%", textAlign: "center",
            boxShadow: "0 20px 60px rgba(0,0,0,.2)",
            animation: "scaleIn .2s ease",
        });

        const icon = overlay.querySelector(".confirm-icon");
        icon.style.cssText = "font-size:2.5rem;margin-bottom:.75rem;";

        const msg = overlay.querySelector(".confirm-msg");
        Object.assign(msg.style, {
            fontSize: ".95rem", color: "#555", lineHeight: "1.5",
            margin: "0 0 1.5rem",
        });

        const actions = overlay.querySelector(".confirm-actions");
        actions.style.cssText = "display:flex;gap:.75rem;justify-content:center;";

        const cancelBtn = overlay.querySelector("#confirm-cancel");
        const okBtn = overlay.querySelector("#confirm-ok");
        okBtn.style.cssText = "background:var(--rose);color:#fff;border:none;padding:.6rem 1.5rem;border-radius:10px;font-weight:600;cursor:pointer;";
        okBtn.onmouseover = () => okBtn.style.background = "var(--rose-d)";
        okBtn.onmouseout = () => okBtn.style.background = "var(--rose)";

        function close(result) {
            overlay.style.animation = "fadeIn .15s ease reverse";
            box.style.animation = "scaleIn .15s ease reverse";
            setTimeout(() => { overlay.remove(); resolve(result); }, 120);
        }

        cancelBtn.onclick = () => close(false);
        okBtn.onclick = () => close(true);
        overlay.onclick = (e) => { if (e.target === overlay) close(false); };
        document.addEventListener("keydown", function handler(e) {
            if (e.key === "Escape") { close(false); document.removeEventListener("keydown", handler); }
        });

        document.body.appendChild(overlay);
    });
}
