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

function trackDocument(document_id, route_no) {
    $('#track_dts').modal('show');
    $('.modal_body').html(loading);
    $('.modal-title').html("<i class='typcn typcn-chart-line'></i> Track Document");
    $('#route_no_individual').html(route_no)
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

function trackDocumentGlobal() {
    $('#track_dts_global').modal('show');
    $("#track_route_no").val("");
    $('.modal_body').html("");
    $('.modal-title').html("<i class='typcn typcn-chart-line'></i> Track Document");
}

function trackDocumentGlobalConfirm() {
    const route_no = $("#track_route_no").val();
    $('.modal_body').html(loading);
    setTimeout(function() {
        $.ajax({
            url: track_document_url.replace('123', route_no ? route_no : '123'),
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

function deleteDocument(document_id, route_no) {
    $('.modal-title').html("Confirmation?");
    $("#document_id_delete").val(document_id);
    $("#document_route_no").text(route_no);
}

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