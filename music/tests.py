from django.test import TestCase
from django.urls import reverse # new
from rest_framework import status # new
from rest_framework.test import APITestCase # new
from .models import Track # new
# Create your tests here.

class TrackTestCase(APITestCase):
    def setUpTestTrack(self):
        self.track = Track.objects.create(
            audio_file="../media/songs/GardlyRadicle-_Bad_Dreams_Remix_CxmHLRR.wav",
            title="Test Track",
            artist="Test Artist",
            thumbnail="../media/thumbnails/babypic_cartoon_fPBqzhU.png",
            vinyl_thumbnail="../media/vinyl_thumbnails/vinyl-red.png",
            genres=["Test Genre"],
            duration_seconds=120,
            release_date="2022-01-01",
            creation_date="2022-01-01",
            language="en",
            explicit_content=False,
            tempo_bpm=120,
            key="C Major",
            time_signature="4/4",
            moods=["Uplifting", "Melancholy"],
            keywords_tags=["summer", "driving"],
            instruments=["piano", "drums"],
            vocal_description="Male Lead",
        )

    def testTrackList(self):
        self.setUpTestTrack()
        response = self.client.get("/api/v1/tracks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Track")
        self.assertContains(response, "Test Track")

    def testTrackDetail(self):
        self.setUpTestTrack()
        track_id = self.track.track_id
        response = self.client.get(f'/api/v1/tracks/{track_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Track")
        self.assertEqual(response.data['artist'], "Test Artist")
        self.assertContains(response, "Test Track")
        self.assertContains(response, "Test Artist")
    # def testTrackModel(self):
    #     self.setUpTestTrack()
    #     self.assertEqual(self.track.title, "Test Track")
    #     self.assertEqual(self.track.artist, "Test Artist")
    #     self.assertEqual(self.track.duration_seconds, 120)
    #     self.assertEqual(self.track.release_date, "2022-01-01")
    #     self.assertEqual(self.track.creation_date, "2022-01-01")
    #     self.assertEqual(self.track.language, "en")
    #     self.assertEqual(self.track.explicit_content, False)
    #     self.assertEqual(self.track.tempo_bpm, 120)
    #     self.assertEqual(self.track.key, "C Major")
    #     self.assertEqual(self.track.time_signature, "4/4")
    #     self.assertEqual(self.track.moods, ["Uplifting", "Melancholy"])
    #     self.assertEqual(self.track.keywords_tags, ["summer", "driving"])
    #     self.assertEqual(self.track.instruments, ["piano", "drums"])
    #     self.assertEqual(self.track.vocal_description, "Male Lead")    

    # def test_track_list(self):
    #     self.setUpTestTrack()
    #     response = self.client.get(reverse("track-list"))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 1)
