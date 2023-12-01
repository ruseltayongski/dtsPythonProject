function acceptDocument(document_id, route_no) {
    $('#accept_dts').modal('show');
    $('.modal-title').html("Accept Documents");
    $("#document_id_accept").val(document_id);
    $("#document_route_no").text(route_no);
}