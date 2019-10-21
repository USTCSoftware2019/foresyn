// function getCookie(name) {
//     var cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         var cookies = document.cookie.split(';');
//         for (var i = 0; i < cookies.length; i++) {
//             var cookie = jQuery.trim(cookies[i]);
//             // Does this cookie string begin with the name we want?
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }
//
// var csrftoken = getCookie('csrftoken');
// $.ajaxSetup({
//     beforeSend: function(xhr) {
// 	xhr.setRequestHeader("X-CSRFToken", csrftoken);
//     }
// });

$('.favorite').click(function() {
    var $obj = $(this);
    var target_id = $obj.attr('id').split('_')[1];
    $obj.prop('disabled', true);
    $.ajax({
        url: $obj.attr('href'),
        type: 'POST',
        data: {
            target_app: $obj.attr('app'),
            target_name: $obj.attr('model_name'),
            target_object_id: target_id
        },
        success: function(response) {
                if (response.status === 'added') {
                    $obj.removeClass('fa-star-o').addClass('fa-star');
                }
                else {
                    $obj.removeClass('fa-star').addClass('fa-star-o');
                }
                // $obj.parent('.favorite').children('.fav-count').text(response.fav_count);
                $obj.prop('disabled', false);
        }
    });
});
