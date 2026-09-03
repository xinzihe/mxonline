(function () {
    'use strict';

    var searchForm = document.querySelector('[data-search-form]');
    if (searchForm) {
        var destinations = {
            course: '/course/list/',
            org: '/org/list/',
            teacher: '/org/teacher/list/'
        };
        searchForm.addEventListener('submit', function () {
            var type = searchForm.querySelector('[name="type"]').value;
            searchForm.action = destinations[type] || destinations.course;
        });
    }
}());
