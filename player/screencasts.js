function get_list(index_url) {
    var xmlhttp=new XMLHttpRequest();
	xmlhttp.open("GET",index_url,false);
	xmlhttp.send();
	res = JSON.parse(xmlhttp.responseText);
	return res;
}

function get_metadata(index_url, key) {
    var xmlhttp=new XMLHttpRequest();
	xmlhttp.open("GET",index_url.replace("index.json",key+".json"),false);
	xmlhttp.send();
	res = JSON.parse(xmlhttp.responseText);
	res.key = key;
	res.url_root = index_url.replace("index.json",key+"/");
	return res;
}


//returns {downloads,videoDOM}
//parent must be in the documents DOM tree.
//width, height may be undefined or null.
//if video_js_options is not needed, hand over an empty object.
//if video_ready_callback is not needed, hand over an empty function.
function insert_player(index_url, key, parent, width, height, video_js_options, video_ready_callback) {
    metadata = get_metadata(index_url, key);
    vidID="screencast-"+key;
    var videostr = '<video id="'+vidID+'" class="video-js vjs-default-skin" controls preload="auto" data-setup="{}"';
    if (height != undefined && height!=null) videostr = videostr+' height="'+height+'"';
    if (width != undefined && width!=null) videostr = videostr+' width="'+width+'"';
    videostr = videostr+'></video>'
    var video = $(videostr);
    for (var i=0; i<metadata.tracks.length; i++) {
        track = metadata.tracks[i];
        trackstr = '<track';
        for (prop in track) {
            if (prop=="default") {
                if (track[prop]) trackstr = trackstr+' default';
            } else {
                trackstr = trackstr+' '+prop+'="'+track[prop]+'"';
            }
        }
        trackstr = trackstr+'>';
        trackdom = $(trackstr);
        video.append(trackdom);
    }
    parent.append(video);

    videojs(video, video_js_options, video_ready_callback);

    return {videoDOM:video, downloads:metadata.downloads};
}
