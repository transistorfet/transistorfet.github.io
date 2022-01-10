
function setTheme(theme, toggle) {
    if (theme == 'light') {
        document.getElementById("pagetheme").setAttribute('href', "/assets/theme-light.css");
        document.getElementById("codetheme").setAttribute('href', "/assets/code-default.css");
        if (toggle) toggle.innerText = 'dark';
    } else {
        document.getElementById("pagetheme").setAttribute('href', "/assets/theme-dark.css");
        document.getElementById("codetheme").setAttribute('href', "/assets/code-manni.css");
        if (toggle) toggle.innerText = 'light';
    }
}

var theme = window.localStorage.getItem('theme') || 'light';
setTheme(theme);

window.onload = function() {
    var toggle = document.getElementById("theme-toggle");
    setTheme(theme, toggle);

    toggle.onclick = function() {
        theme = (theme == 'light') ? 'dark' : 'light';
        window.localStorage.setItem('theme', theme);
        setTheme(theme, toggle);
    }
}

