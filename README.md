# 10kHours.ru

a site that will show how you spend your time based on data from Google Calendar

### How it works:
1. User creates account on this site and provides access to his Calendar data (through redirects).
2. Site downloads user events into db (you can see models in viz/models.py).
3. User chooses period, calendar and keywords he intrested to visualize.
4. Site shows a couple of graphs about user's time spending in given period of time.

### What'd be nice to have:
- Periodic reports system.

What i mean by that: it's boring to go to the site to get report (for now it's only pictures), so I want to send them by email to users.

- Somehow hide owner of event, calendar. Events are stored in db with user names, so admin can see what everybody is doing - that's not cool.
