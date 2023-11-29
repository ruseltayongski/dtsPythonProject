function createDocument() {
    $('.modal_body').html(loading);
    $('.modal-title').html("Create Document");
    setTimeout(function() {
        $.ajax({
            url: create_document_url,
            type: 'GET',
            success: function(result) {
                $('.modal_body').html(result);
            }
        });
    },500);
}

function trackDocument(document_id) {
    $('#track_dts').modal('show');
    $('.modal_body').html(loading);
    $('.modal-title').html("<i class='typcn typcn-chart-line'></i> Track Document");
    setTimeout(function() {
        $.ajax({
            url: track_document_url.replace('123', document_id),
            type: 'GET',
            success: function(result) {
                $('.modal_body').html(result);
            }
        });
    },500);
}

function infoDocument(document_id) {
    $('#info_dts').modal('show');
    $('.modal_body').html(loading);
    $('.modal-title').html("Document Info");
    setTimeout(function() {
        $.ajax({
            url: update_document_url.replace('123', document_id),
            type: 'GET',
            success: function(result) {
                $('.modal_body').html(result);
            }
        });
    },500);
}