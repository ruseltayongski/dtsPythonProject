console.log("DOCUMENTS JS!");
function createPatient() {
    $('.modal_body').html(loading);
    $('.modal-title').html("Create Document");
    setTimeout(function(){
        $.ajax({
            url: create_document_url,
            type: 'GET',
            success: function(result) {
                $('.modal_body').html(result);
            }
        });
    },500);
}