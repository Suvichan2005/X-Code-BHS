const counters = document.querySelectorAll('.counter');
const speed = 200;

counters.forEach(counter => {
	const updateCount = () => {
		const target = +counter.getAttribute('data-target');
		const count = +counter.innerText;
		const inc = target / speed;
		if (count < target) {
			counter.innerText = count + ~~inc;
			setTimeout(updateCount, 1);
		} else {
			counter.innerText = target;
		}
	};

	updateCount();
});

window.onscroll = function () {
  myFunction();
};

var navbar = document.getElementById("mynavbar");
var sticky = navbar.offsetTop;
function myFunction() {
  if (window.pageYOffset > sticky) {
    navbar.classList.add("sticky");
  } else {
    navbar.classList.remove("sticky")
  }
}


ScrollReveal({
	reset:false,
	distance:'40px',
	duration:2500,
	delay:400

});
ScrollReveal().reveal('.hero-line-1', {delay:300, origin:'left'});
ScrollReveal().reveal('.hero-line-2, .pa',{delay:500, origin:'left'});
ScrollReveal().reveal('.section-2-line-1,.family-value' , {delay:100, origin:'left'});
ScrollReveal().reveal('.butn', {delay:500, origin:'bottom'});
ScrollReveal().reveal('.ba', {delay:200, origin:'right'});
ScrollReveal().reveal('.make-an-style,.app', {delay:100, origin:'right'});
ScrollReveal().reveal('.line-1', {delay:200, origin:'top'});
ScrollReveal().reveal('.main-line', {delay:200, origin:'bottom'});
ScrollReveal().reveal('.na', {delay:200, origin:'bottom'});
ScrollReveal().reveal('.ca', {delay:200, origin:'left'});
