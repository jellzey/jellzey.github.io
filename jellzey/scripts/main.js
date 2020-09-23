var myImage = document.querySelector('img');

myImage.onclick = function() {
    var mySrc = myImage.getAttribute('src');
    if(mySrc === 'images/jeff.jpg') {
      myImage.setAttribute ('src','images/jeff2.jpg');
    } else {
      myImage.setAttribute ('src','images/jeff.jpg');
    }
}

var heading = document.querySelector('h2');

heading.onclick = function() {
    alert('What is good huge pimp')
}


var myButton = document.querySelector('button');
var myHeading = document.querySelector('h1');

function setUserName() {
  var myName = prompt('Please enter your name.');
  localStorage.setItem('name', myName);
  myHeading.textContent = 'Whattap, ' + myName +'pimp';
}
if(!localStorage.getItem('name')) {
  setUserName();
} else {
  var storedName = localStorage.getItem('name');
  myHeading.textContent = 'Whattap, ' + storedName +'pimp';
}
myButton.onclick = function() {
  setUserName();
}