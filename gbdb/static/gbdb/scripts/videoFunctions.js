/**
 * Jump video to start of clip
 * @param start_time - start time of clip
 * @return {Boolean}
 */
function setClipTime(start_time)
{
    // Clear menu area
    $('#context_data').empty();
    videojs("observation_session_video").currentTime(start_time);
    return false;
}

/**
 * Change video source - called when events have their own, different videos and we need to change between them
 * when event is clicked
 * @param source - video source
 * @return {Boolean}
 */
function changeVideoSource(source)
{
    // Clear menu area
    $('#context_data').empty();
    videojs("observation_session_video").ready(function() {
        // hide the video UI
        $("#div_video_html5_api").hide();
        // and stop it from playing
        this.pause();
        // assign the targeted videos to the source nodes
        $("video:nth-child(1)").attr("src",source);
        // reset the UI states
        $(".vjs-big-play-button").show();
        $("#observation_session_video").removeClass("vjs-playing").addClass("vjs-paused");
        // load the new sources
        this.load();
        $(".vjs-big-play-button").hide();
        $(".vjs-control-bar").show();
        $("#div_video_html5_api").show();
    });
    return false;
}
