$(function () {

    function widget_control(event){
        sel = $('#id_type option:selected').text();
        if(sel == 'Buy' || sel == 'Sell') {
            $('#id_dividend').closest('.form-group').hide();
            $('#id_ratio').closest('.form-group').hide();
            $('#id_price').closest('.form-group').show();
            $('#id_shares').closest('.form-group').show();
            $('#id_fee').closest('.form-group').show();
        }
        if(sel == 'Dividend' || sel == 'Ratio') {
            $('#id_price').closest('.form-group').hide();
            $('#id_shares').closest('.form-group').hide();
            $('#id_fee').closest('.form-group').hide();
        }
        if(sel == 'Dividend') {
            $('#id_dividend').closest('.form-group').show();
            $('#id_ratio').closest('.form-group').hide();
        }
        if(sel == 'Split') {
            $('#id_ratio').closest('.form-group').show();
            $('#id_dividend').closest('.form-group').hide();
        }
    }
    widget_control();
    $('#id_type').on('change', widget_control)
});