"use strict";

// Prevent dropdown menu from closing when click inside the form
$(document).on("click", ".action-buttons .dropdown-menu", function (e) {
  e.stopPropagation();
});

// Handle checking only through one method per time
$("#text-verification-btn").attr("disabled", true);
$("#url-verification-btn").attr("disabled", true);

$("#title").keyup(function () {
  if ($("#title").val() && $("#maintext").val()) {
    $("#text-verification-btn").attr("disabled", false);
  } else {
    $("#text-verification-btn").attr("disabled", true);
  }
});

$("#maintext").keyup(function () {
  if ($("#maintext").val() && $("#title").val()) {
    $("#text-verification-btn").attr("disabled", false);
  } else {
    $("#text-verification-btn").attr("disabled", true);
  }
});

$("#url").keyup(function () {
  if ($("#url").val()) {
    $("#url-verification-btn").attr("disabled", false);
    $("#text-verification-btn").attr("disabled", true);
  } else {
    $("#url-verification-btn").attr("disabled", true);
  }
});

$("body").on("click", "#pdf", function () {
  html2canvas($("#resultTable")[0], {
    onrendered: function (canvas) {
      var data = canvas.toDataURL();
      var docDefinition = {
        content: [
          {
            image: data,
            width: 500,
          },
        ],
      };
      pdfMake.createPdf(docDefinition).download("nafake_results_table.pdf");
    },
  });
});

$("#closeCard").click(function () {
  $(".result-card").remove();
});

function togglePassword(icon, passField) {
  icon.addEventListener("click", function (e) {
    // toggle the type attribute
    const type =
      passField.getAttribute("type") === "password" ? "text" : "password";
    passField.setAttribute("type", type);
    // toggle the eye slash icon
    this.classList.toggle("fa-eye-slash");
  });
}

const toggleIcon = document.getElementById("toggleIcon");
const password = document.getElementById("password");

const toggleSignPassword1 = document.getElementById("toggleSignPassword1");
const signPassword = document.getElementById("signPassword");

const toggleSignPassword2 = document.getElementById("toggleSignPassword2");
const signConfirmPassword = document.getElementById("signConfirmPassword");

togglePassword(toggleIcon, password);
togglePassword(toggleSignPassword1, signPassword);
togglePassword(toggleSignPassword2, signConfirmPassword);
