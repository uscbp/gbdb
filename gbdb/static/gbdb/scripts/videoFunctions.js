/**
 * Play a clip from the video
 * @param start_time - clip start time
 * @param end_time - clip end time
 * @return {Boolean}
 */
function playClip(start_time, end_time)
{
    // Jump to start time
    videojs("observation_session_video").currentTime(start_time);
    // Stop video at end of clip
    function stopClip(){
        if(this.currentTime()>=end_time)
        {
            this.off('timeupdate',stopClip);
            this.pause();
        }
    }
    // Check if we need to stop at every time update
    videojs("observation_session_video").on("timeupdate",stopClip);
    // Play clip
    videojs("observation_session_video").play();
    return false;
}

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
        // With flash - have to play the clip for rangeslider to work - play for 0 sec and reset to beginning
        function init(){
            videojs("observation_session_video").on("pause",reset);
            function reset(){
                videojs("observation_session_video").off('pause',reset);
                videojs("observation_session_video").currentTime(0);
            }
            playClip(0,0);
        }
        videojs("observation_session_video").on("loadedmetadata",init);

    });
    return false;
}
