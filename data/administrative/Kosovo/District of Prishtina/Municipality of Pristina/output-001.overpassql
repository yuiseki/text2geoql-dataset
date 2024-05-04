[out:json][timeout:30000];
area["name:en"="Kosovo"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="Municipality of Pristina"](area.searchArea);
);
out geom;
