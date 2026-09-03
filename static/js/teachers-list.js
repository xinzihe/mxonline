$(function() {
    console.log("授课讲师列表页 JS 资源已成功加载。");

    // 预留：讲师关注/收藏交互逻辑
    $('.btn-teacher-fav').on('click', function(e) {
        e.preventDefault();
        var $btn = $(this);
        if ($btn.hasClass('faved')) {
            $btn.removeClass('faved').text('❤️ 关注讲师');
        } else {
            $btn.addClass('faved').text('❤️ 已关注');
        }
    });
});