$(document).ready(function(){
    $('.sidenav').sidenav();
    $('select').formSelect();
    $("#checklist_form").on("change", "input:checkbox", function(){
      $("#checklist_form").submit();
  });
});

