
window.onload = function() {
    var toggle = document.getElementById("theme-toggle");
    toggle.innerText = 'dark';

    toggle.onclick = function() {
        if (toggle.innerText == 'light') {
            document.getElementById("pagetheme").setAttribute('href', "/assets/theme-light.css");
            document.getElementById("codetheme").setAttribute('href', "/assets/code-default.css");
            toggle.innerText = 'dark';
        } else {
            document.getElementById("pagetheme").setAttribute('href', "/assets/theme-dark.css");
            document.getElementById("codetheme").setAttribute('href', "/assets/code-manni.css");
            toggle.innerText = 'light';
        }
    }
}

