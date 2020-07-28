"use strict";

// $(document).ready(function () {
//   //------- Mailchimp js --------//
//   function mailChimp() {
//     $("#mc_embed_signup").find("form").ajaxChimp();
//   }
//   mailChimp();
// });

// /*  ==========================================
//     SHOW UPLOADED IMAGE
// * ========================================== */
// function readURL(input) {
//   if (input.files && input.files[0]) {
//     let reader = new FileReader();

//     reader.onload = function (e) {
//       $("#imageResult").attr("src", e.target.result);
//     };
//     reader.readAsDataURL(input.files[0]);
//   }
// }

// $(function () {
//   $("#upload").on("change", function () {
//     readURL($("#upload"));
//   });
// });

// /*  ==========================================
//   SHOW UPLOADED IMAGE NAME
// * ========================================== */
// let input = document.getElementById("upload");
// let infoArea = document.getElementById("upload-label");
// let imageResult = document.getElementById("imageResult");

// input.addEventListener("change", showFileName);

// function showFileName(event) {
//   let input = event.srcElement;
//   let fileName = input.files[0].name;
//   infoArea.textContent = "File name: " + fileName;
//   imageResult.classList.replace("d-none", "d-block");
// }

// Prevent dropdown menu from closing when click inside the form
$(document).on("click", ".action-buttons .dropdown-menu", function (e) {
  e.stopPropagation();
});