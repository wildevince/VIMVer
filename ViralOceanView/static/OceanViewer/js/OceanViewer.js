function getAll_td_byPosition(position) {
	var res = [];
	var All = document.getElementsByTagName('td');
	Array.from(All).forEach(cell => {
		if (cell.getAttribute('data-position') == position) {
			 res.push(cell)
		}
	});
	return res;
}


$(document).ready(function() {

	var all_td = document.getElementsByTagName('td');

	Array.from(all_td).forEach(cell => {
		var position = cell.getAttribute('data-position');

		cell.addEventListener("mouseover", function(event) {
			event.target.setAttribute('hover', 'true')
			let samePositionnedCell = getAll_td_byPosition(position);
			samePositionnedCell.forEach(residu => {
				residu.setAttribute('hover', 'true');
			});
		});

		cell.addEventListener("mouseout", function(event) {
			event.target.setAttribute('hover', 'true')
			let samePositionnedCell = getAll_td_byPosition(position);
			samePositionnedCell.forEach(residu => {
				residu.removeAttribute('hover', 'false');
			});
		});

	});
	
	$("#infobox-help").click(function() {
		$(".infoPanel").Attr("hidden");
		$("#infoPanel-help").removeAttr("hidden");
	});
	$("#infobox-project").click(function() {
		$(".infoPanel").Attr("hidden");
		$("#infoPanel-project").removeAttr("hidden");
	});
	$("#infobox-contact").click(function() {
		$(".infoPanel").Attr("hidden");
		$("#infoPanel-contact").removeAttr("hidden");
	});



	//// Help from chatGPT 
	// Check if the cookie has already been accepted
	var cookieAccepted = getCookie("cookie-accepted");
	if (cookieAccepted) {
	  $("#cookie-banner").hide();
	} else {
	  $("#cookie-accept").on("click", acceptCookie);
	}
	

})



//// Help from chatGPT 
// Function to set a cookie with a given name, value, and expiration days
function setCookie(name, value, days) {
	var expires = "";
	if (days) {
	  var date = new Date();
	  date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
	  expires = "; expires=" + date.toUTCString();
	}
	document.cookie = name + "=" + (value || "") + expires + "; path=/";
  }
  
  // Function to check if a cookie with a given name exists
  function getCookie(name) {
	var nameEQ = name + "=";
	var cookies = document.cookie.split(";");
	for (var i = 0; i < cookies.length; i++) {
	  var cookie = cookies[i];
	  while (cookie.charAt(0) == " ") {
		cookie = cookie.substring(1, cookie.length);
	  }
	  if (cookie.indexOf(nameEQ) == 0) {
		return cookie.substring(nameEQ.length, cookie.length);
	  }
	}
	return null;
  }
  
  // Function to hide the cookie banner and set the cookie when the Accept button is clicked
  function acceptCookie() {
	$("#cookie-banner").hide();
	setCookie("cookie-accepted", "true", 365); // Cookie will expire in 365 days
  }
  
  
  