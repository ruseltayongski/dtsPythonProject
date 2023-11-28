console.log("DOCUMENTS JS");
function createPatient() {
    $('.modal_body').html(loading);
    $('.modal-title').html("Create Document");
    /*var url = "{{ route('patient.create') }}";
    setTimeout(function(){
        $.ajax({
            url: url,
            type: 'GET',
            success: function(result) {
                $('.modal_body').html(result);
            }
        });
    },500);*/
}