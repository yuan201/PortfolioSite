/* Created by YuanYuan on 2016/11/2. */

 $(function () {
     $('#input1').fileinput({
        initialCaption: "Select a file to upload"
     });

     $('#input1').on('change', function (event) {
         event.preventDefault();
         $('#modalUploader').modal('show');
         // verify the content of the file
     });

     $('#modalClose').click(function (event) {
         $('#modalUploader').modal('hide');
     });

     // remove dividend(8) and ratio(9) from buy/sell transactions
     for(var i=8; i<= 9; i++){
         $('tr.buy td:eq('+i+')', '#transaction_table').text('');
         $('tr.sell td:eq('+i+')', '#transaction_table').text('');
     }
     // remove shares, price, fee and cashflow(4-7) from dividend/split transactions
     for(var i=4; i<=7; i++) {
         $('tr.div td:eq('+i+')', '#transaction_table').text('');
         $('tr.split td:eq('+i+')', '#transaction_table').text('');
     }

 });
