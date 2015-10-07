/**
 * Created by Michael on 9/21/15.
 */
// Gets child categories and inserts a new subcategory selector into the form.
function child_categories(id, last){

    $.getJSON({
        url : '/form_categories',
        method : 'GET',
        data : {"category": id}
    })
        .done(function (json){
            var length = json.items["length"];
            if (length > 0) {
                // inserts the selector into the "nested" div
                $('#' + last + "nest").html(
                    "<label for='select' class='col-lg-2 control-label'>"
                    + "sub".repeat(last)+"category</label>\
                <div class='col-lg-10'>\
                    <select class='form-control' id='" + id
                    + "list' class='selects'>\
                    </select>\
                    <br>\
                </div>"
                );
                $('#' + id + 'list').append(
                    "<option>--Choose Subcategory</option>"
                );
                $.each(json.items, function (idx, category){
                    $('#'+id+'list').append(
                        "<option class='"+id+"' " +
                        "id='"+category[1]+"'>"+category[0]+"</option>")
                });
                $('#'+last+"nest").append("<div style='margin-left: "
                    + (10*last)+" !important;' id='"
                    + (last+1) + "nest'></div>");
                $('#'+last+"nest").show();
                $('#'+last+"nest").css(
                    'margin-left',
                    10*last+"px !important"
                );
                $('#'+(last+1)+"nest").hide();

                // update value of hidden form field to track browse_node_id
                $('#'+id+'list').on("change",function(){
                    $("#hidden").val(
                        $("#"+id+"list option:selected").attr('id')
                    );
                   child_categories(
                       $( "#" + id + "list " + "option:selected").attr('id'),
                       last+1
                   );
                })}
        });
}

$(document).ready(function (){
    $('#1nest').hide();
    $.getJSON({
        url : '/form_categories',
        method : 'GET'
    })
        .done(function (json){
            $.each(json.items, function (idx, category){
                $('#select').append(
                    "<option class='form-category' id='" + category[1] + "'>"
                + category[0] + "</option>")
            })
        });
    $('#select').on("change",function(){
        // changes value of hidden form field to keep track of selected
        // category.
        $("#hidden").val($( "select option:selected").attr('id'));
        child_categories($( "select option:selected").attr('id'), 1);
    })

});