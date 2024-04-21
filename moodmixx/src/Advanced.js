import React, { useState, useMemo, useEffect, useRef } from "react";
import TinderCard from "react-tinder-card";
function Advanced() {
  const [songs, setSongs] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [lastDirection, setLastDirection] = useState();
  const [song, setSong] = useState(null);
  const audioRef = useRef(new Audio());
  const currentIndexRef = useRef(currentIndex);
  const childRefs = useMemo(
    () =>
      Array(songs.length)
        .fill(0)
        .map(() => React.createRef()),
    [songs.length]
  );

  useEffect(() => {
    fetchDaylist();
  }, []);

  useEffect(() => {
    return () => {
      audioRef.current.pause();
    };
  }, []);

  const fetchDaylist = async () => {
    setIsLoading(true);
    try {
      // Adjust the URL to where your backend endpoint for getDaylist is hosted
      const response = await fetch(
        "https://moodmixx-app-30a3f646f185.herokuapp.com/playlistTracks",
        {
          credentials: "include",
          mode: "cors",
        }
      );
      if (!response.ok) throw new Error("Failed to fetch daylist");
      const data = await response.json();
      const thankYouCard = {
        song_name: "Thank You for Playing!",
        album_cover: "https://eecs441soloway.github.io/images/soloway.jpg", // You could specify an image URL for the thank you card background
        album_name: "We hope you enjoyed the experience.",
        artist_names: "- MoodMixx Team",
        isThankYouCard: true, // A flag to identify the thank you card
      };
      setSongs([thankYouCard, ...data.song_info]);
      setCurrentIndex(data.song_info.length);
    } catch (error) {
      console.error("Error fetching daylist:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateCurrentIndex = (val) => {
    setCurrentIndex(val);
    currentIndexRef.current = val;
  };

  const canGoBack = currentIndex < songs.length - 1;

  const canSwipe = currentIndex >= 0;

  // set last direction and decrease current index
  function stop() {
    audioRef.current.pause();
  }

  const swiped = (direction, nameToDelete, index, song_preview, track_id) => {
    setLastDirection(direction);
    updateCurrentIndex(index - 1);
    stop();
    if (direction === "right") {
      // Make a POST request to the server to add track to Spotify library
      fetch("https://moodmixx-app-30a3f646f185.herokuapp.com/addTrack", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ trackId: track_id }),
        credentials: "include", // Include credentials for CORS and sessions
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data); // You can process server response here
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
  };

  const outOfFrame = (name, idx) => {
    console.log(`${name} (${idx}) left the screen!`, currentIndexRef.current);
    // handle the case in which go back is pressed before card goes outOfFrame
    currentIndexRef.current >= idx && childRefs[idx].current.restoreCard();
    // TODO: when quickly swipe and restore multiple times the same card,
    // it happens multiple outOfFrame events are queued and the card disappear
    // during latest swipes. Only the last outOfFrame event should be considered valid
  };

  const swipe = async (dir) => {
    if (canSwipe && currentIndex < songs.length) {
      await childRefs[currentIndex].current.swipe(dir); // Swipe the card!
    }
  };

  // increase current index and show card
  const goBack = async () => {
    if (!canGoBack) return;
    const newIndex = currentIndex + 1;
    updateCurrentIndex(newIndex);
    stop();
    await childRefs[newIndex].current.restoreCard();
  };

  function StartButton({ song_preview }) {
    function start() {
      if (song) {
        song.pause(); // Ensures any currently playing song is stopped
        song.currentTime = 0; // Resets the playback position
      }
      const audio = new Audio(song_preview);
      audio.play();
      setSong(audio);
    }

    return (
      <button className="play-button" onClick={start}>
        Play!
      </button>
    );
  }

  function StopButton() {
    function stop() {
      console.log("song from react:", song);
      song.pause();
      console.log("did this stop");
    }

    return (
      <button className="pause-button" onClick={stop}>
        Pause!
      </button>
    );
  }

  return (
    <div>
      <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=MuseoModerno:ital,wght@0,100..900;1,100..900&display=swap"
        rel="stylesheet"
      />
      <link
        href="https://fonts.googleapis.com/css?family=Alatsi&display=swap"
        rel="stylesheet"
      />
      <h1 className="moodmixx-title">moodmixx</h1>
      <div className="cardContainer">
        {songs.map((song, index) => (
          <div>
            <TinderCard
              ref={childRefs[index]}
              className="swipe"
              key={song.song_name}
              onSwipe={(dir) =>
                swiped(
                  dir,
                  song.song_name,
                  index,
                  song.preview_url,
                  song.track_id
                )
              }
              onCardLeftScreen={() => outOfFrame(song.song_name, index)}
            >
              <div
                style={{ backgroundImage: "url(" + song.album_cover + ")" }}
                className="card"
              >
                <h2>{song.song_name}</h2>
                <p>
                  {song.album_name} <br></br>
                  {song.artist_names}
                </p>
              </div>
              <StartButton song_preview={song.preview_url} />
              {<StopButton />}
            </TinderCard>
          </div>
        ))}
      </div>
      <div className="buttons">
        <button
          style={{ backgroundColor: !canSwipe && "#c3c4d3" }}
          onClick={() => swipe("left")}
        >
          Swipe left!
        </button>
        <button
          style={{ backgroundColor: !canGoBack && "#c3c4d3" }}
          onClick={() => goBack()}
        >
          Undo swipe!
        </button>
        <button
          style={{ backgroundColor: !canSwipe && "#c3c4d3" }}
          onClick={() => swipe("right")}
        >
          Swipe right!
        </button>
      </div>
      {lastDirection ? (
        <h2 key={lastDirection} className="infoText">
          You swiped {lastDirection}
        </h2>
      ) : (
        <h2 className="infoText">Swipe a card to get started!</h2>
      )}
    </div>
  );
}

export default Advanced;
