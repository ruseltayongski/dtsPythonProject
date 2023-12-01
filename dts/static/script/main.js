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