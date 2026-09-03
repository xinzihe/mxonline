(function () {
    'use strict';
    var script = document.currentScript;
    var endpoint = script && script.dataset.favoriteUrl;
    var loginUrl = script && script.dataset.loginUrl;
    function cookie(name) { var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)')); return match ? match[2] : ''; }
    document.querySelectorAll('[data-favorite]').forEach(function (button) {
        button.addEventListener('click', function () {
            var body = new URLSearchParams({fav_id: button.dataset.favId, fav_type: button.dataset.favType});
            fetch(endpoint, {method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': cookie('csrftoken')}, body: body.toString()})
                .then(function (response) { return response.json(); })
                .then(function (data) { if (data.status === 'success') { button.textContent = data.msg; } else if (data.msg === '用户未登录') { window.location.href = loginUrl; } else { window.alert(data.msg); } });
        });
    });
}());
