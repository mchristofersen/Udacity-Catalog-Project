/**
 * Created by Michael on 9/22/15.
 */
function show_review(name){
    $("."+name).hide();
    var top = $(window).scrollTop();
    $(document).on("scroll", function (){
        if ($(window).scrollTop() - top > 100 ||
            $(window).scrollTop() - top < -50 ){
            hide_review(name);
        }
    })
    var height = $(window).height();
    var width = $(window).width();
    $(".carousel"+name).css('top',top);
    $(".carousel"+name).css('height',height+"px");
    $(".carousel"+name).css('width',width+"px");
    $(".carousel"+name).carousel(0);
    //$("#"+name+" .item").click(function(){
    //    $(".carousel"+name).carousel(1);
    //});
    $("#"+name+" .left").click(function(){
        event.stopPropagation();
        $("#"+name).carousel("prev");
    });
    $("#"+name+" .right").click(function(){
        event.stopPropagation();
        $("#"+name).carousel("next");
    });
    $('.carousel'+name).show();
}

function hide_review(name){
    $("."+name).show();
    $(".carousel"+name).hide("fade",{duration: 500});
}

function delete_item(asin){
    $.ajax({
        url: '/delete_item',
        method: 'POST',
        data: {'asin':asin}
    })
        .done(function(response){
            if (response.response == 'True'){
               alert('Item Deleted' );
              location.reload();
            } else {
                alert('Error: Item not deleted!')
            }
        } )
}

$(document).ready(function(){
    $('.carousel').carousel();
    var height = $(window).height();
    $(".carousel-inner").css('height',(height/2)+"px !important;");
    $(".carousel-image").height((height/2));
    var $reviews = $('.description');
    $.each($reviews, function(idx, item){
        var xml = $(item).text();
        $(item).html(xml);
    })
});