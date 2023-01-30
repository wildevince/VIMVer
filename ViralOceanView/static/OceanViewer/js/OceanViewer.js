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

	function fileExists(url) {
		if(url){
			var req = new XMLHttpRequest();
			req.open('GET', url, false);
			req.send();
			return req.status==200;
		} else {
			return false;
		}
	}

	$.fn.searchForFigure = function(){
		this.each(function() {
			var filepath = $(this).attr('path');
			if(fileExists(filepath)) {
				$(this).attr("src", filepath);
				$(this).removeAttr("path");
			} else {
				setTimeout( $(this).searchForFigure(),5000);
			}
		})
	}
	// load svg figure on OceanView
	$("#figure_prot_mutation").searchForFigure();
	$("#figure_nucl_mutation").searchForFigure();
	
	
	$(function() {
		$("div.p-row").tooltip({track:true});
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


	


})