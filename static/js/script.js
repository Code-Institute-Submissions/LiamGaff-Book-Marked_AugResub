$(document).ready(function(){
    $('.sidenav').sidenav();
  });


// Handling form submission and run fuction on submit
// $("form[name=signup_form").submit(function(e) {

//     var $form = $(this);
//     var $error = $form.find(".error");
//     var data = $form.serialize();
  
//     $.ajax({
//       url: "/signup",
//       type: "POST",
//       data: data,
//       dataType: "json",
//       success: function(resp) {
//         window.location.href = "/profile/";
//       },
//       error: function(resp) {
//         $error.text(resp.responseJSON.error).removeClass("error--hidden");
//       }
//     });
  
//     e.preventDefault();
//   });


//   // Handle login on submission
//   $("form[name=login_form").submit(function(e) {

//     var $form = $(this);
//     var $error = $form.find(".error");
//     var data = $form.serialize();
  
//     $.ajax({
//       url: "/login",
//       type: "POST",
//       data: data,
//       dataType: "json",
//       success: function(resp) {
//         window.location.href = "/signup/";
//       },
//       error: function(resp) {
//         $error.text(resp.responseJSON.error).removeClass("error--hidden");
//       }
//     });
  
//     e.preventDefault();
//   });
