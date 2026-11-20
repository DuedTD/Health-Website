const lg = document.getElementById("lg")
const su = document.getElementById("su")

const msu = document.getElementById("msu")
const mlog = document.getElementById("mlog")

const logf = document.getElementById("logform")

lg.addEventListener("click", () => {
    lg.classList.add("chosen")
    mlog.classList.remove("lgfade")

    su.classList.remove("chosen")
    msu.classList.add("lgfade")

    logf.classList.remove("show-su")
});

su.addEventListener("click", () => {
    su.classList.add("chosen")
    msu.classList.remove("lgfade")

    lg.classList.remove("chosen")
    mlog.classList.add("lgfade")
    
    logf.classList.add("show-su")
});

document.querySelectorAll(".toggle-pass").forEach((btn) => {
    btn.addEventListener("click", () => {
        const input = btn.previousElementSibling;
        const isHidden = input.type === "password";
        input.type = isHidden ? "text" : "password";
        btn.textContent = isHidden ? "Hide" : "Show";
    });
});

