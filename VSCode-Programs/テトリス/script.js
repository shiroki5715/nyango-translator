document.addEventListener('DOMContentLoaded', function() {
  // スライダー処理
  const slides = document.querySelectorAll('.slide');
  let currentSlide = 0;
  let slideInterval = setInterval(nextSlide, 5000);
  
  const nextButton = document.querySelector('.next');
  const prevButton = document.querySelector('.prev');
  
  nextButton.addEventListener('click', function(){
    nextSlide();
    resetInterval();
  });
  
  prevButton.addEventListener('click', function(){
    prevSlide();
    resetInterval();
  });
  
  function nextSlide(){
    slides[currentSlide].classList.remove('active');
    currentSlide = (currentSlide + 1) % slides.length;
    slides[currentSlide].classList.add('active');
  }
  
  function prevSlide(){
    slides[currentSlide].classList.remove('active');
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    slides[currentSlide].classList.add('active');
  }
  
  function resetInterval(){
    clearInterval(slideInterval);
    slideInterval = setInterval(nextSlide, 5000);
  }
  
  // お問い合わせフォームの処理
  const form = document.getElementById('contact-form');
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    alert('お問い合わせありがとうございます！');
    form.reset();
  });
});
