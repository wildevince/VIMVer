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


$(document).ready(function() {

	// var all_td = document.getElementsByTagName('td');

	$("div.sequence span").mouseover(function () {
		let pos = $(this).attr('data-position');
		$("div.sequence span[data-position="+pos+"]").attr('hover', 'true')
	});

	$("div.sequence span").mouseout(function () {
		$("div.sequence span").attr('hover', 'false')
	});
	


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


});