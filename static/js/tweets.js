$(document).ready(function () {
    $("#spin").spinner();
    $("#topic_dropdown").on('click', 'li a', function () {
        var selText = $(this).children("h4").html();
        $(this).parent('li').siblings().removeClass('active');
        $(this).parents('.btn-group').find('.selection').html(selText);
        $(this).parents('li').addClass("active");
        $("#spin").show();
        var topic_id = $(this).attr("data-id");
        $.ajax({
            url: '/Tweets',
            method: 'GET',
            data: {
                'topic_id': topic_id
            },
            timeout: 10000,
            success: function (html) {
                $('#tweetscontainer').empty();
                $('#tweetscontainer').append(html);
                $("#spin").hide();
            }
        });
    });
});

function saveTweet(tweet_id) {
    var text = $('#tweet_'.concat(tweet_id)).find("#description").text();
    if (text.length >= 256) {
        var excess = text.length - 256;
        var message = "Your tweet body is too long. Please, remove {0} characters.".format(excess);
        swal("Tweet Length!", message, "error");
    } else {
        var date = $('#tweet_'.concat(tweet_id)).find("#date").val();
        var title = $('#tweet_'.concat(tweet_id)).find("#title").text();
        var tweet_link_description = $('#tweet_'.concat(tweet_id)).find("#tweet_link_description").text();
        var bg_url = $('#tweet_'.concat(tweet_id)).find("#image").css('background-image');
        bg_url = /^url\((['"]?)(.*)\1\)$/.exec(bg_url);
        bg_url = bg_url ? bg_url[2] : "";
        var items = getParameters();
        var news_id = -1;
        if (Object.keys(items).length > 0 && items.news_id) {
            news_id = items.news_id;
        }
        $('#tweet_'.concat(tweet_id)).find('.btn-save').attr("disabled", true);
        $.ajax({
            url: "/Tweets",
            method: 'POST',
            data: {
                'tweet_id': tweet_id,
                'posttype': 'update',
                'text': text,
                'date': date,
                'news_id': news_id,
                'title': title,
                'tweet_link_description': tweet_link_description,
                'image_url': bg_url
            }
        }).success(function (response) {
            swal({
                    title: "Good job!",
                    text: "Your tweet is saved!",
                    type: "success",
                    showCancelButton: false,
                    confirmButtonClass: "btn-success",
                    confirmButtonText: "Ok!",
                    closeOnConfirm: true,
                    closeOnCancel: false
                },
                function () {
                    if (Object.keys(items).length > 0 && items.news_id) {
                        window.location.replace("/Tweets");
                    }
                });
        });
    }
}

function removeTweet(tweet_id) {
    swal({
            title: "Are you sure?",
            text: "Your will not be able to recover this tweet!",
            type: "warning",
            showCancelButton: true,
            confirmButtonClass: "btn-danger",
            confirmButtonText: "Yes, delete it!",
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        },
        function () {
            $.ajax({
                url: "/Tweets",
                method: 'POST',
                data: {
                    'tweet_id': tweet_id,
                    'posttype': 'remove'
                }
            }).success(function (response) {
                swal("Deleted!", "Your tweet has been deleted.", "success");
                $('#tweet_'.concat(tweet_id)).remove();
            });
        });
}


function getTweets() {
    $("#spin").show();
    var status = $('.btn-success').val();
    var topic_id = $("#topic_dropdown > .active > a").attr("data-id");
    $.ajax({
        type: "GET",
        url: "/Tweets",
        data: {
            'topic_id': topic_id,
            'status': status,
            'request_type': "ajax"
        },
        success: function (html) {
            $('#tweetscontainer').empty();
            $('#tweetscontainer').append(html);
            $("#spin").hide();
        }
    });
}


function changeFilter(clickedFilter) {
    $('.btn-success').removeClass('btn-success').addClass('btn-default');
    $(clickedFilter).removeClass('btn-default').addClass('btn-success');
    getTweets();
}
