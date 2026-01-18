# TODO List

## Medium Priority  
- [ ] Create the newsletter system
- [ ] also implement the dynamicstem folder build in fetch licenses in the front end in addition to for the email sending

- [ ] add check button in checkout to receive newletter/new beats
- [ ] Put authentication for the backend API access
- [ ] For large stems, consider streaming to the ZIP instead of writestr(f.read()) to avoid memory spikes
- [ ] I need to add this to my nginx for production :jclient_max_body_size 30M;
- [ ] what needs to be memoized/cached in the frontend
- [ ] thinking about analitics in the front end
- [ ] Use react virtualized for better performance for the track library in the front end to make sure only visible tracks (in a few more) are rendered in the viewport
- [ ] increase the height of the MusicContainer to fit more tracks 
- [ ] add a loading spinner or skeleton loader for the track library
- [ ] add analytics to the frontend
- [ ] add license zip urls to the confirmation page


## Low Priority
- [ ] Fix the back to detail button in the front end to not be buggy
- [ ] Think about integratiing open/click tracking in the future
- [ ] change from npm start to vite in the frontend
- [ ] make the music licensing page more engaging
- [ ] Make the stem folder generation for email
- [ ] fix buggy play pause button
- [ ] Change status of newsletter from draft to send when sent
- [ ] add metadata to the track before sending
- [ ] Do I want to get the download url from license app to transaction app or is the way i'm doing it good for now
- [ ] fix all the links to everything...track, licenses....etc
## Bug Fixes
- [ ] Fix the license agreement pdf generation
- [ ] add some frame or banner in the music licensing page 
- [ ] add a donation link and the donation icon in audio player
- [ ] Use transactional email service (SendGrid, Mailgun) for better deliverability
- [ ] fix the scrollbar in order summary to a visible color
- [ ] fix check box duplicate issue in license aknowledge
- [ ] fix trackpricingtable and order summary missing details/info


django-summernote for rich text editor