function releaseDocument(document_id) {
    $('#release_dts').modal('show');
    $('.modal_body').html(loading);
    $('.modal-title').html("<i class='typcn typcn-arrow-forward-outline'></i> Release Document");
    setTimeout(function() {
        $.ajax({
            url: release_document_url.replace('123', document_id),
            type: 'GET',
            success: function(result) {
                $('.modal_body').html(result);
                $('#release_document_id').val(document_id)
            }
        });
    },500);
}

function cycleEndDocument(document_id) {
    $('#cycle_end_dts').modal('show');
    $('.modal-title').html("<i class='typcn typcn-info'></i> Confirmation");
    $("#document_id_end_cycle").val(document_id);
}