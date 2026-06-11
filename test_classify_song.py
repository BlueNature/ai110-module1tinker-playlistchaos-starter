import pytest
from playlist_logic import classify_song

BASE_PROFILE = {
    "hype_min_energy": 7,
    "chill_max_energy": 3,
    "favorite_genre": "rock",
}


def song(title="", genre="", energy=5):
    return {"title": title, "genre": genre, "energy": energy}


# --- energy boundaries ---

def test_energy_at_hype_min_is_hype():
    assert classify_song(song(energy=7), BASE_PROFILE) == "Hype"

def test_energy_just_below_hype_min_is_not_hype():
    assert classify_song(song(energy=6), BASE_PROFILE) == "Mixed"

def test_energy_at_chill_max_is_chill():
    assert classify_song(song(energy=3), BASE_PROFILE) == "Chill"

def test_energy_just_above_chill_max_is_not_chill():
    assert classify_song(song(energy=4), BASE_PROFILE) == "Mixed"

def test_energy_zero_is_chill():
    assert classify_song(song(energy=0), BASE_PROFILE) == "Chill"

def test_negative_energy_is_chill():
    assert classify_song(song(energy=-5), BASE_PROFILE) == "Chill"

def test_energy_well_above_hype_min_is_hype():
    assert classify_song(song(energy=100), BASE_PROFILE) == "Hype"

def test_energy_in_middle_range_is_mixed():
    assert classify_song(song(energy=5), BASE_PROFILE) == "Mixed"


# --- favorite_genre ---

def test_favorite_genre_match_with_low_energy_is_hype():
    # energy=1 would be Chill, but genre match wins
    assert classify_song(song(genre="rock", energy=1), BASE_PROFILE) == "Hype"

def test_favorite_genre_match_with_mid_energy_is_hype():
    assert classify_song(song(genre="rock", energy=5), BASE_PROFILE) == "Hype"

def test_favorite_genre_case_sensitive_no_match():
    # "Rock" != "rock"; also "rock" not in "Rock" so no hype keyword match either
    assert classify_song(song(genre="Rock", energy=1), BASE_PROFILE) == "Chill"

def test_empty_favorite_genre_matches_empty_song_genre():
    # "" == "" → Hype even at low energy
    profile = {**BASE_PROFILE, "favorite_genre": ""}
    assert classify_song(song(genre="", energy=1), profile) == "Hype"

def test_non_matching_genre_does_not_grant_hype():
    assert classify_song(song(genre="jazz", energy=5), BASE_PROFILE) == "Mixed"


# --- hype genre keywords ---

def test_hype_keyword_rock_in_genre():
    assert classify_song(song(genre="indie rock", energy=1), BASE_PROFILE) == "Hype"

def test_hype_keyword_punk_in_genre():
    assert classify_song(song(genre="punk", energy=1), BASE_PROFILE) == "Hype"

def test_hype_keyword_party_in_genre():
    assert classify_song(song(genre="party pop", energy=1), BASE_PROFILE) == "Hype"

def test_hype_keyword_substring_in_genre():
    # "rock" is a substring of "rockabilly"
    assert classify_song(song(genre="rockabilly", energy=1), BASE_PROFILE) == "Hype"

def test_hype_keyword_case_sensitive_no_match():
    # "Rock" does not contain lowercase "rock"
    profile = {**BASE_PROFILE, "favorite_genre": "jazz"}
    assert classify_song(song(genre="Rock", energy=1), profile) == "Chill"


# --- chill title keywords ---

def test_chill_keyword_lofi_in_title():
    assert classify_song(song(title="lofi beats", energy=5), BASE_PROFILE) == "Chill"

def test_chill_keyword_ambient_in_title():
    assert classify_song(song(title="ambient journey", energy=5), BASE_PROFILE) == "Chill"

def test_chill_keyword_sleep_in_title():
    assert classify_song(song(title="sleepytime mix", energy=5), BASE_PROFILE) == "Chill"

def test_chill_keyword_in_genre_does_not_classify_as_chill():
    # chill keywords are only checked in the title
    assert classify_song(song(genre="lofi", energy=5), BASE_PROFILE) == "Mixed"

def test_chill_keyword_case_sensitive_no_match():
    # "Lofi" does not contain lowercase "lofi"
    assert classify_song(song(title="Lofi Beats", energy=5), BASE_PROFILE) == "Mixed"


# --- Hype takes priority over Chill ---

def test_favorite_genre_beats_low_energy():
    assert classify_song(song(genre="rock", energy=0), BASE_PROFILE) == "Hype"

def test_favorite_genre_beats_chill_title_keyword():
    assert classify_song(song(title="ambient mix", genre="rock", energy=1), BASE_PROFILE) == "Hype"

def test_hype_keyword_in_genre_beats_low_energy():
    assert classify_song(song(genre="punk", energy=0), BASE_PROFILE) == "Hype"

def test_hype_min_energy_beats_chill_title_keyword():
    assert classify_song(song(title="lofi beats", energy=7), BASE_PROFILE) == "Hype"

def test_inverted_profile_hype_check_still_runs_first():
    # hype_min=3, chill_max=7: energy=5 satisfies both; Hype wins
    profile = {**BASE_PROFILE, "hype_min_energy": 3, "chill_max_energy": 7, "favorite_genre": "jazz"}
    assert classify_song(song(energy=5), profile) == "Hype"


# --- missing / empty fields ---

def test_empty_song_dict_defaults_to_chill():
    # energy defaults to 0 → 0 <= 3 → Chill
    assert classify_song({}, BASE_PROFILE) == "Chill"

def test_missing_profile_fields_uses_defaults():
    # {} profile → hype_min=7, chill_max=3, favorite_genre=""
    # song genre="" matches favorite_genre="" → Hype
    assert classify_song(song(genre="", energy=1), {}) == "Hype"

def test_high_hype_min_in_profile():
    profile = {**BASE_PROFILE, "hype_min_energy": 11, "favorite_genre": "jazz"}
    # energy=10 < 11, no genre match, no hype keyword → Mixed
    assert classify_song(song(energy=10), profile) == "Mixed"

def test_low_chill_max_in_profile():
    profile = {**BASE_PROFILE, "chill_max_energy": -1, "favorite_genre": "jazz"}
    # energy=0 > -1, no keywords → Mixed
    assert classify_song(song(energy=0), profile) == "Mixed"
