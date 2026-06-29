/*
=========================================
Wine Quality Predictor
script.js
=========================================
*/

document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("predictionForm");
    const button = document.getElementById("predictBtn");

    if (form && button) {

        form.addEventListener("submit", function () {

            button.disabled = true;

            button.classList.add("loading");

            button.innerHTML = "Predicting...";

        });

    }

    /* =========================================
       Fade Animation
    ========================================= */

    const observer = new IntersectionObserver(

        entries => {

            entries.forEach(entry => {

                if (entry.isIntersecting) {

                    entry.target.classList.add("show");

                }

            });

        },

        {

            threshold:0.15

        }

    );

    document.querySelectorAll(".hero,.form-card,.result-card").forEach(el=>{

        el.classList.add("hidden");

        observer.observe(el);

    });

});