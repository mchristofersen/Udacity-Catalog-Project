
// Function for rotating icons
$.fn.animateRotate = function(startAngle,
                              endAngle,
                              duration,
                              easing,
                              complete){
    return this.each(function(){
        var elem = $(this);

        $({deg: startAngle}).animate({deg: endAngle}, {
            duration: duration,
            easing: easing,
            step: function(now){
                elem.css({
                  '-moz-transform':'rotate('+now+'deg)',
                  '-webkit-transform':'rotate('+now+'deg)',
                  '-o-transform':'rotate('+now+'deg)',
                  '-ms-transform':'rotate('+now+'deg)',
                  'transform':'rotate('+now+'deg)'
                });
            },
            complete: complete || $.noop
        });
    });
};

function toggle_category(category){
    event.stopPropagation();
    // check current state and toggle subcategory list visibility and animation
    if ($("#"+category+"caret").attr('style') == 'transform: rotate(90deg);'){
       $("#"+category+"caret").animateRotate(90, 0, 300,'swing',function (){
           $('div#'+category+'.category-list').toggle('slide',{
               direction: 'up'
           });
       } );
    }else {
        $("#"+category+"caret").animateRotate(0, 90, 300,'swing',function (){
           $('div#'+category+'.category-list').toggle('slide',{
               direction: 'up'
           });
       } );    }
}

// When parent category is clicked, query database for subcategories of
// parent category.
function get_children(category){
    $("#"+category+"caret").animateRotate(0,90);
    $.ajax({
        method: 'GET',
        url: "/category",
        data: {"category": category}
    })
        .done(function results(res) {
            $('#'+category).hide().html(res).show('slide',{
               direction: 'up'
           });
            $('#'+category+'button').attr('onclick','javascript:void(0)');
            $('#'+category+'button').click(function (){
                toggle_category(category);
            });
            $('html, body').animate(
                { scrollTop: $('#'+category+'button').offset().top -20 }
                , 'slow');
            }
            )
}


function scroll_to(px){
    $('html, body').animate({ scrollTop: px }, 'slow');
}




