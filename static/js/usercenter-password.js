(function () {
    'use strict';
    var page = document.querySelector('[data-profile-page]');
    var form = document.querySelector('#profile-password-form');
    if (!page || !form) return;
    var dialog = form.closest('dialog');
    var script = document.currentScript;
    var loginUrl = script && script.dataset.loginUrl;

    function csrf() {
        var match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }
    function show(text) { form.querySelector('[data-password-message]').textContent = text || ''; }
    function resetForm() {
        form.reset();
        show('');
    }
    function errors(data) {
        return Object.keys(data).map(function (key) {
            return Array.isArray(data[key]) ? data[key].join(' ') : data[key];
        }).join(' ');
    }

    // 每次打开和关闭都清理敏感密码字段，避免浏览器保留上次输入内容。
    document.querySelectorAll('[data-open-dialog="password"]').forEach(function (button) {
        button.addEventListener('click', resetForm);
    });
    dialog.addEventListener('close', resetForm);

    // 捕获阶段拦截旧脚本，向用户展示明确校验信息。
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        event.stopImmediatePropagation();
        var password1 = form.elements.password1.value;
        var password2 = form.elements.password2.value;
        if (password1.length < 6 || password1.length > 20) {
            show('密码长度必须为 6-20 位字符。');
            return;
        }
        if (password1 !== password2) {
            show('两次输入的密码不一致。');
            return;
        }
        fetch(page.dataset.passwordUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrf()},
            body: new URLSearchParams({password1: password1, password2: password2})
        }).then(function (response) { return response.json(); }).then(function (data) {
            if (data.status === 'success') {
                show('密码已修改，正在跳转到登录页…');
                setTimeout(function () { window.location.href = loginUrl || '/login/'; }, 700);
            } else {
                show(data.msg || errors(data) || '密码修改失败。');
            }
        }).catch(function () { show('请求失败，请稍后重试。'); });
    }, true);
}());
