(function () {
    'use strict';
    var script = document.currentScript;
    var endpoint = script && script.dataset.favoriteUrl;
    var loginUrl = script && script.dataset.loginUrl;
    var followLabels = {'1': '关注课程', '2': '关注机构', '3': '关注讲师'};
    function cookie(name) { var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)')); return match ? match[2] : ''; }
    document.querySelectorAll('[data-favorite]').forEach(function (button) {
        button.addEventListener('click', function () {
            if (button.disabled) return;
            button.disabled = true;
            var body = new URLSearchParams({fav_id: button.dataset.favId, fav_type: button.dataset.favType});
            fetch(endpoint, {method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': cookie('csrftoken')}, body: body.toString()})
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    if (data.status === 'success') {
                        button.textContent = data.label || (data.action === 'followed' ? '取消关注' : followLabels[button.dataset.favType]);
                        button.classList.toggle('is-following', data.action === 'followed');
                        if (data.action === 'unfollowed' && button.closest('[data-favorite-list]')) {
                            window.location.reload();
                            return;
                        }
                    } else if (data.msg === '用户未登录') {
                        window.location.href = loginUrl;
                    } else {
                        window.alert(data.msg);
                    }
                    button.disabled = false;
                })
                .catch(function () {
                    button.disabled = false;
                    window.alert('操作失败，请稍后重试。');
                });
        });
    });
}());
