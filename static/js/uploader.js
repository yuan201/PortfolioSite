/* Created by YuanYuan on 2016/11/2. */

 $(function () {
     $('#input1').fileinput({
        initialCaption: "Select a file to upload"
     });

     $('#uploader').on('submit', function (event) {
         event.preventDefault();
         window.alert($('#input1').content);
         $('#modalUploader').modal('show');
         // $('tbody', '#modalUploader').append();
     });

     $('#modalClose').click(function (event) {
         $('#modalUploader').modal('hide');
     });


});
