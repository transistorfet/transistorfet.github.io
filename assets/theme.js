
function setTheme(toggle, theme) {
    if (theme == 'light') {
        document.getElementById("pagetheme").setAttribute('href', "/assets/theme-light.css");
        document.getElementById("codetheme").setAttribute('href', "/assets/code-default.css");
        toggle.innerText = 'dark';
    } else {
        document.getElementById("pagetheme").setAttribute('href', "/assets/theme-dark.css");
        document.getElementById("codetheme").setAttribute('href', "/assets/code-manni.css");
        toggle.innerText = 'light';
    }
}

window.onload = function() {
    var theme = window.localStorage.getItem('theme') || 'light';
    var toggle = document.getElementById("theme-toggle");
    setTheme(toggle, theme);

    toggle.onclick = function() {
        theme = (theme == 'light') ? 'dark' : 'light';
        window.localStorage.setItem('theme', theme);
        setTheme(toggle, theme);
    }
}

