$(document).ready(function() {
    $('#search-form').on('submit', function(event) {
        event.preventDefault();
        performSearch();
    });

    $('#search-button').on('click', function(event) {
        event.preventDefault();
        performSearch();
    });

    function performSearch() {
        var query = $('#search-input').val();

        $.ajax({
            url: '/search',
            method: 'GET',
            data: { query: query },
            success: function(response) {
                window.location.href = '/search?query=' + encodeURIComponent(query);
            },
            error: function(error) {
                console.log(error);
            }
        });
    }
});
